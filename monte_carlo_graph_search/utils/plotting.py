import matplotlib.pyplot as plt
import numpy as np
import math

def plot_images(seed_text, images, reward):
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

    image_rows = []
    for i in range(rows):
        image_row = np.concatenate(images[i * cols: (i + 1) * cols], 1)
        image_rows.append(image_row)

    plt.axis('off')
    plt.title(f"{seed_text}   steps: {image_len - 1}   reward: {round(reward, 2)}")

    plt.imshow(np.concatenate(image_rows, 0))
    #plt.savefig(f"{Logger.directory_path + str(number)}.png", dpi=384)

    plt.show()