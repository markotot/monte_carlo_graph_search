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

    run_ids = [131, 132, 133]
    aggregate_metrics = {}

    # Load all runs
    for run_id in run_ids:
        run_metrics = load_run("markotot/MCGS", f"MCGS-{run_id}")

        for metric in run_metrics:
            if run_id == 131:
                if len(run_metrics[metric]) > 1:
                    run_metrics[metric] = run_metrics[metric].drop([len(run_metrics[metric]) - 1])

            if metric not in aggregate_metrics:
                aggregate_metrics[metric] = run_metrics[metric]
            else:
                # If the run has more steps than the aggregate, add the missing steps
                agg_len = len(aggregate_metrics[metric])
                step_difference = len(run_metrics[metric]) - agg_len
                if step_difference > 0:
                    for x in range(1, step_difference + 1):
                        # new row will have the step of the last row + 1, and the rest of the columns will be 0
                        new_row = [agg_len + x] + [0] * (len(aggregate_metrics[metric].columns) - 1)
                        aggregate_metrics[metric].loc[x + agg_len - 1] = new_row

                aggregate_metrics[metric] += run_metrics[metric]

    for metric in aggregate_metrics:
        aggregate_metrics[metric] /= len(run_ids)

    print(aggregate_metrics["moves"])
