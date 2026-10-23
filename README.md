# CycleScope — Bike Rental Demand Prediction

An Invoqe internship project prepared for Harshita Nayan. Predict hourly rental counts from calendar and weather conditions using real historical data. No API key is required.

## Run on Windows / VS Code

Install Python 3.11 or 3.12. Extract the ZIP first, then open the extracted `Invoqe_BikeDemandPrediction` folder in VS Code (the folder containing `app.py`). In Terminal → New Terminal, run:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Open the Local URL printed by Streamlit, normally http://localhost:8501. Keep the terminal running. Stop with Ctrl+C. These commands do not require activating PowerShell scripts.

The ZIP includes the real dataset, trained model and measured reports, so first launch does not require training or an API connection. Installing dependencies needs internet. On macOS/Linux use `.venv/bin/python` in place of `.venv\Scripts\python`.

If `python` is unavailable on Windows, try `py -3.11` for the first command. If the model fails to load due to a dependency version, install the requirements and retrain it:

```powershell
.venv\Scripts\python train.py
.venv\Scripts\python -m streamlit run app.py
```

## What the application does

- Predict demand: date, hour, holiday, temperature, humidity, wind and weather form; estimated hourly total displayed after submission.
- Explore data: working-day hourly patterns, monthly averages, original records and missing-value counts.
- Model results: baseline and three model families, CV and test metrics, actual versus predicted chart, tuning settings and downloadable predictions.

## Dataset and attribution

Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5W894

Source: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset
Download: https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip
License: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/

Original Capital Bikeshare hourly observations from Washington, DC, 2011–2012. The downloaded `hour.csv` has 17,379 rows; the repository page's metadata count differs, so this project reports the actual loaded file count. Original `Readme.txt` and `day.csv` are retained for provenance. Data are attributed to their source; this project does not claim to have collected them. The dataset is unchanged; feature transformations are performed in code.

## Methodology

1. Read the CSV; check missing values, remove duplicate rows and invalid missing target/date/hour records, sort by timestamp and reject duplicate timestamps. Original data have no missing values; no cleaning problems are invented.
2. Inspect hourly and monthly averages. All-data EDA is descriptive; the test targets are not used for model selection.
3. Use calendar and weather features. Exclude `casual` and `registered` because their sum equals `cnt` (target leakage). Exclude `instant` and raw `dteday`. Omit `atemp` as a redundant input and `season` because month already supplies seasonal information.
4. Engineer sine/cosine hour and month features. Fit imputation/scaling only within each training fold. Linear regression uses scaling; trees do not require it.
5. Hold out the final 20% of distinct dates. Tune/select on the preceding dates using three expanding-window TimeSeriesSplit folds with a 24-row gap. The series has some missing hours, so the gap means 24 observations, not necessarily exactly 24 clock hours.
6. Compare mean baseline, Linear Regression, Random Forest, and histogram Gradient Boosting. Tune forest minimum leaf size and boosting leaf count/L2 regularization. Pick the lowest development CV MAE, refit on development data, and only then evaluate on the final test period.
7. Clip all model predictions to zero for reporting and serving. GridSearchCV uses raw model MAE for selection; this distinction can affect the linear baseline at negative predictions.

The saved model remains trained on development data, so the included held-out results correspond to that exact model. No post-test refit is silently performed.

## Measured results

| Model | Development CV MAE | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|
| Mean baseline | 139.81 | 174.97 | 232.56 | -0.112 |
| Linear Regression | 127.98 | 123.97 | 167.84 | 0.421 |
| Random Forest | 56.64 | 50.81 | 76.68 | 0.879 |
| Gradient Boosting | 50.96 | 42.73 | 65.16 | 0.913 |

Selected model: Gradient Boosting, based on development CV, before evaluating the test period. MAE is rentals/hour, not percentage accuracy. RMSE emphasizes larger errors. R² is not an accuracy percentage. Reproducing under different library versions may change values slightly.

## Limitations

This is an educational historical conditional-demand model, not a current operational service. The interface deliberately restricts dates to 2011–2012. Observed weather inputs are used; a real deployment predicting future demand would need weather forecasts and prospective validation. Calendar/year trends, geography, seasonal coverage and rare conditions limit generalization. Weather category 4 is extremely rare and is excluded from manual input choices. Model error varies across hours; MAE is not a confidence interval. Associations do not establish causation. Totals refer to the whole recorded system, not a station or fleet size.

## Files

- `app.py`: Streamlit interface.
- `model.py`: shared loading and feature transformations.
- `train.py`: chronological evaluation and tuning.
- `check_app.py`: smoke check for rendering and prediction submission.
- `data/`: source data and original documentation.
- `artifacts/model.joblib`: trained development model.
- `artifacts/metrics.csv`, `report.json`, `test_predictions.csv`, `eda.png`: actual results and analysis.

Only load the included trusted joblib artifact or one you trained yourself.

## Verify and reproduce

```powershell
.venv\Scripts\python train.py
.venv\Scripts\python check_app.py
```

Training may take several minutes depending on your computer. It overwrites the generated model and reports with fresh measured results.






