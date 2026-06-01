# Neerraa — Groundwater Risk Intelligence System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-orange)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.0-red)](https://xgboost.ai/)


Confidence-Aware Groundwater Quality Assessment using XGBoost, Spatial Intelligence, and BIS IS 10500:2012 Standards.

🌐 Live Demo: https://neerraa.streamlit.app/
<img width="1919" height="959" alt="Screenshot 2026-06-01 143718" src="https://github.com/user-attachments/assets/880936a6-9eff-4c92-a41f-5f559b0ee3e2" />
*Interactive groundwater risk assessment platform supporting ML, Spatial, and Hybrid prediction modes.*
## Assessment Modes

| Mode | Input | Purpose |
|--------|--------|--------|
| ML | Water chemistry values | Predict risk using trained XGBoost model |
| Spatial | Latitude & Longitude | Estimate groundwater quality from location |
| Hybrid | Chemistry + Location | Combine both sources for maximum reliability |
---
## Why Neerraa?

Groundwater testing is often expensive, infrequent, and geographically sparse.

Neerraa helps users assess groundwater safety through:

- ML-based prediction from laboratory chemistry
- Spatial estimation from geographic coordinates
- Hybrid decision logic combining both approaches
- BIS IS 10500:2012 regulatory interpretation
- Explainable risk reports and treatment recommendations

Unlike traditional water-quality tools, Neerraa can provide assessments even when complete laboratory measurements are unavailable.
## At a Glance

| Metric | Value |
|----------|----------|
| Training Samples | ~14,500 |
| Algorithm | XGBoost |
| Macro F1 | 0.97 |
| Assessment Modes | 3 |
| Deployment | Live |
| Backend | FastAPI |
| Frontend | Streamlit |
## Key Features

✅ XGBoost-based groundwater risk prediction

✅ Spatial groundwater estimation using coordinates

✅ Hybrid confidence-aware inference engine

✅ Contaminant-level health risk explanations

✅ BIS IS 10500:2012 compliance interpretation

✅ FastAPI backend + Streamlit frontend

✅ Live deployed application

---
## Model Performance

| Metric | Score |
|----------|----------|
| Algorithm | XGBoost |
| Macro F1 Score | 0.97 |
| Dataset Size | ~14,500 Samples |
| Standard | BIS IS 10500:2012 |
| Deployment | Live |

## System Architecture

The platform combines machine learning, spatial intelligence, and regulatory rule-based reasoning into a unified groundwater decision-support pipeline.
<img width="706" height="763" alt="image" src="https://github.com/user-attachments/assets/647c7a3e-ed53-47ed-811e-d1b577245f44" />

## Architecture Overview
- `preprocessing/`: data cleaning pipeline for CGWB source CSV
- `notebooks/`: exploratory analysis, modeling, and integration notebooks
- `models/ml/`: serialized XGBoost classifier and scaler
- `outputs/spatial_predictions/`: serialized spatial estimator model
- `deploy/`: FastAPI backend and prediction service
- `frontend.py`: Streamlit user interface that calls the backend

## Tech Stack
- Python 3.11+
- Streamlit for UI
- FastAPI for backend API
- XGBoost and scikit-learn for ML inference
- Pandas / NumPy for data processing
- Joblib for model serialization
- Matplotlib / Seaborn for visualization

## Folder Structure
```text
├── assets/                     # Visual assets and UI screenshots
├── data/                       # Raw, cleaned, and processed datasets
│   ├── raw/
│   ├── cleaned/
│   └── processed/
├── deploy/                     # Backend API service and deployment helpers
│   ├── app.py
│   └── risk_predictor.py
├── models/                     # Saved ML/spatial artifacts and reference data
│   ├── ml/
│   └── spatial/
├── notebooks/                  # Analysis and training notebooks
├── outputs/                    # Generated model outputs and integration metadata
├── preprocessing/              # Data cleaning script and report
└── frontend.py                 # Streamlit app for interactive assessment
```

## Workflow / System Flow
1. Preprocess raw CGWB groundwater data with `preprocessing/preprocess_groundwater_data.py`
2. Use notebooks to standardize data, generate labels, train models, and serialize artifacts
3. Start the backend API from `deploy/app.py`
4. Launch `frontend.py` to run the Streamlit interface
5. Use ML-only, spatial-only, or hybrid assessment modes for prediction

## Installation
```powershell
cd c:\groundwater_risk_assessment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables
- None required by default for the current implementation.
- `frontend.py` currently uses a hardcoded API endpoint. For local development, update `API_URL` in `frontend.py` to `http://127.0.0.1:8000`.

## Usage Instructions
### Run the backend
```powershell
uvicorn deploy.app:app --reload
```

### Run the frontend
```powershell
streamlit run frontend.py
```

### Use cases
- `ML only`: enter measured chemistry values
- `Spatial only`: enter latitude and longitude only
- `Hybrid`: combine location and chemistry for source-aware inference

## API Setup
### Health check
`GET /health`

### Standards reference
`GET /standards`

### Prediction endpoint
`POST /predict`

#### Supported request payloads
- ML only: `{ "chemistry": { ... } }`
- Spatial only: `{ "latitude": 12.97, "longitude": 77.59 }`
- Hybrid: `{ "latitude": 12.97, "longitude": 77.59, "chemistry": { ... } }`

#### Example ML request
```json
{
  "chemistry": {
    "pH": 7.3,
    "NO3": 35,
    "F_mgL": 0.7,
    "Cl_mgL": 190,
    "SO4": 95,
    "Ca_mgL": 55,
    "Mg_mgL": 22,
    "Na_mgL": 130,
    "K_mgL": 5
  }
}
```

## Deployment Instructions
### Local development
1. Install dependencies
2. Start backend: `uvicorn deploy.app:app --reload`
3. Start UI: `streamlit run frontend.py`

### Production-ready notes
- Backend loads serialized models from `models/ml/` and `outputs/spatial_predictions/`
- Add a `Dockerfile` for containerized deployment
- Use a managed web service or cloud deployment platform
- Ensure model artifact paths are available in the deployment environment

## Screenshots
Visual examples are available in `assets/Interface/`:
### Dashboard Overview

Interactive interface supporting:

- ML Prediction
- Spatial Prediction
- Hybrid Assessment
<img width="1919" height="959" alt="Screenshot 2026-06-01 143718" src="https://github.com/user-attachments/assets/f40d4fd1-c1c6-4ae6-b6f5-5f043289a7fe" />

### ML-Based Assessment

Users enter groundwater chemistry values and receive a risk prediction with confidence scores.
<img width="1919" height="911" alt="Screenshot 2026-06-01 143733" src="https://github.com/user-attachments/assets/edf5ba93-9a92-48d2-9024-465b014a5109" />

### Spatial Groundwater Estimation

Risk estimation using only latitude and longitude coordinates.
<img width="1919" height="794" alt="Screenshot 2026-06-01 143751" src="https://github.com/user-attachments/assets/38b9e452-7420-4bb9-a2b8-ebf216d69b3b" />
<img width="1919" height="913" alt="Screenshot 2026-06-01 143803" src="https://github.com/user-attachments/assets/6d87c36b-83c6-4a5f-85a2-e12b805f8f9c" />
### Hybrid Intelligence Engine

Combines chemistry measurements and location context to produce the most reliable assessment.
<img width="1919" height="894" alt="Screenshot 2026-06-01 143849" src="https://github.com/user-attachments/assets/af978fc2-d8e8-44fa-a534-0e94c830e971" />
<img width="1919" height="908" alt="Screenshot 2026-06-01 143905" src="https://github.com/user-attachments/assets/7baa2b2d-16d8-4cec-9f1d-98ca918c4454" />
### Contaminant-Level Explanations

For every exceeded parameter:

- Cause
- Health Risk
- Corrective Action

are generated automatically.
<img width="1919" height="911" alt="Screenshot 2026-06-01 143923" src="https://github.com/user-attachments/assets/10ebb63e-0810-451b-9ee6-edeff7e5d1c9" />

<img width="1917" height="913" alt="Screenshot 2026-06-01 143952" src="https://github.com/user-attachments/assets/a9cffa4b-0b1c-4d36-bcc4-b13def004d45" />
<img width="1919" height="905" alt="Screenshot 2026-06-01 143939" src="https://github.com/user-attachments/assets/410ce705-d8f0-426e-b99d-d735fbc58db2" />


## Project Impact

Neerraa demonstrates how machine learning, spatial intelligence, and regulatory standards can be combined into a practical groundwater decision-support platform.

The system enables water quality assessment even when laboratory measurements are incomplete, making it useful for early-stage screening and decision support.

## Future Improvements
- Add a `Dockerfile` and container deployment workflow
- Introduce a config file / `.env` support for backend/frontend endpoints
- Add end-to-end tests for API and UI logic
- Improve spatial modeling with kriging or GWR
- Add interactive map visualization for risk heatmaps
- Implement a versioned model registry and deployment pipeline


