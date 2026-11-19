"""Regenerate a clearly synthetic demo dataset for learning and testing."""
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "dataset" / "student_data.csv"

def main():
    rng = np.random.default_rng(42)
    n = 1200
    study_hours = rng.uniform(0.5, 8.0, n).round(1)
    attendance = rng.uniform(40, 100, n).round(1)
    previous_score = rng.uniform(25, 98, n).round(1)
    assignment_score = rng.uniform(20, 100, n).round(1)
    sleep_hours = rng.uniform(4, 9, n).round(1)
    extracurricular_hours = rng.uniform(0, 4, n).round(1)
    noise = rng.normal(0, 7, n)
    final_score = (
        8 + study_hours * 4.0 + attendance * 0.19 +
        previous_score * 0.23 + assignment_score * 0.20 +
        sleep_hours * 1.1 - extracurricular_hours * 1.0 + noise
    )
    final_score = np.clip(final_score, 0, 100).round(1)
    data = pd.DataFrame({
        "study_hours": study_hours,
        "attendance": attendance,
        "previous_score": previous_score,
        "assignment_score": assignment_score,
        "sleep_hours": sleep_hours,
        "extracurricular_hours": extracurricular_hours,
        "final_score": final_score,
    })
    OUT_PATH.parent.mkdir(exist_ok=True)
    data.to_csv(OUT_PATH, index=False)
    print(f"Saved {len(data)} synthetic student records to {OUT_PATH}")

if __name__ == "__main__":
    main()
