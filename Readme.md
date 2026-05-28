# Groundwater Risk Assessment DSS

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-orange)](https://streamlit.io/)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.0.0-red)](https://xgboost.ai/)


Confidence-aware groundwater quality decision support for drinking water safety using BIS IS 10500:2012, hybrid ML, and spatial interpolation.
NOW LIVE! : https://neerraa.streamlit.app/

## Overview
This repository implements a pilot decision support system for groundwater chemical risk assessment in India. It combines data preprocessing, machine learning classification, spatial interpolation, and an interactive Streamlit frontend backed by a FastAPI prediction service.

## Problem Statement
Groundwater quality monitoring is often fragmented, noisy, and geographically sparse. Decision-makers need a practical system to classify drinking-water risk, explain exceedances, and estimate water quality at unsampled locations.

## Solution
This project delivers a hybrid risk assessment pipeline:
- ML-based risk classification from laboratory chemistry values
- Spatial estimation via nearest-neighbor interpolation for location-only queries
- Hybrid decision logic that chooses the most confident prediction source
- Regulatory alignment with BIS IS 10500:2012 drinking water standards

## Features
- ML risk prediction with trained XGBoost classifier
- Location-based spatial risk estimation using IDW and confidence scoring
- Hybrid inference combining chemistry and coordinates
- Interactive Streamlit UI with explanation, advice, and parameter dashboards
- FastAPI backend with `/health`, `/standards`, and `/predict`
- Cleaned groundwater data pipeline and reproducible preprocessing
- Serialized model artifacts for deployment-ready inference

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
- `Screenshot 2026-05-23 004157.png`
- `Screenshot 2026-05-23 004136.png`
- `Screenshot 2026-05-23 004052.png`
- `Screenshot 2026-05-23 002718.png`

## Demo
- Local demo: start the backend and run `frontend.py`
- Remote endpoint: the current Streamlit UI points to `https://groundwater-risk-assessment.onrender.com` by default

## Future Improvements
- Add a `Dockerfile` and container deployment workflow
- Introduce a config file / `.env` support for backend/frontend endpoints
- Add end-to-end tests for API and UI logic
- Improve spatial modeling with kriging or GWR
- Add interactive map visualization for risk heatmaps
- Implement a versioned model registry and deployment pipeline

## Challenges Faced
- Cleaning noisy PDF-derived groundwater data with repeated header rows
- Correcting swapped latitude/longitude coordinates in the raw dataset
- Handling sparse hydrochemical observations while preserving extreme contamination cases
- Balancing standards-based exceedance logic with ML-derived risk classification
- Providing explainable predictions for multiple user entry modes

## Scalability Ideas
- Split API and UI into separate services for independent scaling
- Cache model responses and use vectorized batch prediction for bulk queries
- Store models and datasets in cloud object storage for large-scale deployment
- Add asynchronous request handling and rate limiting for production
- Migrate to a dedicated data service or geospatial database if dataset grows

## Contribution Guide
1. Fork the repository
2. Create a feature branch
3. Install dependencies locally
4. Open a pull request with a clear description

> Note: no license file is included in this repository. Add a `LICENSE` if you want to clarify reuse rights.

## Credits
- Groundwater data preprocessing and domain analysis: `preprocessing/preprocess_groundwater_data.py`
- Spatial confidence modeling: `spatial/spatial_models.py`
- Prediction logic and API: `deploy/app.py`, `deploy/risk_predictor.py`
- Interactive UI: `frontend.py`
