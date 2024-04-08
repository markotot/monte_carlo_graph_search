import os
import pickle

import neptune
import networkx as nx
import numpy as np


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


def analyse_graph_metrics(graph):

    total_nodes = len(graph.nodes)
    total_edges = len(graph.edges)

    number_of_children = []
    num_visits = []

    terminated_nodes = []

    expanded_nodes = []
    number_of_expanded_nodes_children = []

    reversible_nodes = []
    cycle_lengths = []

    clustering_coefficients = []

    nodes_info = list(nx.get_node_attributes(graph, "info").values())
    for node_info in nodes_info:

        children = graph.successors(node_info.observation)
        num_children = len(list(children))
        number_of_children.append(num_children)

        terminated_nodes.append(node_info.terminated)
        expanded_nodes.append(node_info.is_leaf)

        # Count expanded nodes
        if node_info.is_leaf is False:
            number_of_expanded_nodes_children.append(num_children)

        # Count reversibility and cycle length
        cycle_length = get_cycle_length(graph, node_info)
        reversible_nodes.append(cycle_length > 0)
        cycle_lengths.append(cycle_length)

        num_visits.append(node_info.visits)
        clustering_coefficients.append(nx.clustering(graph, node_info.observation))

    mean_total_visits = np.sum(np.mean(num_visits))
    num_terminated_nodes = np.sum(np.array(terminated_nodes, dtype=bool))
    num_expanded_nodes = np.sum(np.array(expanded_nodes, dtype=bool))
    mean_expanded_nodes_children = np.mean(number_of_expanded_nodes_children)
    mean_children = np.mean(number_of_children)
    mean_visits = np.mean(num_visits)
    mean_cycle_length = np.mean(cycle_lengths)
    num_reversible_nodes = np.sum(np.array(reversible_nodes, dtype=bool))
    num_irreversible_nodes = total_nodes - num_reversible_nodes
    reversibility_percentage = num_reversible_nodes / total_nodes

    mean_clustering_coefficient = np.mean(clustering_coefficients)

    # Communities
    # https://networkx.org/documentation/stable/reference/algorithms/community.html

    metrics = {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "num_terminated_nodes": num_terminated_nodes,
        "num_expanded_nodes": num_expanded_nodes,
        "mean_children": mean_children,
        "mean_expanded_nodes_children": mean_expanded_nodes_children,
        "mean_visits": mean_visits,
        "total_visits": mean_total_visits,
        "mean_clustering_coefficient": mean_clustering_coefficient,
        "num_reversible_nodes": num_reversible_nodes,
        "num_irreversible_nodes": num_irreversible_nodes,
        "reversibility_percentage": reversibility_percentage,
        "cycle_length": mean_cycle_length,
    }

    for key, value in metrics.items():
        print(f"{key}: {value}")
    return metrics


if __name__ == "__main__":

    nums = range(5946, 5947)

    run_ids = []
    for num in nums:
        run_ids.append(f"MCGS-{num}")

    graphs = []
    for run_id in run_ids:
        env_type, env_seed, agent_seed, graph, config = load_run("markotot/MCGS", f"{run_id}")
        graphs.append(graph)

    for graph in graphs:
        graph_metrics = analyse_graph_metrics(graph)
