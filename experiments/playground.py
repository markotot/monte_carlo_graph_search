import time

import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.environment.griddly.clusters import ClustersEnv


@hydra.main(version_base=None, config_path="configs", config_name="mcgs")
def run_playground(config: DictConfig) -> None:
    env = ClustersEnv(config=config)
    env.reset()
    env.render()
    terminated = False
    truncated = False
    # desno dole levo gore gore desno dole dole levo gore gore
    # levo levo levo levo dole dole gore deno dole dole
    # desno desno gore desno dole

    action_sequence = [4, 1, 1, 3, 2, 3, 4, 1, 2, 2, 3, 4, 4, 1, 2, 1, 1, 1, 4, 4, 2, 3, 4, 4, 3, 3, 2, 3, 4]
    for action in action_sequence:
        state, reward, terminated, truncated, info = env.step(action)
        env.render()
        time.sleep(0.5)

    print(f"Reward: {reward}")
    print(f"Terminated: {terminated}")
    print(f"Truncated: {truncated}")
    print(f"Info: {info}")


if __name__ == "__main__":
    run_playground()
