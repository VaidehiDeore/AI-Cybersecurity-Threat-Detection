"""Train and evaluate a baseline supervised threat classifier."""
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from src.config import MODEL_PATH, METRICS_PATH, OUTPUTS_DIR, SYNTHETIC_DATA_PATH, RANDOM_STATE
from src.data_generator import save_dataset
from src.preprocessing import build_preprocessor, clean_frame, TARGET_COLUMN

def train_model(dataset_path=SYNTHETIC_DATA_PATH):
    if not dataset_path.exists():
        save_dataset(dataset_path)
    data = clean_frame(pd.read_csv(dataset_path))
    X = data.drop(columns=[TARGET_COLUMN])
    y = data[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    pipeline = Pipeline([
        ("preprocessor", build_preprocessor(X_train.assign(label=y_train))),
        ("classifier", RandomForestClassifier(
            n_estimators=160, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1
        )),
    ])
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test, predictions, average="weighted", zero_division=0
    )
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision_weighted": float(precision),
        "recall_weighted": float(recall),
        "f1_weighted": float(f1),
        "test_rows": int(len(y_test)),
        "classes": sorted(str(c) for c in y.unique()),
        "confusion_matrix_labels": sorted(str(c) for c in y.unique()),
        "confusion_matrix": confusion_matrix(
            y_test, predictions, labels=sorted(y.unique())
        ).tolist(),
        "classification_report": classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        ),
        "dataset_note": "Synthetic educational data; not a real-world benchmark."
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("Training complete.")
    print(f"Rows used: {len(data)} | Test rows: {len(y_test)}")
    print(f"Accuracy:  {metrics['accuracy']:.3f}")
    print(f"Precision: {metrics['precision_weighted']:.3f}")
    print(f"Recall:    {metrics['recall_weighted']:.3f}")
    print(f"F1 score:  {metrics['f1_weighted']:.3f}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metrics: {METRICS_PATH}")
    return pipeline, metrics

if __name__ == "__main__":
    train_model()
