"""Generate safe, synthetic network-flow records for reproducible demonstrations."""
from pathlib import Path
import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "duration", "src_bytes", "dst_bytes", "failed_logins",
    "connection_count", "request_rate", "syn_error_rate", "service"
]
NUMERIC_COLUMNS = [
    "duration", "src_bytes", "dst_bytes", "failed_logins",
    "connection_count", "request_rate", "syn_error_rate"
]

def generate_dataset(n_rows: int = 5000, random_state: int = 42) -> pd.DataFrame:
    """Create labeled NORMAL, DOS, BRUTE_FORCE, and ANOMALY flow examples.

    These are synthetic teaching records, not captured network traffic.
    """
    rng = np.random.default_rng(random_state)
    labels = rng.choice(
        ["NORMAL", "DOS", "BRUTE_FORCE", "ANOMALY"],
        size=n_rows, p=[0.68, 0.14, 0.10, 0.08]
    )
    rows = []
    for label in labels:
        if label == "NORMAL":
            duration = rng.gamma(2.0, 2.0)
            src_bytes = rng.lognormal(7.0, 0.8)
            dst_bytes = rng.lognormal(6.8, 0.8)
            failed_logins = rng.poisson(0.15)
            connection_count = rng.poisson(5) + 1
            request_rate = rng.gamma(2.0, 2.0)
            syn_error_rate = rng.beta(1.0, 18.0)
        elif label == "DOS":
            duration = rng.gamma(1.0, 0.4)
            src_bytes = rng.lognormal(5.5, 0.7)
            dst_bytes = rng.lognormal(3.5, 0.7)
            failed_logins = rng.poisson(0.1)
            connection_count = rng.poisson(70) + 25
            request_rate = rng.gamma(8.0, 15.0)
            syn_error_rate = rng.beta(8.0, 2.0)
        elif label == "BRUTE_FORCE":
            duration = rng.gamma(2.0, 1.0)
            src_bytes = rng.lognormal(5.0, 0.5)
            dst_bytes = rng.lognormal(4.5, 0.5)
            failed_logins = rng.poisson(18) + 5
            connection_count = rng.poisson(20) + 8
            request_rate = rng.gamma(4.0, 4.0)
            syn_error_rate = rng.beta(2.0, 8.0)
        else:
            duration = rng.lognormal(3.0, 1.0)
            src_bytes = rng.lognormal(9.5, 1.0)
            dst_bytes = rng.lognormal(8.8, 1.0)
            failed_logins = rng.poisson(3)
            connection_count = rng.poisson(25) + 5
            request_rate = rng.gamma(5.0, 8.0)
            syn_error_rate = rng.beta(4.0, 4.0)
        rows.append({
            "duration": float(max(duration, 0)),
            "src_bytes": float(max(src_bytes, 0)),
            "dst_bytes": float(max(dst_bytes, 0)),
            "failed_logins": int(failed_logins),
            "connection_count": int(connection_count),
            "request_rate": float(max(request_rate, 0)),
            "syn_error_rate": float(np.clip(syn_error_rate, 0, 1)),
            "service": rng.choice(["web", "dns", "ssh", "database", "api"]),
            "label": label,
        })
    return pd.DataFrame(rows)

def save_dataset(path: str | Path, n_rows: int = 5000, random_state: int = 42) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    generate_dataset(n_rows, random_state).to_csv(path, index=False)
    return path

if __name__ == "__main__":
    from src.config import SYNTHETIC_DATA_PATH
    output = save_dataset(SYNTHETIC_DATA_PATH)
    print(f"Generated synthetic dataset: {output}")
    print(pd.read_csv(output).head().to_string(index=False))
