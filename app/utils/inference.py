from gradio_client import Client, handle_file
import re

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = Client("Lazypanda0103/Unified-Comprehensive-Freshness-Classification")
    return _client


def predict(image_path: str) -> dict:
    client = _get_client()
    result = client.predict(image=handle_file(image_path), api_name="/predict")

    _, markdown, score = result
    score = round(float(score), 1)

    if score >= 50:
        label = "fresh"
        display_label = "Fresh"
    else:
        label = "spoiled"
        display_label = "Spoiled"

    return {
        "label": label,
        "display_label": display_label,
        "freshness_score": score,
    }
