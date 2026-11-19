from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "dataset" / "student_data.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "student_score_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"

FEATURES = [
    "study_hours",
    "attendance",
    "previous_score",
    "assignment_score",
    "sleep_hours",
    "extracurricular_hours",
]
TARGET = "final_score"


def train_model():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. Run: python generate_dataset.py"
        )

    data = pd.read_csv(DATA_PATH)
    required = FEATURES + [TARGET]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    X = data[FEATURES]
    y = data[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=180,
        max_depth=12,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = {
        "rows": int(len(data)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "mae": round(float(mean_absolute_error(y_test, predictions)), 2),
        "rmse": round(float(mean_squared_error(y_test, predictions) ** 0.5), 2),
        "r2": round(float(r2_score(y_test, predictions)), 3),
        "features": FEATURES,
        "algorithm": "Random Forest Regressor",
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("Model trained and saved.")
    print(json.dumps(metrics, indent=2))
    return metrics


def ensure_model():
    if not MODEL_PATH.exists() or not METRICS_PATH.exists():
        return train_model()
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    train_model()
