import copy

import numpy as np
from minigrid.core.grid import Grid
from minigrid.core.world_object import Ball, Box, Door, Floor, Goal, Key, Lava, Wall
from minigrid.envs import DoorKeyEnv

from monte_carlo_graph_search.environment.minigrid import minigrid_levels
from monte_carlo_graph_search.environment.minigrid.minigrid_utils import (
    TEXT_TO_OBJECT,
    EnvType,
)


class CustomMinigridEnv(DoorKeyEnv):
    """
    Environment with a door and key, sparse reward
    """

    forward_model_calls = 0

    def __init__(self, env_config):

        self.config = env_config
        self.level_ascii = minigrid_levels.load_level(self.config.level_name)

        super().__init__(size=self.config.size, render_mode="rgb_array", highlight=False)

        self.is_stochastic = self.config.action_failure_probability > 0

        self.env_type = EnvType.DoorKey
        self.random = np.random.RandomState(self.config.seed)
        self.name = "GymDoorkey"

        self.action = None
        self.state = None
        self.reward = None

        self.terminated = None
        self.truncated = None

        self.info = None

        self.reset()

    def step(self, action):

        self.action = action  # Save the original action
        self.state, self.reward, self.terminated, self.truncated, self.info = super().step(action)  # Do the step
        observation = self.observation()
        CustomMinigridEnv.forward_model_calls += 1
        return observation, self.reward, self.terminated, self.truncated, self.info

    def stochastic_step(self, action, action_failure_prob=None):
        self.action = action  # Save the original action

        if self.is_stochastic:  # If the env is stochastic check if action should fail
            if action_failure_prob < self.config.action_failure_probability:  # If the action should fail, swap it here
                action = 6  # No action

        return self.step(action)

    def _gen_grid(self, width, height):

        if self.level_ascii is None:
            super()._gen_grid(width, height)
        else:
            self.grid = Grid(width, height)

            for j, ascii_row in enumerate(self.level_ascii["level_layout"]):
                for i, text_object in enumerate(ascii_row):
                    self.create_grid(type_text=text_object, row=i, column=j)

            self.agent_pos = self.level_ascii["agent"]["position"]
            self.agent_dir = self.level_ascii["agent"]["direction"]
            self.grid.set(self.agent_pos[0], self.agent_pos[1], None)

            for door in self.level_ascii["doors"]:
                is_open = door["status"] == "open"
                is_locked = door["status"] == "locked"
                self.put_obj(
                    Door(color=door["colour"], is_open=is_open, is_locked=is_locked),
                    door["position"][0],
                    door["position"][1],
                )

            for key in self.level_ascii["keys"]:
                self.put_obj(Key(color=key["colour"]), key["position"][0], key["position"][1])

    def create_grid(self, type_text: int, row: int, column: int):

        obj_type = TEXT_TO_OBJECT[type_text]
        if obj_type == "empty" or obj_type == "unseen":  # These are not objects
            return
        if obj_type == "agent" or obj_type == "door" or obj_type == "key":  # These will be created separately
            return

        if obj_type == "wall":
            v = Wall("grey")
        elif obj_type == "floor":
            v = Floor("blue")  # ignore the floor
            return
        elif obj_type == "ball":
            v = Ball("blue")
        elif obj_type == "box":
            v = Box("orange")
        elif obj_type == "goal":
            v = Goal()
        elif obj_type == "lava":
            v = Lava()
        else:
            AssertionError("unknown object type in decode '%s'" % obj_type)

        self.put_obj(v, row, column)

    def reset(self):

        self.state = None
        self.terminated = None
        self.truncated = None
        self.reward = None
        self.info = None

        super().reset(seed=self.config.seed)

        return self.observation()

    def render(self):
        return super().render()

    def get_agent_position(self):
        agent_pos_x = self.agent_pos[0]
        agent_pos_y = self.agent_pos[1]
        agent_dir = self.agent_rotation_mapper(self.agent_dir)
        return tuple(agent_pos_x, agent_pos_y, agent_dir)

    def observation(self):
        return self.get_observation()

    def get_observation(self):
        agent_pos_x = self.agent_pos[0]
        agent_pos_y = self.agent_pos[1]
        agent_dir = self.agent_dir
        agent_carry = None if self.carrying is None else self.carrying.type

        doors_open = [tile.is_open for tile in self.grid.grid if tile is not None and tile.type == "door"]
        doors_locked = [tile.is_locked for tile in self.grid.grid if tile is not None and tile.type == "door"]
        grid = [("empty" if tile is None else tile.type) for tile in self.grid.grid]

        return tuple([agent_pos_x, agent_pos_y, agent_dir, agent_carry] + doors_open + doors_locked + grid)

    def copy(self):
        return copy.deepcopy(self)

    def get_local_surrounding(self, sight=1):

        surrounding = np.zeros((2 * sight + 1, 2 * sight + 1), dtype=int)

        player_column = self.agent_pos[0]
        player_row = self.agent_pos[1]
        grid = np.reshape(self.grid.grid, (self.height, self.width))

        row = 0
        column = 0
        for i in range(player_row - sight, player_row + sight + 1):
            for j in range(player_column - sight, player_column + sight + 1):

                if i < 0 or i >= self.height or j < 0 or j >= self.width:
                    surrounding[row][column] = -1
                else:
                    element = "empty" if grid[i][j] is None else grid[i][j].type
                    if element == "empty":
                        surrounding[row][column] = 0
                    elif element == "wall":
                        surrounding[row][column] = 1
                    elif element == "key":
                        surrounding[row][column] = 2
                    elif element == "door":
                        surrounding[row][column] = 3
                    elif element == "goal":
                        surrounding[row][column] = 4
                column += 1

            column = 0
            row += 1

        return surrounding

    def process_grid(self):
        grid = np.reshape(self.grid.grid, (self.height, self.width))
        surrounding = np.zeros(grid.shape)
        for i in range(self.height):
            for j in range(self.width):
                element = "empty" if grid[i][j] is None else grid[i][j].type
                if element == "empty":
                    surrounding[i][j] = 0
                elif element == "wall":
                    surrounding[i][j] = 1
                elif element == "key":
                    surrounding[i][j] = 2
                elif element == "door":
                    surrounding[i][j] = 3
                elif element == "goal":
                    surrounding[i][j] = 4

        return surrounding
