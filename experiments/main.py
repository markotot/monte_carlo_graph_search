import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.agents.mcgs_agent import MCGSAgent
from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.environment.minigrid.custom_minigrid_env import (
    CustomMinigridEnv,
)
from monte_carlo_graph_search.utils import utils
from monte_carlo_graph_search.utils.plotting import plot_images


@hydra.main(version_base=None, config_path="configs", config_name="mcgs")
def run_app(config: DictConfig) -> None:

    logger = NeptuneLogger(config=config, name="MCGS")

    env = CustomMinigridEnv(env_config=config.env)
    agent = MCGSAgent(env=env, logger=logger, config=config)

    image = env.render()
    images = [image]
    logger.upload_image("images/initial_state", image)

    total_reward = 0
    for n in range(config.search.max_moves):
        action = agent.plan()
        state, reward, done, info = agent.act(action)
        print(f"Step {n} done!")
        image = env.render()
        images.append(image)
        total_reward += reward
        if done:
            break

        # agent.graph.draw_graph()
    print("Search done, combining images")
    combined_images = plot_images(
        f"env seed: {config.env.seed}   agent seed: {config.search.seed}",
        images,
        total_reward,
        save_to_neptune=True,
    )
    logger.upload_image("images/combined_images", combined_images)

    print("Image uploaded, logging final metrics")
    metrics = agent.get_final_metrics(done)
    logger.write(metrics, agent.move_counter)

    utils.add_to_experiment_file(f"../experiment_runs/{config.run_name}.txt", logger.get_id())
    logger.close()


if __name__ == "__main__":
    run_app()
