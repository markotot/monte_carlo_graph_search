import hydra
from omegaconf import DictConfig

from monte_carlo_graph_search.core.logger import NeptuneLogger

# from monte_carlo_graph_search.utils.data_analysis import aggregate_metrics


@hydra.main(version_base=None, config_path="configs", config_name="aggregate_data")
def run_app(config: DictConfig) -> None:

    # start_id = config.start_run_id
    # end_id = config.end_run_id
    # metrics = aggregate_metrics(range(start_id, end_id))

    logger = NeptuneLogger(config=config, name="Aggregate Data")
    # for metric in metrics.keys():
    #     logger.upload_data_frame(output_path=f"metrics/{start_id}-{end_id}/{metric}", data_frame=metrics[metric])

    with open("test.txt", "w") as f:
        f.write(logger.get_id())
    logger.close()


if __name__ == "__main__":
    run_app()
