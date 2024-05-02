import hydra
import networkx as nx
import numpy as np
import pandas as pd
from omegaconf import DictConfig

from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.utils.data_analysis import load_run

#
# def load_run(project_id, run_id):
#
#     run = neptune.init_run(project=project_id, with_id=run_id, mode="read-only")
#     env_type = run["config/env/type"].fetch()
#     env_seed = run["config/env/seed"].fetch()
#     agent_seed = run["config/search/seed"].fetch()
#
#     config = run["config"].fetch()
#
#     run[f"graph/{env_type}/{env_seed}_{agent_seed}"].download()  # download to current working directory
#
#     # Load the graph
#     file_name = f"{env_seed}_{agent_seed}.pkl"
#     with open(file_name, "rb") as f:
#         graph = pickle.load(f)
#     os.remove(file_name)
#
#     run.stop()
#
#     return env_type, env_seed, agent_seed, graph, config


def get_cycle_length(graph, node_info):

    try:
        cycle = nx.find_cycle(graph, node_info.observation, orientation="original")
        cycle_length = len(cycle)
    except nx.exception.NetworkXNoCycle:
        cycle_length = np.NAN

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
        "expanded_node_children": [],
        "visits_per_node": [],
        "clustering_coefficient": [],
        "reversible_nodes": [],
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
            "reversible_nodes": [],
            "cycle_length": [],
        }

    nodes_info = list(nx.get_node_attributes(graph, "info").values())

    solved_paths = []
    start_node = None
    for node_info in nodes_info:
        if node_info.start_node is True:
            start_node = node_info

    for node_info in nodes_info:

        children = graph.successors(node_info.observation)
        num_children = len(list(children))

        graph_metrics["children_per_node"].append(num_children)

        action_metrics[node_info.action]["times_selected"] += 1

        has_parent = node_info.parent is not None and node_info.parent != -1
        if has_parent:
            edge_info = graph.get_edge_data(node_info.parent.observation, node_info.observation)["info"]
            action_metrics[node_info.action]["rewards"].append(edge_info.reward)
        else:
            in_edges = graph.in_edges(node_info.observation, data=True)
            for edge in in_edges:
                edge_info = edge[2]["info"]
                if edge_info.action == node_info.action:
                    action_metrics[node_info.action]["rewards"].append(edge_info.reward)
        action_metrics[node_info.action]["children"].append(num_children)

        graph_metrics["terminated_nodes"].append(node_info.terminated)
        graph_metrics["expanded_nodes"].append(node_info.is_leaf)

        # Count expanded nodes
        if node_info.is_leaf is False:
            graph_metrics["expanded_node_children"].append(num_children)
            action_metrics[node_info.action]["expanded_node_children"].append(num_children)

        # Count reversibility and cycle length
        cycle_length = get_cycle_length(graph, node_info)
        graph_metrics["cycle_length"].append(cycle_length)
        graph_metrics["reversible_nodes"].append(cycle_length > 0)
        graph_metrics["visits_per_node"].append(node_info.visits)
        graph_metrics["clustering_coefficient"].append(nx.clustering(graph, node_info.observation))

        action_metrics[node_info.action]["cycle_length"].append(cycle_length)
        action_metrics[node_info.action]["reversible_nodes"].append(cycle_length > 0)

        if node_info.terminated:

            observations = nx.dijkstra_path(graph, start_node.observation, node_info.observation)
            actions = []
            for i in range(len(observations) - 1):
                edge_info = graph.get_edge_data(observations[i], observations[i + 1])["info"]
                actions.append(edge_info.action)

            solved_paths.append(actions)

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
        "mean_children": np.nanmean(graph_metrics["children_per_node"]),
        "std_children": np.nanstd(graph_metrics["children_per_node"]),
        "max_children": np.nanmax(np.asarray(graph_metrics["children_per_node"], dtype=np.float16), initial=np.NAN),
        "min_children": np.nanmin(np.asarray(graph_metrics["children_per_node"], dtype=np.float16), initial=np.NAN),
        "num_expanded_nodes": np.sum(np.array(graph_metrics["expanded_nodes"], dtype=bool)),
        "mean_expanded_node_children": np.nanmean(graph_metrics["expanded_node_children"]),
        "std_expanded_node_children": np.nanstd(graph_metrics["expanded_node_children"]),
        "max_expanded_node_children": np.nanmax(graph_metrics["expanded_node_children"]),
        "min_expanded_node_children": np.nanmin(graph_metrics["expanded_node_children"]),
        "mean_visits_per_node": np.nanmean(graph_metrics["visits_per_node"]),
        "std_visits_per_node": np.nanstd(graph_metrics["visits_per_node"]),
        "max_visits_per_node": np.nanmax(graph_metrics["visits_per_node"]),
        "min_visits_per_node": np.nanmin(graph_metrics["visits_per_node"]),
        "clustering_coefficient": np.nanmean(graph_metrics["clustering_coefficient"]),
        "reversible_nodes": np.sum(np.array(graph_metrics["reversible_nodes"], dtype=bool)),
        "reversibility_percentage": reversibility_percentage,
        "cycle_length": np.nanmean(graph_metrics["cycle_length"]),
        "std_cycle_length": np.nanstd(graph_metrics["cycle_length"]),
        "max_cycle_length": np.nanmax(graph_metrics["cycle_length"]),
        "min_cycle_length": np.nanmin(graph_metrics["cycle_length"]),
    }

    # Calculate aggregated action metrics
    aggregated_action_metrics = {}
    for action_id, metrics in action_metrics.items():
        if metrics["times_selected"] != 0:
            reversibility_percentage = (
                np.sum(np.array(metrics["reversible_nodes"], dtype=bool)) / metrics["times_selected"]
            )

            if len(graph_metrics["expanded_node_children"]) == 0:
                mean_exp_node_children = np.NAN
                std_exp_node_children = np.NAN
                max_exp_node_children = np.NAN
                min_exp_node_children = np.NAN
            else:
                mean_exp_node_children = np.nanmean(
                    np.asarray(graph_metrics["expanded_node_children"], dtype=np.float16)
                )
                std_exp_node_children = np.nanstd(np.asarray(graph_metrics["expanded_node_children"], dtype=np.float16))
                max_exp_node_children = np.nanmax(np.asarray(graph_metrics["expanded_node_children"], dtype=np.float16))
                min_exp_node_children = np.nanmin(np.asarray(graph_metrics["expanded_node_children"], dtype=np.float16))

            aggregated_action_metrics[action_id] = {
                "mean_reward": np.nanmean(metrics["rewards"]),
                "std_reward": np.nanstd(metrics["rewards"]),
                "max_reward": np.nanmax(metrics["rewards"]),
                "min_reward": np.nanmin(metrics["rewards"]),
                "mean_children": np.nanmean(metrics["children"]),
                "std_children": np.nanstd(metrics["children"]),
                "max_children": np.nanmax(metrics["children"]),
                "min_children": np.nanmin(metrics["children"]),
                "mean_expanded_node_children": mean_exp_node_children,
                "std_expanded_node_children": std_exp_node_children,
                "max_expanded_node_children": max_exp_node_children,
                "min_expanded_node_children": min_exp_node_children,
                "times_selected": metrics["times_selected"],
                "percentage_of_times_selected_as_best_action": 0,
                "reversibility_percentage": reversibility_percentage,
                "cycle_length": np.nanmean(metrics["cycle_length"]),
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

    aggregate_graph_metrics_pd = pd.DataFrame.from_dict(aggregate_graph_metrics, orient="index")
    aggregated_action_metrics_pd = pd.DataFrame.from_dict(aggregated_action_metrics, orient="index")
    solved_paths_metrics_pd = pd.DataFrame(solved_paths)

    return aggregate_graph_metrics_pd, aggregated_action_metrics_pd, solved_paths_metrics_pd


def run_analysis(run_ids, num_actions, config):

    graphs = []
    for run_id in run_ids:
        _, _, _, graph, _ = load_run("markotot/MCGS", f"{run_id}", analysed_metrics=[])
        graphs.append(graph)

    graph_dataframes = []
    action_metrics_dataframes = []
    solved_path_dataframes = []

    for graph in graphs:
        graph_metrics, action_metrics, solved_paths = analyse_graph_metrics(graph, num_actions=num_actions)
        graph_dataframes.append(graph_metrics)
        action_metrics_dataframes.append(action_metrics)
        solved_path_dataframes.append(solved_paths)

    aggregated_graph_metrics = pd.concat(graph_dataframes).groupby(level=0).mean()
    aggregated_action_metrics = pd.concat(action_metrics_dataframes).groupby(level=0).mean()
    aggregated_solved_paths = pd.concat(solved_path_dataframes)

    return aggregated_graph_metrics, aggregated_action_metrics, aggregated_solved_paths


@hydra.main(version_base=None, config_path="configs", config_name="aggregate_data")
def run_app(config: DictConfig) -> None:

    run_ids = ["MCGS-5978", "MCGS-5993", "MCGS-5992"]
    num_actions = 7

    aggregated_graph_metrics, aggregated_action_metrics, aggregated_solved_paths = run_analysis(
        run_ids=run_ids, num_actions=num_actions, config=config
    )

    logger = NeptuneLogger(config=config, name="GraphAnalysis")
    logger.upload_data_frame(output_path="metrics/graph_metrics", data_frame=aggregated_graph_metrics)
    logger.upload_data_frame(output_path="metrics/action_metrics", data_frame=aggregated_action_metrics)
    logger.upload_data_frame(output_path="metrics/solved_path_metrics", data_frame=aggregated_solved_paths)
    logger.close()


if __name__ == "__main__":
    run_app()
