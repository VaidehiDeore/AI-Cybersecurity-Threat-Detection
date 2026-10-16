"""Reusable preprocessing helpers for the threat classifier."""
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

TARGET_COLUMN = "label"

def build_preprocessor(frame: pd.DataFrame) -> ColumnTransformer:
    feature_frame = frame.drop(columns=[TARGET_COLUMN], errors="ignore")
    numeric = feature_frame.select_dtypes(include=["number"]).columns.tolist()
    categorical = feature_frame.select_dtypes(exclude=["number"]).columns.tolist()

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipeline, numeric),
        ("categorical", categorical_pipeline, categorical),
    ])

def clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    cleaned.columns = [str(col).strip() for col in cleaned.columns]
    cleaned = cleaned.drop_duplicates()
    if TARGET_COLUMN not in cleaned.columns:
        raise ValueError(f"Dataset must contain a '{TARGET_COLUMN}' target column.")
    cleaned = cleaned.dropna(subset=[TARGET_COLUMN])
    return cleaned
