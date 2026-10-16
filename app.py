"""Flask API and multi-page-style SOC dashboard for local demonstrations."""
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd

from src.config import ROOT_DIR, MODEL_PATH, METRICS_PATH, SYNTHETIC_DATA_PATH
from src.detect import predict_records, demo_records
from src.data_generator import save_dataset

app = Flask(__name__, static_folder="web", static_url_path="/static")

def load_data():
    if not SYNTHETIC_DATA_PATH.exists():
        save_dataset(SYNTHETIC_DATA_PATH)
    return pd.read_csv(SYNTHETIC_DATA_PATH)

def load_metrics():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {}

@app.get("/")
def dashboard():
    return send_from_directory(ROOT_DIR / "web", "index.html")

@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "model_ready": MODEL_PATH.exists(),
        "mode": "synthetic_local_simulation",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.get("/api/summary")
def summary():
    data = load_data()
    counts = data["label"].value_counts().to_dict()
    metrics = load_metrics()
    return jsonify({
        "total_flows": int(len(data)),
        "label_counts": {str(k): int(v) for k, v in counts.items()},
        "metrics": {
            "accuracy": metrics.get("accuracy"),
            "precision": metrics.get("precision_weighted"),
            "recall": metrics.get("recall_weighted"),
            "f1": metrics.get("f1_weighted"),
            "test_rows": metrics.get("test_rows")
        },
        "recent_flows": data.tail(12).to_dict(orient="records")
    })

@app.get("/api/traffic")
def traffic():
    data = load_data()
    return jsonify({
        "records": data.tail(40).to_dict(orient="records"),
        "total": int(len(data)),
        "generated_at": datetime.now(timezone.utc).isoformat()
    })

@app.get("/api/analytics")
def analytics():
    data = load_data()
    counts = data["label"].value_counts().to_dict()
    metrics = load_metrics()
    return jsonify({
        "label_counts": {str(k): int(v) for k, v in counts.items()},
        "metrics": metrics,
        "feature_summary": {
            "avg_request_rate": round(float(data["request_rate"].mean()), 2),
            "avg_connections": round(float(data["connection_count"].mean()), 2),
            "avg_failed_logins": round(float(data["failed_logins"].mean()), 2),
            "high_request_rate_flows": int((data["request_rate"] >= data["request_rate"].quantile(.9)).sum())
        }
    })

@app.get("/api/alerts")
def alerts():
    if not MODEL_PATH.exists():
        return jsonify({"error": "Model is not trained. Run: python -m src.train"}), 503
    results = predict_records(demo_records())
    return jsonify({"alerts": results, "generated_at": datetime.now(timezone.utc).isoformat()})

@app.post("/api/predict")
def predict():
    if not MODEL_PATH.exists():
        return jsonify({"error": "Model is not trained. Run: python -m src.train"}), 503
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list) or not payload["records"]:
        return jsonify({"error": "Send JSON with a non-empty 'records' array."}), 400
    try:
        results = predict_records(payload["records"])
    except (ValueError, TypeError, KeyError) as exc:
        return jsonify({"error": f"Invalid feature data: {exc}"}), 400
    return jsonify({"predictions": results})

if __name__ == "__main__":
    # Local-only development server. Do not expose debug mode publicly.
    app.run(host="127.0.0.1", port=5000, debug=False)
