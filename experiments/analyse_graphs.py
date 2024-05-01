import os
import pickle

import hydra
import neptune
import networkx as nx
import numpy as np
import pandas as pd
from omegaconf import DictConfig

from monte_carlo_graph_search.core.logger import NeptuneLogger


def load_run(project_id, run_id):

    run = neptune.init_run(project=project_id, with_id=run_id, mode="read-only")
    env_type = run["config/env/type"].fetch()
    env_seed = run["config/env/seed"].fetch()
    agent_seed = run["config/search/seed"].fetch()

    config = run["config"].fetch()

    run[f"graph/{env_type}/{env_seed}_{agent_seed}"].download()  # download to current working directory

    # Load the graph
    file_name = f"{env_seed}_{agent_seed}.pkl"
    with open(file_name, "rb") as f:
        graph = pickle.load(f)
    os.remove(file_name)

    run.stop()

    return env_type, env_seed, agent_seed, graph, config


def get_cycle_length(graph, node_info):

    try:
        cycle = nx.find_cycle(graph, node_info.observation, orientation="original")
        cycle_length = len(cycle)
    except nx.exception.NetworkXNoCycle:
        cycle_length = 0

    return cycle_length


def analyse_graph_metrics(graph, num_actions):

    total_nodes = len(graph.nodes)
    total_edges = len(graph.edges)

    graph_metrics = {
        "num_total_nodes": total_nodes,
        "num_total_edges": total_edges,
        "terminated_nodes": [],
        "expanded_nodes": [],
        "children_per_node": [],
        "expanded_children_per_node": [],
        "visits_per_node": [],
        "clustering_coefficient": [],
        "reversible_nodes": [],
        "irreversible_nodes": [],
        "reversibility_percentage": None,
        "cycle_length": [],
    }

    action_metrics = {}
    for i in range(num_actions):
        action_metrics[i] = {
            "rewards": [],
            "children": [],
            "expanded_node_children": [],
            "times_selected": 0,
            # TODO: Calcualte p_t_selected_best how many times this action is prefered to other action
            #  i.e. there are multiple parents but this action was the best one,
            "percentage_of_times_selected_as_best_action": 0,
        }

    nodes_info = list(nx.get_node_attributes(graph, "info").values())

    for node_info in nodes_info:

        children = graph.successors(node_info.observation)
        num_children = len(list(children))

        graph_metrics["children_per_node"].append(num_children)

        action_metrics[node_info.action]["times_selected"] += 1
        if node_info.parent is not None and node_info.parent != -1:
            edge_info = graph.get_edge_data(node_info.parent.observation, node_info.observation)["info"]
            action_metrics[node_info.action]["rewards"].append(edge_info.reward)
        action_metrics[node_info.action]["children"].append(num_children)

        graph_metrics["terminated_nodes"].append(node_info.terminated)
        graph_metrics["expanded_nodes"].append(node_info.is_leaf)

        # Count expanded nodes
        if node_info.is_leaf is False:
            graph_metrics["expanded_children_per_node"].append(num_children)
            action_metrics[node_info.action]["expanded_node_children"].append(num_children)

        # Count reversibility and cycle length
        cycle_length = get_cycle_length(graph, node_info)
        graph_metrics["cycle_length"].append(cycle_length)
        graph_metrics["reversible_nodes"].append(cycle_length > 0)
        graph_metrics["irreversible_nodes"].append(cycle_length == 0)
        graph_metrics["visits_per_node"].append(node_info.visits)
        graph_metrics["clustering_coefficient"].append(nx.clustering(graph, node_info.observation))

    # Calculate aggregate graph metrics
    # Communities
    # https://networkx.org/documentation/stable/reference/algorithms/community.html
    reversibility_percentage = (
        np.sum(np.array(graph_metrics["reversible_nodes"], dtype=bool)) / graph_metrics["num_total_nodes"]
    )
    aggregate_graph_metrics = {
        "total_nodes": graph_metrics["num_total_nodes"],
        "total_edges": graph_metrics["num_total_edges"],
        "num_terminated_nodes": np.sum(np.array(graph_metrics["terminated_nodes"], dtype=bool)),
        "num_expanded_nodes": np.sum(np.array(graph_metrics["expanded_nodes"], dtype=bool)),
        "mean_children": np.mean(graph_metrics["children_per_node"]),
        "std_children": np.std(graph_metrics["children_per_node"]),
        "max_children": np.max(graph_metrics["children_per_node"]),
        "min_children": np.min(graph_metrics["children_per_node"]),
        "mean_visits_per_node": np.mean(graph_metrics["visits_per_node"]),
        "std_visits_per_node": np.std(graph_metrics["visits_per_node"]),
        "max_visits_per_node": np.max(graph_metrics["visits_per_node"]),
        "min_visits_per_node": np.min(graph_metrics["visits_per_node"]),
        "clustering_coefficient": np.mean(graph_metrics["clustering_coefficient"]),
        "reversible_nodes": np.sum(np.array(graph_metrics["reversible_nodes"], dtype=bool)),
        "irreversible_nodes": np.sum(np.array(graph_metrics["irreversible_nodes"], dtype=bool)),
        "reversibility_percentage": reversibility_percentage,
        "cycle_length": np.mean(graph_metrics["cycle_length"]),
        "std_cycle_length": np.std(graph_metrics["cycle_length"]),
        "max_cycle_length": np.max(graph_metrics["cycle_length"]),
        "min_cycle_length": np.min(graph_metrics["cycle_length"]),
    }

    # Calculate aggregated action metrics
    aggregated_action_metrics = {}
    for action_id, metrics in action_metrics.items():
        if metrics["times_selected"] != 0:
            aggregated_action_metrics[action_id] = {
                "mean_reward": np.mean(metrics["rewards"]),
                "std_reward": np.std(metrics["rewards"]),
                "max_reward": np.max(metrics["rewards"]),
                "min_reward": np.min(metrics["rewards"]),
                "mean_children": np.mean(metrics["children"]),
                "std_children": np.std(metrics["children"]),
                "max_children": np.max(metrics["children"]),
                "min_children": np.min(metrics["children"]),
                "mean_expanded_node_children": np.mean(metrics["expanded_node_children"]),
                "std_expanded_node_children": np.std(metrics["expanded_node_children"]),
                "max_expanded_node_children": np.max(metrics["expanded_node_children"]),
                "min_expanded_node_children": np.min(metrics["expanded_node_children"]),
                "times_selected": metrics["times_selected"],
                "percentage_of_times_selected_as_best_action": 0,
            }
        else:
            aggregated_action_metrics[action_id] = {
                "mean_reward": None,
                "std_reward": None,
                "max_reward": None,
                "min_reward": None,
                "mean_children": None,
                "std_children": None,
                "max_children": None,
                "min_children": None,
                "mean_expanded_node_children": None,
                "std_expanded_node_children": None,
                "max_expanded_node_children": None,
                "min_expanded_node_children": None,
                "times_selected": 0,
                "percentage_of_times_selected_as_best_action": None,
            }

    aggregated_action_metrics_pd = pd.DataFrame.from_dict(aggregated_action_metrics, orient="index")
    aggregate_graph_metrics_pd = pd.DataFrame.from_dict(aggregate_graph_metrics, orient="index")

    return aggregate_graph_metrics_pd, aggregated_action_metrics_pd


@hydra.main(version_base=None, config_path="configs", config_name="aggregate_data")
def run_analysis(config: DictConfig) -> None:

    num_actions = 6
    nums = [5950]

    run_ids = []
    for num in nums:
        run_ids.append(f"MCGS-{num}")

    graphs = []
    for run_id in run_ids:
        env_type, env_seed, agent_seed, graph, run_config = load_run("markotot/MCGS", f"{run_id}")
        graphs.append(graph)

    for graph in graphs:
        graph_metrics, action_metrics = analyse_graph_metrics(graph, num_actions=num_actions)

    logger = NeptuneLogger(config=config, name="GraphAnalysis")

    logger.upload_data_frame(output_path="metrics/graph_metrics", data_frame=graph_metrics)
    logger.upload_data_frame(output_path="metrics/action_metrics", data_frame=action_metrics)
    logger.close()


if __name__ == "__main__":
    run_analysis()
