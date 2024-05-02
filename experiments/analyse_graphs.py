import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.utils.data_analysis import run_graph_analysis


@hydra.main(version_base=None, config_path="configs", config_name="aggregate_data")
def run_app(config: DictConfig) -> None:

    run_ids = ["MCGS-5978", "MCGS-5993", "MCGS-5992"]
    num_actions = 7

    aggregated_graph_metrics, aggregated_action_metrics, aggregated_solved_paths = run_graph_analysis(
        run_ids=run_ids, num_actions=num_actions
    )

    logger = NeptuneLogger(config=config, name="GraphAnalysis")
    logger.upload_data_frame(output_path="metrics/graph_metrics", data_frame=aggregated_graph_metrics)
    logger.upload_data_frame(output_path="metrics/action_metrics", data_frame=aggregated_action_metrics)
    logger.upload_data_frame(output_path="metrics/solved_path_metrics", data_frame=aggregated_solved_paths)
    logger.close()


if __name__ == "__main__":
    run_app()
