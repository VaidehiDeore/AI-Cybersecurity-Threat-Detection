
"""Generate reproducible synthetic network-flow records for education.

These records are simulated examples, not captured network traffic.
Attack labels are generated independently of individual feature values,
so overlapping patterns make classification less trivial.
"""
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


def generate_dataset(
    n_rows: int = 5000,
    random_state: int = 42
) -> pd.DataFrame:
    """Generate overlapping traffic patterns with four synthetic labels."""
    rng = np.random.default_rng(random_state)

    labels = rng.choice(
        ["NORMAL", "DOS", "BRUTE_FORCE", "ANOMALY"],
        size=n_rows,
        p=[0.68, 0.14, 0.10, 0.08],
    )

    rows = []

    for label in labels:
        # Start with a shared baseline for every class.
        # Attack-specific behavior modifies these values, but does not
        # force every record into a perfectly separable feature range.
        duration = rng.lognormal(0.7, 0.9)
        src_bytes = rng.lognormal(6.5, 1.25)
        dst_bytes = rng.lognormal(6.0, 1.25)
        failed_logins = rng.poisson(1.2)
        connection_count = rng.poisson(12) + 1
        request_rate = rng.gamma(2.2, 3.0)
        syn_error_rate = rng.beta(1.5, 10.0)

        if label == "DOS":
            # Elevated traffic is common, but not guaranteed for every flow.
            intensity = rng.choice(["low", "medium", "high"], p=[0.25, 0.40, 0.35])
            if intensity == "low":
                connection_count += rng.poisson(10)
                request_rate += rng.gamma(2.0, 3.0)
                syn_error_rate = rng.beta(2.0, 8.0)
            elif intensity == "medium":
                connection_count += rng.poisson(35)
                request_rate += rng.gamma(3.0, 8.0)
                syn_error_rate = rng.beta(3.0, 5.0)
            else:
                connection_count += rng.poisson(75)
                request_rate += rng.gamma(5.0, 12.0)
                syn_error_rate = rng.beta(5.0, 3.0)

        elif label == "BRUTE_FORCE":
            # Some attack flows have few failed logins; normal traffic can
            # also contain failures. This intentionally creates overlap.
            failed_logins += rng.choice(
                [rng.poisson(2), rng.poisson(8), rng.poisson(18)],
                p=[0.25, 0.40, 0.35],
            )
            connection_count += rng.poisson(12)
            request_rate += rng.gamma(2.0, 3.0)

        elif label == "ANOMALY":
            # Anomaly is deliberately heterogeneous rather than one fixed
            # combination of extreme values.
            anomaly_type = rng.choice(
                ["volume", "duration", "login", "rate", "subtle"],
                p=[0.22, 0.18, 0.18, 0.22, 0.20],
            )
            if anomaly_type == "volume":
                src_bytes *= rng.lognormal(0.8, 0.5)
                dst_bytes *= rng.lognormal(0.7, 0.5)
            elif anomaly_type == "duration":
                duration *= rng.lognormal(1.0, 0.6)
            elif anomaly_type == "login":
                failed_logins += rng.poisson(5)
            elif anomaly_type == "rate":
                request_rate += rng.gamma(3.0, 5.0)
                connection_count += rng.poisson(18)
            # The subtle subtype remains close to ordinary traffic.

        rows.append({
            "duration": float(max(duration, 0.001)),
            "src_bytes": float(max(src_bytes, 0)),
            "dst_bytes": float(max(dst_bytes, 0)),
            "failed_logins": int(failed_logins),
            "connection_count": int(connection_count),
            "request_rate": float(max(request_rate, 0)),
            "syn_error_rate": float(np.clip(syn_error_rate, 0, 1)),
            "service": str(rng.choice(
                ["web", "dns", "ssh", "database", "api"]
            )),
            "label": str(label),
        })

    return pd.DataFrame(rows, columns=FEATURE_COLUMNS + ["label"])


def save_dataset(
    path: str | Path,
    n_rows: int = 5000,
    random_state: int = 42
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    generate_dataset(n_rows, random_state).to_csv(path, index=False)
    return path


if __name__ == "__main__":
    from src.config import SYNTHETIC_DATA_PATH

    output = save_dataset(SYNTHETIC_DATA_PATH)
    print(f"Generated synthetic dataset: {output}")
    print(pd.read_csv(output).head().to_string(index=False))
