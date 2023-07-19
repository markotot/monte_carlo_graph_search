import neptune
import numpy as np


class NeptuneLogger:

    def __init__(self, config):
        self.config = config

        tags = self.create_tags()
        self.run = neptune.init_run(project=self.config.neptune_project, tags=tags)
        self.run["config"] = self.config

    def write(self, data, timestep):
        for key, value in data.items():
            if not np.isnan(value):
                self.run[key].log(value, step=timestep)

    def close(self):
        self.run.stop()

    def create_tags(self):

        tags = []
        if self.config.novelty.use_novelty_detection is True:
            tags += ["novelty"]

        if self.config.stored_rollouts.use_stored_rollouts:
            tags += ["stored rollouts"]

        return tags

