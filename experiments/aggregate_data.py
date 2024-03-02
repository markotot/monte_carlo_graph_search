import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.core.logger import NeptuneLogger
from monte_carlo_graph_search.utils.data_analysis import aggregate_metrics


@hydra.main(version_base=None, config_path="configs", config_name="aggregate_data")
def run_app(config: DictConfig) -> None:

    logger = NeptuneLogger(config=config, name="Aggregate Data")
    run_ids = range(config.start_run_id, config.end_run_id + 1)
    metrics = aggregate_metrics(run_ids)
    for metric in metrics.keys():
        logger.upload_data_frame(output_path=f"metrics/{metric}", data_frame=metrics[metric])

    logger.close()


if __name__ == "__main__":
    run_app()
