# Architecture Notes

## Components
- `src/data_generator.py`: deterministic safe synthetic network-flow data.
- `src/preprocessing.py`: duplicate handling, target validation, imputation, scaling, and categorical encoding.
- `src/train.py`: stratified holdout split, Random Forest training, metrics, and serialized pipeline.
- `src/anomaly.py`: separate Isolation Forest model and anomaly scores.
- `src/detect.py`: model inference and transparent demo severity mapping.
- `app.py`: local Flask API, dataset summaries, traffic records, analytics, predictions, and demo alerts.
- `web/`: responsive light-theme SOC frontend with Overview, Live Monitor, Alert Center, and Analytics views.

## Data flow
Synthetic records -> cleaning -> train/test split -> preprocessing/model pipeline -> metrics/artifacts -> API inference -> dashboard pages.

## API endpoints
- `GET /api/health`: service and model status.
- `GET /api/summary`: dataset totals, class counts, model metrics.
- `GET /api/traffic`: recent synthetic traffic records.
- `GET /api/analytics`: class distribution, metrics, feature summaries.
- `GET /api/alerts`: predictions for safe demo records.
- `POST /api/predict`: predictions for a non-empty `records` JSON array.

## Scope boundary
No live packet capture or offensive traffic generation is included. All initial examples are synthetic records. Real datasets must be mapped to the project's feature schema and evaluated independently.
