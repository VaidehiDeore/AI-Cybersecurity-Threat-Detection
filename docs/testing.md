# Testing Guide

Run `pytest -q` from the repository root. Then verify:
1. `python -m src.data_generator` creates `data/synthetic_network_traffic.csv`.
2. `python -m src.train` saves `models/threat_classifier.joblib` and `outputs/evaluation_metrics.json`.
3. `python -m src.visualize` creates the two plot images.
4. `python app.py` starts the local service at `127.0.0.1:5000`.
5. Visit `/api/health`, `/api/summary`, and `/api/alerts`.
6. Click **Run demo detection** on the dashboard and verify rows appear.

Generated models and outputs are ignored by Git by default; commit selected screenshots and documentation, not bulky transient artifacts.
