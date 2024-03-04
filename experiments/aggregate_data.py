import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.utils.data_analysis import (
    aggregate_metrics,
    env_metrics,
    search_metrics,
)


@hydra.main(version_base=None, config_path="configs", config_name="aggregate_data")
def run_app(config: DictConfig) -> None:

    with open(f"../experiment_runs/{config.run_name}.txt", "r") as f:
        run_ids = [line.rstrip() for line in f]

    metrics, essential_metrics, run_config = aggregate_metrics(run_ids, search_metrics + env_metrics)

    logger = NeptuneLogger(config=config, name="Aggregate Data")

    logger.upload_config(output_path="experiments_config", data=run_config)

    for metric in metrics.keys():
        logger.upload_data_frame(
            output_path=f"metrics/{config.start_run_id}-{config.end_run_id}/{metric}", data_frame=metrics[metric]
        )
    logger.upload_data_frame(output_path="essential_metrics", data_frame=essential_metrics)

    logger.close()


if __name__ == "__main__":
    run_app()
