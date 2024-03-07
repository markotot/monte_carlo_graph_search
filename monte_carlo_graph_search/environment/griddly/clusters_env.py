from os import getcwd

import gym
import numpy as np
from griddly import GymWrapperFactory, gd
from minigrid.envs import DoorKeyEnv


class ClustersEnv(DoorKeyEnv):
    """
    Environment with a door and key, sparse reward
    """

    forward_model_calls = 0
    initialized = False

    def __init__(self, env_config):

        if ClustersEnv.initialized is False:
            wrapper = GymWrapperFactory()

            path = getcwd().split("/")[-1] == "experiments"
            yaml_path = (
                "../monte_carlo_graph_search/environment/griddly/clusters.yaml"
                if path
                else "monte_carlo_graph_search/environment/griddly/clusters.yaml"
            )
            wrapper.build_gym_from_yaml("ClustersEnv", yaml_path)
            ClustersEnv.initialized = True

        self.env = gym.make(
            "GDY-ClustersEnv-v0",
            player_observer_type=gd.ObserverType.VECTOR,
            global_observer_type=gd.ObserverType.SPRITE_2D,
        )

        self.action = None
        self.state = None
        self.reward = None
        self.done = None
        self.info = None

        self.reset()

    def step(self, action):

        self.action = action  # Save the original action
        self.state, self.reward, self.done, self.info = self.env.step(action)  # Do the step
        observation = self.observation()
        ClustersEnv.forward_model_calls += 1
        return observation, self.reward, self.done, self.info

    def stochastic_step(self, action, action_failure_prob=None):
        self.action = action  # Save the original action

        if self.is_stochastic:  # If the env is stochastic check if action should fail
            if action_failure_prob < self.config.action_failure_probability:  # If the action should fail, swap it here
                action = 6  # No action

        self.state, self.reward, self.done, self.info = self.step(action)  # Do the step
        observation = self.observation()
        return observation, self.reward, self.done, self.info

    def reset(self):

        self.state = None
        self.done = None
        self.reward = None
        self.info = None

        self.state = self.env.reset()

        return self.observation()

    def render(self):
        return self.env.render(observer="global")

    def get_agent_position(self):
        agent_pos_x = self.agent_pos[0]
        agent_pos_y = self.agent_pos[1]
        agent_dir = self.agent_rotation_mapper(self.agent_dir)
        return tuple(agent_pos_x, agent_pos_y, agent_dir)

    def observation(self):
        return self.get_observation()

    def get_observation(self):

        layers = self.state
        grid = np.zeros(shape=layers[0].shape, dtype=np.float32)
        for idx, layer in enumerate(layers):
            grid = np.add(grid, layer * (idx + 1))

        return grid.T
