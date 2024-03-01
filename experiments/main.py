import sys

import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.agents.mcgs_agent import MCGSAgent
from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.environment.minigrid.custom_minigrid_env import (
    CustomMinigridEnv,
)


@hydra.main(version_base=None, config_path="configs", config_name="mcgs")
def run_app(config: DictConfig) -> None:

    print(sys.argv)
    logger = NeptuneLogger(config=config)
    env = CustomMinigridEnv(env_config=config.env)
    agent = MCGSAgent(env=env, logger=logger, config=config)

    images = []

    # image = env.render()
    # plt.imshow(image)
    # plt.show()

    total_reward = 0
    for _ in range(config.search.max_moves):

        action = agent.plan()
        state, reward, done, info = agent.act(action)
        image = env.render()
        images.append(image)

        total_reward += reward
        if done:
            break

    metrics = agent.get_final_metrics(done)
    logger.write(metrics, agent.move_counter)

    # plot_images(
    #     f"env seed: {config.env.seed}   agent seed: {config.search.seed}",
    #     images,
    #     total_reward,
    # )

    logger.close()


if __name__ == "__main__":
    run_app()
