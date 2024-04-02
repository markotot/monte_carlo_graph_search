class MinigridNovelty:
    def __init__(self, config):
        self.total_data_points = 0
        self.threshold = config.novelty_threshold

        self.novelty_features = {
            "x_pos": {},
            "y_pos": {},
            "rotation": {},
            "carry": {},
            "door_open": {},
            "door_locked": {},
        }

        # Discovered, Nodes, Moves, FMC
        self.subgoals = {
            "key": {
                "discovered": False,
                "nodes": -1,
                "moves": -1,
                "forward_model_calls": -1,
            },
            "door": {
                "discovered": False,
                "nodes": -1,
                "moves": -1,
                "forward_model_calls": -1,
            },
            "goal": {
                "discovered": False,
                "nodes": -1,
                "moves": -1,
                "forward_model_calls": -1,
            },
        }

    def calculate_novelty(self, observation):
        return self.pseudo_count_novelty_function(observation)

    def check_if_novel(self, feature_value, feature_name):

        if feature_value not in self.novelty_features[feature_name]:
            return 1
        else:
            feature_value_count = self.novelty_features[feature_name][feature_value]
            num_feature_keys = len(self.novelty_features[feature_name].keys())
            feature_value_threshold = feature_value_count * num_feature_keys / self.total_data_points
            return int(feature_value_threshold < self.threshold)

    def pseudo_count_novelty_function(self, observation):

        novelty_value = 0
        x_pos, y_pos, rot, carry, door_open, door_locked = observation[:6]

        novelty_value += self.check_if_novel(x_pos, "x_pos")
        novelty_value += self.check_if_novel(y_pos, "y_pos")
        novelty_value += self.check_if_novel(rot, "rotation")
        novelty_value += self.check_if_novel(carry, "carry")
        novelty_value += self.check_if_novel(door_open, "door_open")
        novelty_value += self.check_if_novel(door_locked, "door_locked")

        return novelty_value

    def update_posterior(self, observation, terminated, nodes, move, forward_model_calls):

        x_pos, y_pos, rot, carry, opened, locked = observation[:6]

        if x_pos in self.novelty_features["x_pos"]:
            self.novelty_features["x_pos"][x_pos] += 1
        else:
            self.novelty_features["x_pos"][x_pos] = 1

        if y_pos in self.novelty_features["y_pos"]:
            self.novelty_features["y_pos"][y_pos] += 1
        else:
            self.novelty_features["y_pos"][y_pos] = 1

        if rot in self.novelty_features["rotation"]:
            self.novelty_features["rotation"][rot] += 1
        else:
            self.novelty_features["rotation"][rot] = 1

        if carry in self.novelty_features["carry"]:
            self.novelty_features["carry"][carry] += 1
        else:
            self.novelty_features["carry"][carry] = 1

        if opened in self.novelty_features["door_open"]:
            self.novelty_features["door_open"][opened] += 1
        else:
            self.novelty_features["door_open"][opened] = 1

        if locked in self.novelty_features["door_locked"]:
            self.novelty_features["door_locked"][locked] += 1
        else:
            self.novelty_features["door_locked"][locked] = 1

        if carry == "key":
            self.discover_subgoal("key", nodes, move, forward_model_calls)
        if opened is True:
            self.discover_subgoal("door", nodes, move, forward_model_calls)
        if terminated is True:
            self.discover_subgoal("goal", nodes, move, forward_model_calls)

        self.total_data_points += 1

    def get_discovered_subgoals(self):

        subgoals = {
            "key_discovered": self.subgoals["key"]["discovered"],
            "door_discovered": self.subgoals["door"]["discovered"],
            "goal_discovered": self.subgoals["goal"]["discovered"],
        }

        return subgoals

    def discover_subgoal(self, subgoal_name, nodes, move, forward_model_calls):
        if self.subgoals[subgoal_name]["discovered"] is False:
            self.subgoals[subgoal_name]["discovered"] = True
            self.subgoals[subgoal_name]["nodes"] = nodes
            self.subgoals[subgoal_name]["moves"] = move
            self.subgoals[subgoal_name]["forward_model_calls"] = forward_model_calls

    def get_subgoal_metrics(self):
        metrics = {}
        for subgoal_key, subgoal_value in self.subgoals.items():
            for key, value in subgoal_value.items():
                if "discovered" not in key:
                    metrics[f"subgoal_{subgoal_key}_{key}"] = value
        return metrics
