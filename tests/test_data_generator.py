from src.data_generator import generate_dataset

def test_generator_shape_and_labels():
    frame = generate_dataset(200, random_state=1)
    assert len(frame) == 200
    assert {"label", "request_rate", "failed_logins", "service"}.issubset(frame.columns)
    assert set(frame["label"]).issubset({"NORMAL", "DOS", "BRUTE_FORCE", "ANOMALY"})
