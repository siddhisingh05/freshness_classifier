import numpy as np
from PIL import Image

TARGET_SIZE = (224, 224)
MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def load_and_preprocess(path: str) -> np.ndarray:
    img = Image.open(path).convert("RGB")
    img = img.resize(TARGET_SIZE, Image.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = (arr - MEAN) / STD
    return np.expand_dims(arr, axis=0)
