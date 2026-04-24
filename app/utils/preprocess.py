import numpy as np
from PIL import Image

size = (224, 224)

mean_vals = [0.485, 0.456, 0.406]
std_vals = [0.229, 0.224, 0.225]


def load_and_preprocess(path):
    img = Image.open(path).convert("RGB")
    img = img.resize(size)

    arr = np.array(img).astype("float32") / 255.0

    mean = np.array(mean_vals, dtype="float32")
    std = np.array(std_vals, dtype="float32")

    arr = (arr - mean) / std

    arr = np.expand_dims(arr, axis=0)

    return arr
