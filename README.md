# Student Performance Predictor

A beginner-friendly machine-learning semester project built with Python, Flask, scikit-learn, SQLite, HTML, CSS, and JavaScript.

## Features
- Predicts an estimated final score from six student inputs.
- Converts the estimated score into a simple performance band.
- Trains a Random Forest Regression model and reports MAE, RMSE, and R².
- Saves prediction history in a local SQLite database.
- Dashboard cards, recent predictions, a performance-distribution chart, history page, and project/methodology page.
- Input validation and a button to clear stored prediction history.

## Important limitation
The included `dataset/student_data.csv` is **synthetic demo data generated for this project**. It is not real student records, and model metrics from it do not establish real-world accuracy. For a research-quality submission, replace it with a permitted, documented real dataset and explain its source, limitations, and consent/privacy considerations. Do not use the output to make high-stakes decisions about real students.

## Requirements
- Python 3.10 or newer
- VS Code (recommended)
- Internet connection only if you want the optional Chart.js graph from its CDN; prediction functionality itself is local.

## Run in VS Code

### 1. Extract and open
Extract the ZIP, then in VS Code choose **File → Open Folder** and select `student-performance-predictor`.

### 2. Open terminal
Choose **Terminal → New Terminal**.

### 3. Create a virtual environment (recommended)
Windows PowerShell:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```
If activation is blocked, you can skip activation and use `.venv\Scripts\python.exe` for the following commands.

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install packages
Windows:
```powershell
py -m pip install -r requirements.txt
```
macOS/Linux:
```bash
python3 -m pip install -r requirements.txt
```

### 5. Train the ML model (first run)
```bash
python train_model.py
```
If the command above says the file is not found, use:
```bash
python ml_model.py
```
(The primary training file is `ml_model.py`; `python train_model.py` is also provided as a convenient alias.)
Expected: model and metrics are saved under `models/`.

### 6. Start the web application
```bash
python app.py
```
Open the local address printed in the terminal, usually:
http://127.0.0.1:5000

Stop the server with **Ctrl+C** in the terminal.

## Project structure
```text
student-performance-predictor/
├── app.py
├── ml_model.py
├── generate_dataset.py
├── requirements.txt
├── README.md
├── dataset/
│   └── student_data.csv
├── models/                 # model and metrics created after training
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── history.html
│   └── about.html
└── static/
    ├── style.css
    └── app.js
```

## How the ML works
1. The CSV file contains six input features and one target: `final_score`.
2. The dataset is split into 80% training and 20% testing data.
3. Random Forest Regressor learns relationships between features and scores.
4. MAE, RMSE, and R² are calculated on the held-out test set.
5. The model predicts a score from 0–100. A simple rule maps that score to a performance band:
   - 75–100: Excellent
   - 60–74.9: Good
   - 40–59.9: Needs Improvement
   - Below 40: At Risk

These bands are project-demo labels, not official academic classifications.

## Viva points
- **Why regression?** The target is a continuous numeric score.
- **Why Random Forest?** It combines many decision trees and can model non-linear relationships without feature scaling.
- **What is a feature?** An input variable such as attendance.
- **What is the target?** The final score the model learns to estimate.
- **What is MAE?** Average absolute difference between predicted and actual test scores; lower is better.
- **What is RMSE?** Square root of average squared error; it penalizes large errors more strongly.
- **What is R²?** A measure of how much target variation is explained on test data; closer to 1 is generally better.
- **Why split the data?** To evaluate performance on records not used for fitting the model.
- **What is SQLite?** A lightweight local database used here to store prediction history.

## Troubleshooting
- `python` not found: try `py` on Windows or `python3` on macOS/Linux.
- Module not found: activate the environment and run `python -m pip install -r requirements.txt`.
- Port 5000 busy: close the other app using it or change `app.run(debug=True, port=5001)` at the bottom of `app.py`.
- Model missing: run `python ml_model.py`.
