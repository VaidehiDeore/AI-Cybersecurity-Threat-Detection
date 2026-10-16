"""Prediction and transparent alert-severity helpers."""
from datetime import datetime, timezone
import joblib
import pandas as pd
from src.config import MODEL_PATH

SEVERITY = {
    "NORMAL": "INFO",
    "ANOMALY": "MEDIUM",
    "BRUTE_FORCE": "HIGH",
    "DOS": "CRITICAL",
}

def predict_records(records, model_path=MODEL_PATH):
    model = joblib.load(model_path)
    frame = pd.DataFrame(records)
    predictions = model.predict(frame)
    probabilities = model.predict_proba(frame) if hasattr(model, "predict_proba") else None
    classes = list(model.classes_)
    results = []
    for index, predicted in enumerate(predictions):
        label = str(predicted)
        confidence = float(max(probabilities[index])) if probabilities is not None else None
        results.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "predicted_label": label,
            "threat_detected": label != "NORMAL",
            "severity": SEVERITY.get(label, "MEDIUM"),
            "confidence": round(confidence, 4) if confidence is not None else None,
        })
    return results

def demo_records():
    return [
        {"duration": 2.4, "src_bytes": 1500, "dst_bytes": 900, "failed_logins": 0,
         "connection_count": 4, "request_rate": 3.2, "syn_error_rate": 0.03, "service": "web"},
        {"duration": 0.2, "src_bytes": 220, "dst_bytes": 30, "failed_logins": 0,
         "connection_count": 130, "request_rate": 180, "syn_error_rate": 0.92, "service": "web"},
        {"duration": 1.1, "src_bytes": 180, "dst_bytes": 100, "failed_logins": 25,
         "connection_count": 28, "request_rate": 22, "syn_error_rate": 0.2, "service": "ssh"},
    ]

if __name__ == "__main__":
    from src.train import train_model
    if not MODEL_PATH.exists():
        train_model()
    for result in predict_records(demo_records()):
        print(result)
