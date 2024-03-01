import neptune

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


if __name__ == "__main__":

    run_ids = [126, 132, 133]
    aggregate_metrics = {}
    for run_id in run_ids:
        run_metrics = load_run("markotot/MCGS", f"MCGS-{run_id}")
        for metric in run_metrics:
            if metric not in aggregate_metrics:
                aggregate_metrics[metric] = run_metrics[metric]
            else:
                aggregate_metrics[metric] += run_metrics[metric]

    print(aggregate_metrics["moves"])
