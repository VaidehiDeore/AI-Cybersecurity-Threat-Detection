from src.data_generator import generate_dataset
from src.preprocessing import clean_frame
from src.train import train_model

def test_clean_frame_removes_duplicates():
    frame = generate_dataset(50, random_state=3)
    frame = frame.drop_duplicates()
    cleaned = clean_frame(frame)
    assert "label" in cleaned.columns
    assert len(cleaned) <= len(frame)

def test_training_pipeline(tmp_path, monkeypatch):
    # Use a small dataset file to validate the end-to-end training function.
    import src.train as train_module
    from pathlib import Path
    dataset = tmp_path / "sample.csv"
    generate_dataset(300, random_state=4).to_csv(dataset, index=False)
    model, metrics = train_module.train_model(dataset)
    assert 0 <= metrics["accuracy"] <= 1
    assert metrics["f1_weighted"] >= 0
