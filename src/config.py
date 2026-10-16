from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT_DIR / "models"
OUTPUTS_DIR = ROOT_DIR / "outputs"

SYNTHETIC_DATA_PATH = DATA_DIR / "synthetic_network_traffic.csv"
MODEL_PATH = MODELS_DIR / "threat_classifier.joblib"
PIPELINE_PATH = MODELS_DIR / "preprocessing_pipeline.joblib"
METRICS_PATH = OUTPUTS_DIR / "evaluation_metrics.json"
PREDICTIONS_PATH = OUTPUTS_DIR / "latest_predictions.csv"

RANDOM_STATE = 42
