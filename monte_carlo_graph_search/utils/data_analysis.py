import neptune
import pandas as pd

analysed_metrics = [
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


def load_run(project_id, run_id):

    run = neptune.init_run(project=project_id, with_id=run_id, mode="read-only")

    metrics = {}
    for metric in analysed_metrics:
        metrics[metric] = run[metric].fetch_values(include_timestamp=False)

    run.stop()
    return metrics


def aggregate_metrics(run_ids):

    aggregate_metrics = {}
    all_metrics = {}
    # Load all runs
    for run_id in run_ids:
        all_metrics[run_id] = load_run("markotot/MCGS", f"{run_id}")

    # Find the max steps for each metric
    for metric in analysed_metrics:
        max_steps = 0
        for run_id in run_ids:
            max_steps = max(max_steps, len(all_metrics[run_id][metric]))
        aggregate_metrics[metric] = pd.DataFrame(range(1, max_steps + 1), columns=["step"])

    # Add the values for each run to the aggregate metrics
    for metric in analysed_metrics:
        for run_id in run_ids:
            value_data_frame = all_metrics[run_id][metric].rename(columns={"value": run_id})
            aggregate_metrics[metric] = pd.concat(
                [aggregate_metrics[metric], value_data_frame[run_id]], join="outer", axis=1
            )

    # Calculate the mean, std, max, and min for each metric
    for metric in analysed_metrics:
        aggregate_metrics[metric]["mean"] = aggregate_metrics[metric].iloc[:, 1:].mean(numeric_only=True, axis=1)
        aggregate_metrics[metric]["std"] = aggregate_metrics[metric].iloc[:, 1:].std(numeric_only=True, axis=1)
        aggregate_metrics[metric]["max"] = aggregate_metrics[metric].iloc[:, 1:].max(numeric_only=True, axis=1)
        aggregate_metrics[metric]["min"] = aggregate_metrics[metric].iloc[:, 1:].min(numeric_only=True, axis=1)

    return aggregate_metrics


if __name__ == "__main__":
    run_ids = ["131", "132", "133", "138", "139"]
    metrics = aggregate_metrics(run_ids)
    print(metrics["time_per_move"])
