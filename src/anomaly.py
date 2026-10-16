"""Unsupervised anomaly scoring for numeric network-flow features."""
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from src.config import MODELS_DIR

ANOMALY_MODEL_PATH = MODELS_DIR / "isolation_forest.joblib"
FEATURES = ["duration", "src_bytes", "dst_bytes", "failed_logins",
            "connection_count", "request_rate", "syn_error_rate"]

def train_anomaly_detector(frame: pd.DataFrame):
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("isolation_forest", IsolationForest(
            contamination=0.08, random_state=42, n_estimators=150
        )),
    ])
    model.fit(frame[FEATURES])
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ANOMALY_MODEL_PATH)
    return model

def score_anomalies(frame: pd.DataFrame, model=None):
    if model is None:
        model = joblib.load(ANOMALY_MODEL_PATH)
    result = frame.copy()
    result["anomaly_flag"] = model.predict(result[FEATURES]).astype(int) == -1
    result["anomaly_score"] = -model.decision_function(result[FEATURES])
    return result
