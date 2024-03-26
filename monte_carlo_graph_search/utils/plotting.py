import math

import cv2
import matplotlib.pyplot as plt
import numpy as np


def pad_images(images: np.ndarray, top=0, bottom=0, left=0, right=0, constant=0) -> np.ndarray:
    assert len(images.shape) == 4, "not a batch of images!"
    return np.pad(images, ((0, 0), (top, bottom), (left, right), (0, 0)), mode="constant", constant_values=constant)


def plot_images(seed_text, images, reward, save_to_neptune):
    image_len = len(images)

    empty = np.array(images[0].copy())
    empty.fill(0)

    cols = math.sqrt(image_len)
    if math.floor(cols) < cols:
        cols = math.floor(cols) + 1
    else:
        cols = math.floor(cols)  # for some reason this is needed

    rows = math.ceil(len(images) / cols)

    images.extend(((cols * rows) - image_len) * [empty])

    padded_images = pad_images(np.array(images), top=3, bottom=3, left=3, right=3)
    image_rows = []
    resize_factor = 4
    for i in range(rows):
        image_slice = padded_images[i * cols : (i + 1) * cols]
        image_row = np.concatenate(image_slice, 1)
        x, y, _ = image_row.shape
        image_row_resized = cv2.resize(
            image_row, dsize=(y // resize_factor, x // resize_factor), interpolation=cv2.INTER_CUBIC
        )
        image_rows.append(image_row_resized)

    image = np.concatenate(image_rows, 0)

    if save_to_neptune:
        return image
    else:
        plt.axis("off")
        plt.title(f"{seed_text}   steps: {image_len - 1}   reward: {round(reward, 2)}")
        plt.imshow(image)
        plt.show()
        return None
