class Node:
    def __init__(self, id, parent, is_leaf, action, reward, done, visits, novelty_value, config):

        self.id = id
        self.parent = parent
        self.is_leaf = is_leaf
        self.action = action
        self.total_value = reward
        self.done = done
        self.visits = visits

        self.novelty_value = novelty_value
        if parent is not None:
            self.novelty_value += self.parent.novelty_value * config.novelty.inherit_novelty_factor

        self.chosen = False
        self.unreachable = False

    def uct_value(self):
        # c = 0.0
        ucb = 0  # c * sqrt(log(self.parent.visits + 1) / self.visits)
        return self.value() + ucb

    def value(self):
        if self.visits == 0:
            return 0
        else:
            return self.total_value / self.visits

    def trajectory_from_root(self):

        action_trajectory = []
        current_node = self

        while current_node.parent is not None:
            action_trajectory.insert(0, current_node.action)
            current_node = current_node.parent

        return action_trajectory

    def reroute(self, path, actions):
        parent_order = list(reversed(path))
        actions_order = list(reversed(actions))
        node = self

        for i in range(len(parent_order) - 1):

            if node.parent != parent_order[i + 1]:
                node.set_parent(parent_order[i + 1])
            node.action = actions_order[i]
            node = parent_order[i + 1]

    def set_parent(self, parent):
        self.parent = parent

    def __hash__(self):
        return hash(self.id)
