import copy
import time

import numpy as np

from monte_carlo_graph_search.core.edge import Edge
from monte_carlo_graph_search.core.graph import Graph
from monte_carlo_graph_search.core.node import Node
from monte_carlo_graph_search.core.novelty import Novelty
from monte_carlo_graph_search.utils import utils


class MCGSAgent:
    def __init__(self, env, logger, config):

        self.config = config
        self.random = np.random.RandomState(self.config.search.seed)

        self.env = env
        self.logger = logger
        self.graph = Graph(seed=self.config.search.seed, config=config)
        self.novelty = Novelty(config=config)

        # statistic counters, maybe move into another class
        self.edge_counter = 0
        self.move_counter = 0
        self.num_simulations = 0  # One simulation has  N rollouts (N = number of children)

        observation = self.env.get_observation()
        self.root_node = Node(
            id=observation,
            parent=None,
            is_leaf=True,
            done=False,
            action=None,
            reward=0,
            visits=0,
            novelty_value=self.novelty.calculate_novelty(observation),
            config=config,
        )
        self.root_node.chosen = True

        self.graph.add_node(self.root_node)
        self.novelty.update_posterior(
            self.root_node.id,
            self.root_node.done,
            self.graph.get_number_of_nodes(),
            self.move_counter,
            self.env.forward_model_calls,
        )

    def plan(self) -> int:

        start_time = time.perf_counter()

        self.move_counter += 1
        aggregated_metrics = {}

        # Graph Maintenance
        maintenance_metrics = self.maintain_graph()
        aggregated_metrics.update(maintenance_metrics)

        remaining_budget = self.config.search.budget_per_move
        iterations = 0

        while remaining_budget > 0:

            # Selection
            selection_env = copy.deepcopy(self.env)
            node, selection_budget, selection_metrics = self.selection(selection_env)
            utils.update_metrics(aggregated_metrics, selection_metrics)

            # Expansion - This could be modified to allow single child expansion
            if node is None:
                children, actions_to_children = [self.root_node], [6]
            else:
                children, actions_to_children, expansion_budget, expansion_metrics = self.expansion(node, selection_env)
                utils.update_metrics(aggregated_metrics, expansion_metrics)

            # Rollouts
            total_simulation_budget = 0
            for idx in range(len(children)):
                child_average_reward, trajectories, single_simulation_budget, simulation_metrics = self.simulation(
                    actions_to_children[idx], selection_env
                )
                total_simulation_budget += single_simulation_budget
                utils.update_metrics(aggregated_metrics, simulation_metrics)

                # Storing rollouts
                if self.config.stored_rollouts.use_stored_rollouts:
                    rollout_nodes, rewards, storing_nodes_metrics = self.add_novelties_to_graph(trajectories)
                    utils.update_metrics(aggregated_metrics, storing_nodes_metrics)

                # Backpropagation
                if self.config.use_backpropagation:
                    start_backprop_time = time.perf_counter()
                    if self.config.stored_rollouts.use_stored_rollouts:
                        for i, node in enumerate(rollout_nodes):
                            self.backpropagation(node, rewards[i])
                    self.backpropagation(children[idx], child_average_reward)
                    end_backprop_time = time.perf_counter()
                    backprop_metrics = {"backpropagation_time": (end_backprop_time - start_backprop_time)}
                    utils.update_metrics(aggregated_metrics, backprop_metrics)

            iteration_budget = selection_budget + expansion_budget + total_simulation_budget
            remaining_budget -= iteration_budget

            iteration_metrics = {"iteration_spent_budget": iteration_budget}
            utils.update_metrics(aggregated_metrics, iteration_metrics)
            iterations += 1

        # Select Move
        best_node, action, select_best_move_metrics = self.select_best_move(self.root_node, closest=True)
        aggregated_metrics.update(select_best_move_metrics)

        end_time = time.perf_counter()
        time_per_move = end_time - start_time

        subgoals = self.novelty.get_discovered_subgoals()

        aggregated_metrics.update(self.graph.get_metrics())
        aggregated_metrics.update(
            moves=self.move_counter,
            total_fmc=self.env.forward_model_calls,
            total_num_simulations=self.num_simulations,
            iterations_per_move=iterations,
            time_per_move=time_per_move,
            key_discovered=int(subgoals["key_discovered"]),
            door_discovered=int(subgoals["door_discovered"]),
            goal_discovered=int(subgoals["goal_discovered"]),
        )

        aggregated_metrics = utils.dict_sum(aggregated_metrics)
        aggregated_metrics = utils.add_time_percentages(aggregated_metrics, time_per_move)

        self.logger.write(aggregated_metrics, self.move_counter)

        return action

    def act(self, action):
        return self.env.stochastic_step(action, self.random.random_sample())

    def selection(self, env):

        start_time = time.perf_counter()
        if self.root_node.is_leaf:
            return self.root_node, 0, {}

        node = self.graph.select_frontier_node(
            noisy=self.config.selection.use_noisy_frontier_selection,
            novelty_factor=self.config.novelty.novelty_factor * int(self.config.novelty.use_novelty_detection),
        )

        if node is None:  # If no frontier node was found, select the root node
            return self.root_node, 0, {}

        selected_node, spent_budget = self.go_to_node(node, env)

        end_time = time.perf_counter()
        metrics = {
            "selection_time": (end_time - start_time),
            "selection_spent_budget": spent_budget,
        }
        return selected_node, spent_budget, metrics

    def expansion(self, node, env):

        start_time = time.perf_counter()
        if node.done:
            return [], []

        new_nodes = []
        actions_to_new_nodes = []

        spent_budget = 0
        if (
            node.is_leaf
        ):  # Nodes might not be leaves if the environment is fully stochastic, and the selection phase gets complicated
            node.is_leaf = False
            self.graph.remove_from_frontier(node)

        for action in range(self.env.action_space.n):

            expansion_env = copy.deepcopy(env)
            state, reward, done, info = expansion_env.step(action)
            # Do we need it here, since it's already tracked in custom_minigrid_env.py -> step() # Maybe we don't ne
            spent_budget += 1
            current_observation = expansion_env.get_observation()
            child, reward = self.add_new_observation(current_observation, node, action, reward, done)
            if child is not None:
                new_nodes.append(child)
                actions_to_new_nodes.append(action)

        end_time = time.perf_counter()
        metrics = {
            "expansion_time": (end_time - start_time),
            "expansion_spent_budget": spent_budget,
        }
        return new_nodes, actions_to_new_nodes, spent_budget, metrics

    def simulation(self, action_to_node, env):

        start_time = time.perf_counter()

        rewards = []
        trajectories = []
        spent_budget_simulation = 0

        for i in range(self.config.search.num_rollouts):

            allowed_actions = range(self.env.action_space.n)
            if self.config.use_disabled_actions:
                action_to_remove = i % self.env.action_space.n
                allowed_actions.remove(action_to_remove)

            action_list = self.random.choice(allowed_actions, self.config.search.rollout_depth)
            action_failure_probabilities = self.random.random_sample(self.config.search.rollout_depth + 1)

            average_reward, trajectory, spent_budget = self.rollout(
                action_to_node, env, action_list, action_failure_probabilities
            )
            trajectories.append(trajectory)
            rewards.append(average_reward)
            spent_budget_simulation += spent_budget

        self.num_simulations += 1

        end_time = time.perf_counter()

        metrics = {
            "simulation_time": (end_time - start_time),
            "simulation_spent_budget": spent_budget_simulation,
            "average_reward": np.mean(average_reward),
        }

        return np.mean(rewards), trajectories, spent_budget_simulation, metrics

    def backpropagation(
        self, node, reward
    ):  # This is the simple version when only the optimal path to the root is updated
        i = 1  # discount factor
        while node is not None:
            node.visits += 1
            node.total_value += reward * np.power(self.config.search.discount_factor, i)
            node = node.parent
            i += 1

    def rollout(self, action_to_node, env, action_list, action_failure_probabilities):

        path = []
        spent_budget = 0
        cumulative_reward = 0

        rollout_env = copy.deepcopy(env)
        rollout_env.stochastic_step(action_to_node, action_failure_probabilities[0])
        spent_budget += 1

        previous_observation = rollout_env.get_observation()
        for idx, action in enumerate(action_list):

            state, reward, done, info = rollout_env.stochastic_step(action, action_failure_probabilities[idx + 1])
            observation = rollout_env.get_observation()
            spent_budget += 1

            cumulative_reward += reward
            path.append((previous_observation, observation, action, reward, done))
            previous_observation = observation
            if done:
                break

        return cumulative_reward, path, spent_budget

    def add_new_observation(self, current_observation, parent_node, action, reward, done):

        new_node = None

        if current_observation != parent_node.id:  # Don't add the node if nothing has changed in the observation
            if not self.graph.has_node(
                current_observation
            ):  # If the node is not in the graph, create it and add it to the graph

                child = Node(
                    id=current_observation,
                    parent=parent_node,
                    is_leaf=True,
                    done=done,
                    action=action,
                    reward=reward,
                    visits=0,
                    novelty_value=self.novelty.calculate_novelty(current_observation),
                    config=self.config,
                )
                self.graph.add_node(child)
                self.novelty.update_posterior(
                    child.id,
                    child.done,
                    self.graph.get_number_of_nodes(),
                    self.move_counter,
                    self.env.forward_model_calls,
                )
                new_node = child
            else:
                # enable for FMC optimisation, comment for full exploration
                child = self.graph.get_node_info(current_observation)  # TODO: why is this here?
                if child.is_leaf:
                    new_node = child

            _ = self.add_edge(parent_node, child, action, reward, done)

        return new_node, reward

    def add_novelties_to_graph(self, trajectories):
        # TODO: rework this logic

        start_time = time.perf_counter()
        nodes = []
        node_rewards = []
        novel_nodes_added = 0
        for trajectory in trajectories:
            for idx, step in enumerate(trajectory):

                observation = step[1]
                novelty = self.novelty.calculate_novelty(observation)
                if (not self.graph.has_node(observation)) and (
                    novelty > 0 or self.config.stored_rollouts.only_store_novel_nodes is False
                ):

                    for i in range(idx + 1):
                        transition = trajectory[i]
                        previous_obs = transition[0]
                        current_obs = transition[1]
                        action = transition[2]
                        reward = transition[3]
                        done = transition[4]

                        parent_node = self.graph.get_node_info(previous_obs)
                        node, node_reward = self.add_new_observation(current_obs, parent_node, action, reward, done)
                        nodes.append(node)
                        node_rewards.append(node_reward)
                    if node.novelty_value >= 1:
                        novel_nodes_added += 1

        end_time = time.perf_counter()
        metrics = {
            "storing_nodes_time": (end_time - start_time),
            "novel_nodes_added": novel_nodes_added,
        }
        return nodes, node_rewards, metrics

    def maintain_graph(self):
        start_time = time.perf_counter()
        self.set_root_node()
        self.graph.reroute_all()
        end_time = time.perf_counter()
        maintenance_metrics = {"maintenance_time": (end_time - start_time)}
        return maintenance_metrics

    def go_to_node(self, destination_node, env):

        observation = env.get_observation()
        node = self.graph.get_node_info(observation)
        spent_budget = 0

        reached_destination = False
        while self.graph.has_path(node, destination_node) and not reached_destination:
            observations, actions = self.graph.get_path(node, destination_node)
            for idx, action in enumerate(actions):  # For each action in the path, do one step in the environment
                previous_observation = env.get_observation()
                parent_node = self.graph.get_node_info(previous_observation)

                state, reward, done, info = env.step(action)
                spent_budget += 1

                current_observation = env.get_observation()
                # If we get a new observation (can happen in fully stochastic envs)
                if not self.graph.has_node(current_observation):
                    self.add_new_observation(current_observation, parent_node, action, reward, done)  # TODO:

                elif not self.graph.has_edge_by_nodes(parent_node, self.graph.get_node_info(current_observation)):
                    self.add_edge(
                        parent_node=parent_node,
                        child_node=self.graph.get_node_info(current_observation),
                        action=action,
                        reward=reward,
                        done=done,
                    )

                if observations[idx + 1] != current_observation:
                    node = self.graph.get_node_info(current_observation)
                    break

                if destination_node.id == current_observation:
                    reached_destination = True
                    break

        return self.graph.get_node_info(current_observation), spent_budget

    def add_edge(self, parent_node, child_node, action, reward, done):

        edge = Edge(
            id=self.edge_counter,
            node_from=parent_node,
            node_to=child_node,
            action=action,
            reward=reward,
            done=done,
        )

        if not self.graph.has_edge(edge):
            self.graph.add_edge(edge)
            self.edge_counter += 1

        # If child was unreachable make it reachable again and update its parent
        if child_node.unreachable is True and child_node != self.root_node:
            child_node.set_parent(parent_node)
            child_node.actions = action
            child_node.unreachable = False

        return edge

    def set_root_node(self):

        self.graph.clear_new_nodes()

        # Record the old root node
        old_root_node = self.root_node
        new_root_id = self.env.get_observation()
        self.root_node = self.graph.get_node_info(new_root_id)
        self.graph.set_root_node(self.root_node)

        # Set new root node as chosen
        self.root_node.chosen = True
        self.root_node.parent = None

        # If we changed root, reroute old root to new route
        if self.root_node.id != old_root_node.id:
            if self.graph.has_path(self.root_node, old_root_node):
                self.graph.reroute_path(self.root_node, old_root_node)
                old_root_node.action = self.graph.get_edge_info(old_root_node.parent, old_root_node).action

    def select_best_move(self, node, closest=False):

        start_time = time.perf_counter()
        if closest:  # find the closest done node
            best_node = self.graph.get_closest_done_node(only_reachable=True)

        if best_node is None:  # find the node with the highest reward + [novelty]
            best_node = self.graph.get_best_node(only_reachable=True)

        if best_node is None:  # if there is no reachable node, use root (6 - no action)
            return self.root_node, 6

        if best_node.done is True:
            pass
            # Log metrics that the goal has been found

        while best_node.parent != self.root_node:  # get to the first child of root
            best_node = best_node.parent

        edge = self.graph.get_edge_info(node, best_node)
        end_time = time.perf_counter()

        metrics = {"select_move_time": (end_time - start_time)}
        return best_node, edge.action, metrics

    def get_final_metrics(self, done):

        metrics = {
            "total_moves": self.move_counter,
            "game_finished": done,
        }
        subgoal_metrics = self.novelty.get_subgoal_metrics()
        metrics.update(subgoal_metrics)
        return metrics
