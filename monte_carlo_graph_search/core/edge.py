class Edge:
    def __init__(self, id, node_from, node_to, action, reward, done):
        self.id = id
        self.node_from = node_from
        self.node_to = node_to
        self.action = action
        self.reward = reward
        self.done = done

    def __hash__(self):
        return hash(self.id)
