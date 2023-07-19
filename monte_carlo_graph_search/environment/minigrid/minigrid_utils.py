from enum import Enum


class EnvType(Enum):
    Empty = 0
    DoorKey = 1


OBJECT_TO_TEXT = {
    "unseen": 'U',
    "empty": 'E',
    "wall": 'W',
    "floor": ' ',
    "door": 'D',
    "key": 'K',
    "ball": 'B',
    "box": 'X',
    "goal": 'G',
    "lava": 'L',
    "agent": 'A',
}

OBJECT_TO_IDX = {
    "unseen": 0,
    "empty": 1,
    "wall": 2,
    "floor": 3,
    "door": 4,
    "key": 5,
    "ball": 6,
    "box": 7,
    "goal": 8,
    "lava": 9,
    "agent": 10,
}

COLOR_TO_IDX = {"red": 0, "green": 1, "blue": 2, "purple": 3, "yellow": 4, "grey": 5}

TEXT_TO_OBJECT = dict(zip(OBJECT_TO_TEXT.values(), OBJECT_TO_TEXT.keys()))
IDX_TO_OBJECT = dict(zip(OBJECT_TO_IDX.values(), OBJECT_TO_IDX.keys()))
IDX_TO_COLOR = dict(zip(COLOR_TO_IDX.values(), COLOR_TO_IDX.keys()))


def get_action_list():
    print("0 - Turn left")
    print("1 - Turn right")
    print("2 - Move forward")
    print("3 - Pick up object")
    print("4 - Drop object")
    print("5 - Interact")
    print("6 - Done")


def agent_rotation_to_text(agent_dir):
    return {0: "right", 1: "down", 2: "left", 3: "up"}[agent_dir]


def agent_action_to_text(action):
    return {0: "Turns left",
            1: "Turns right",
            2: "Moves forward",
            3: "Picks up object",
            4: "Drops object",
            5: "Interacts",
            6: "Done",
            }[action]


def generate_mission():
    return f"Reach the goal"


def observation_to_text(node):
    agent_pos_x = node.id[0]
    agent_pos_y = node.id[1]
    agent_dir = agent_rotation_to_text(node.id[2])
    carry = node.id[3]
    door_open = node.id[4]
    door_locked = node.id[5]
    return f"Agent position: ({agent_pos_x}, {agent_pos_y})\t" \
           f"Agent direction: {agent_dir}\t" \
           f"Carry: {carry}\t" \
           f"Door open: {door_open}"\
           f"Door locked: {door_locked}\n"


