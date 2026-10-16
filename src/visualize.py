"""Create evaluation and anomaly plots as image assets."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.config import METRICS_PATH, OUTPUTS_DIR, SYNTHETIC_DATA_PATH, MODEL_PATH
from src.anomaly import train_anomaly_detector, score_anomalies

def create_visuals():
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if not SYNTHETIC_DATA_PATH.exists():
        from src.data_generator import save_dataset
        save_dataset(SYNTHETIC_DATA_PATH)
    data = pd.read_csv(SYNTHETIC_DATA_PATH)
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    labels = metrics["confusion_matrix_labels"]
    cm = metrics["confusion_matrix"]
    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels)
    plt.title("Threat Classifier — Confusion Matrix")
    plt.xlabel("Predicted label")
    plt.ylabel("Actual label")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "confusion_matrix.png", dpi=160)
    plt.close()

    detector = train_anomaly_detector(data)
    scored = score_anomalies(data, detector)
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=scored.sample(min(1200, len(scored)), random_state=42),
                    x="request_rate", y="connection_count",
                    hue="anomaly_flag", palette={False: "#0891b2", True: "#e11d48"},
                    alpha=0.7, s=28)
    plt.title("Synthetic Network Traffic — Anomaly Highlights")
    plt.xlabel("Request rate")
    plt.ylabel("Connection count")
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "anomaly_detection.png", dpi=160)
    plt.close()
    print(f"Visuals saved to {OUTPUTS_DIR}")

if __name__ == "__main__":
    create_visuals()
