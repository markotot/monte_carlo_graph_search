class ClustersNovelty:
    def __init__(self, config):
        self.total_data_points = 0
        self.threshold = config.novelty_threshold

    def calculate_novelty(self, observation):
        return 0

    def check_if_novel(self, feature_value, feature_name):
        return 0

    def pseudo_count_novelty_function(self, observation):
        return 0

    def update_posterior(self, observation, done, nodes, move, forward_model_calls):

        self.total_data_points += 1
        return 0

    def get_discovered_subgoals(self):
        return {}

    def discover_subgoal(self, subgoal_name, nodes, move, forward_model_calls):
        pass

    def get_subgoal_metrics(self):
        return {}
