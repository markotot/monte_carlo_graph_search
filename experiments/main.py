import hydra
import pandas as pd
from omegaconf import DictConfig

from experiments.analyse_graphs import analyse_graph_metrics
from monte_carlo_graph_search.agents.mcgs_agent import MCGSAgent
from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.environment.griddly.clusters_env import ClustersEnv
from monte_carlo_graph_search.environment.griddly.clusters_novelty import (
    ClustersNovelty,
)
from monte_carlo_graph_search.environment.minigrid.custom_minigrid_env import (
    CustomMinigridEnv,
)
from monte_carlo_graph_search.environment.minigrid.minigrid_novelty import (
    MinigridNovelty,
)
from monte_carlo_graph_search.utils import utils
from monte_carlo_graph_search.utils.plotting import plot_images

# TODO: fix plotting so that it can plot images in neptune through apocrita (probably needs scaling)
# TODO: check why CLUSTERS play isn't optimal
#  is there something wrong with the value saved in the graph?
#  print the best value node that is found in the graph
#  create custom reward-done function?


def init_env(config):

    config_type = config.env.type
    if config_type == "minigrid":
        env = CustomMinigridEnv(env_config=config.env)
        novelty = MinigridNovelty(config=config.novelty)
    elif config_type == "clusters":
        env = ClustersEnv(config=config.env)
        novelty = ClustersNovelty(config=config.novelty)
    else:
        raise ValueError(f"Unknown environment type: {config_type}")
    return env, novelty


@hydra.main(version_base=None, config_path="configs", config_name="mcgs")
def run_app(config: DictConfig) -> None:

    logger = NeptuneLogger(config=config, name="MCGS")
    env, novelty = init_env(config)

    agent = MCGSAgent(env=env, novelty=novelty, logger=logger, config=config)

    image = env.render()
    images = [image]
    logger.upload_image("images/initial_state", image)
    total_reward = 0
    for _ in range(config.search.max_moves):
        action = agent.plan()
        state, reward, terminated, truncated, info = agent.act(action)
        image = env.render()
        images.append(image)
        total_reward += reward
        if terminated or truncated:
            break

        # agent.graph.draw_graph()
    combined_images = plot_images(
        f"env seed: {config.env.seed}   agent seed: {config.search.seed}",
        images,
        total_reward,
        save_to_neptune=True,
    )
    logger.upload_image("images/combined_images", combined_images)

    if config.search.save_graph:
        name = f"graph/{config.env.type}/{config.env.seed}_{config.search.seed}"
        # budget = config.search.max_moves * config.search.budget_per_move
        logger.upload_pickle(name, agent.graph.graph)

    metrics = agent.get_final_metrics(terminated or truncated, total_reward)
    logger.write(metrics, agent.move_counter)

    if config.search.analyse_metrics:

        all_actions_df = pd.DataFrame.from_dict(agent.all_actions, orient="index")
        logger.upload_data_frame(output_path="analysis/all_actions", data_frame=all_actions_df)

        graph_metrics, action_metrics, solved_paths = analyse_graph_metrics(
            agent.graph.graph, num_actions=env.action_space.n
        )
        logger.upload_data_frame(output_path="analysis/solved_paths", data_frame=solved_paths)
        logger.upload_data_frame(output_path="analysis/graph_metrics", data_frame=graph_metrics)
        logger.upload_data_frame(output_path="analysis/action_metrics", data_frame=action_metrics)

    utils.add_to_experiment_file(f"../experiment_runs/{config.run_name}.txt", logger.get_id())
    logger.close()


if __name__ == "__main__":
    run_app()
