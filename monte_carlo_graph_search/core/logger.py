import neptune
import numpy as np
from neptune.types import File


class NeptuneLogger:
    def __init__(self, config, name):
        self.config = config

        tags = self.create_tags()
        self.run = neptune.init_run(
            project=self.config.neptune_project,
            name=name,
            tags=tags,
        )

        self.run["config"] = self.config

    def write(self, data, timestep):
        for key, value in data.items():
            if not np.isnan(value):
                self.run[key].log(value, step=timestep)

    def upload_data_frame(self, output_path, data_frame):

        file = File.as_html(data_frame)
        self.run[output_path].upload(file)

    def upload_config(self, output_path, data):
        self.run[output_path] = data

    def close(self):
        self.run.stop()

    def create_tags(self):

        tags = []
        if self.config.novelty.use_novelty_detection is True:
            tags += ["novelty"]

        if self.config.stored_rollouts.use_stored_rollouts is True:
            tags += ["stored rollouts"]

        return tags

    def get_id(self):
        return self.run["sys/id"].fetch()

    def add_to_experiment_file(self, file_path):
        with open(file_path, "a+") as f:
            f.write(f"{self.get_id()}\n")
