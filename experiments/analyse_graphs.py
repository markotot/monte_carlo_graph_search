import os
import pickle

import neptune


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


if __name__ == "__main__":

    run_ids = ["MCGS-5846"]

    for run_id in run_ids:
        env_type, env_seed, agent_seed, graph, config = load_run("markotot/MCGS", f"{run_id}")
        print(graph)
