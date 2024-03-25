import neptune
import pandas as pd

search_metrics = [
    "backpropagation_time",
    "expansion_time",
    "selection_time",
    "storing_nodes_time",
    "select_move_time",
    "maintenance_time",
    "simulation_time",
    "time_per_move",
    "backpropagation_time_percentage",
    "expansion_time_percentage",
    "selection_time_percentage",
    "storing_nodes_time_percentage",
    "select_move_time_percentage",
    "maintenance_time_percentage",
    "simulation_time_percentage",
    "time_per_move_percentage",
    "expansion_spent_budget",
    "iteration_spent_budget",
    "selection_spent_budget",
    "simulation_spent_budget",
    "iterations_per_move",
    "total_nodes",
    "total_edges",
    "total_frontier_nodes",
    "total_unreachable_nodes",
    "new_nodes",
    "novel_nodes_added",
    "total_num_simulations",
    "total_fmc",
    "total_moves",
    "moves",
    "average_reward",
    "game_finished",
]

env_metrics = [
    "key_discovered",
    "door_discovered",
    "goal_discovered",
    "subgoal_door_moves",
    "subgoal_door_nodes",
    "subgoal_door_forward_model_calls",
    "subgoal_goal_moves",
    "subgoal_goal_nodes",
    "subgoal_goal_forward_model_calls",
    "subgoal_key_moves",
    "subgoal_key_nodes",
    "subgoal_key_forward_model_calls",
]


def load_run(project_id, run_id, analysed_metrics):

    run = neptune.init_run(project=project_id, with_id=run_id, mode="read-only")

    metrics = {}
    env_seed = run["config/env/seed"].fetch()
    agent_seed = run["config/search/seed"].fetch()
    config = run["config"].fetch()
    for metric in analysed_metrics:
        metrics[metric] = run[f"metrics/{metric}"].fetch_values(include_timestamp=False)

    run.stop()

    return env_seed, agent_seed, metrics, config


def aggregate_metrics(run_ids, analysed_metrics):

    aggregate_metrics = {}
    all_metrics = {}
    # Load all runs
    for run_id in run_ids:
        env_seed, agent_seed, metrics, config = load_run("markotot/MCGS", f"{run_id}", analysed_metrics)
        all_metrics[f"MCGS-{env_seed}-{agent_seed}"] = metrics

    del config["env"]["seed"]
    del config["search"]["seed"]

    # Find the max steps for each metric
    for metric in analysed_metrics:
        max_steps = 0
        for run_id in all_metrics.keys():
            max_steps = max(max_steps, len(all_metrics[run_id][metric]))
        aggregate_metrics[metric] = pd.DataFrame(range(1, max_steps + 1), columns=["step"])

    # Add the values for each run to the aggregate metrics
    for metric in analysed_metrics:
        for run in all_metrics.keys():
            value_data_frame = all_metrics[run][metric].rename(columns={"value": run})
            aggregate_metrics[metric] = pd.concat(
                [aggregate_metrics[metric], value_data_frame[run]], join="outer", axis=1
            )

    # Calculate the mean, std, max, and min for each metric
    for metric in analysed_metrics:

        data = aggregate_metrics[metric].iloc[:, 1:]
        aggregate_metrics[metric]["mean"] = data.mean(numeric_only=True, axis=1)
        aggregate_metrics[metric]["std"] = data.std(numeric_only=True, axis=1)
        aggregate_metrics[metric]["max"] = data.max(numeric_only=True, axis=1)
        aggregate_metrics[metric]["min"] = data.min(numeric_only=True, axis=1)

    essential_metrics_names = []
    essential_metrics = []
    for metric_name in aggregate_metrics.keys():
        if len(aggregate_metrics[metric_name]) == 1:
            data = aggregate_metrics[metric_name].iloc[:, -4:].values.squeeze()
            essential_metrics.append(data)
            essential_metrics_names.append(metric_name)

    essential_metrics = pd.DataFrame(
        essential_metrics, columns=["mean", "std", "max", "min"], index=essential_metrics_names
    )
    return aggregate_metrics, essential_metrics, config


if __name__ == "__main__":
    run_ids = ["MCGS-496", "MCGS-495", "MCGS-494"]
    analysed_metrics = search_metrics + env_metrics
    metrics, essential_metrics, run_config = aggregate_metrics(run_ids, analysed_metrics)
    print(metrics)
    print(run_config)
