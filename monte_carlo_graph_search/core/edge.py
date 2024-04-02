class Edge:
    def __init__(self, edge_id, node_from, node_to, action, reward, terminated, truncated):
        self.id = edge_id
        self.node_from = node_from
        self.node_to = node_to
        self.action = action
        self.reward = reward
        self.terminated = terminated
        self.truncated = truncated

    def __hash__(self):
        return hash(self.id)
