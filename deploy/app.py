"""
Groundwater Risk Assessment API
=================================
Confidence-aware risk prediction using ML + Spatial modes.
BIS IS 10500:2012 standards for drinking water quality.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
import warnings
import numpy as np
import joblib
import sys

warnings.filterwarnings("ignore", category=UserWarning)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from spatial.spatial_models import SpatialParameterEstimator
from deploy.risk_predictor import ConfidenceAwareRiskPredictor

# ============================================================
# BIS IS 10500:2012 STANDARDS
# ============================================================
BIS_STANDARDS = {
    "pH":      {"limit": "6.5 – 8.5", "unit": "",      "max": 8.5, "min": 6.5},
    "NO3":     {"limit": "<= 45",      "unit": "mg/L",  "max": 45},
    "F_mgL":   {"limit": "<= 1.5",     "unit": "mg/L",  "max": 1.5},
    "Cl_mgL":  {"limit": "<= 250",     "unit": "mg/L",  "max": 250},
    "SO4":     {"limit": "<= 200",     "unit": "mg/L",  "max": 200},
    "Ca_mgL":  {"limit": "<= 75",      "unit": "mg/L",  "max": 75},
    "Mg_mgL":  {"limit": "<= 30",      "unit": "mg/L",  "max": 30},
    "Na_mgL":  {"limit": "<= 200",     "unit": "mg/L",  "max": 200},
    "K_mgL":   {"limit": "<= 12",      "unit": "mg/L",  "max": 12},
    "Total_Hardness_mgL": {"limit": "<= 300", "unit": "mg/L", "max": 300},
}

FEATURE_IMPORTANCE = {
    "Cl_mgL": 0.2653, "NO3": 0.2447, "Mg_mgL": 0.1649,
    "Ca_mgL": 0.0944, "F_mgL": 0.0735, "Na_mgL": 0.0647,
    "SO4": 0.0418, "pH": 0.0405, "K_mgL": 0.0103,
}

FEATURE_ORDER = ["pH", "NO3", "F_mgL", "Cl_mgL", "SO4",
                 "Ca_mgL", "Mg_mgL", "Na_mgL", "K_mgL"]

LABELS = ["SAFE", "MODERATE", "HIGH"]

PARAM_NAMES = {
    "pH": "pH", "NO3": "Nitrate", "F_mgL": "Fluoride",
    "Cl_mgL": "Chloride", "SO4": "Sulphate", "Ca_mgL": "Calcium",
    "Mg_mgL": "Magnesium", "Na_mgL": "Sodium", "K_mgL": "Potassium",
    "Total_Hardness_mgL": "Total Hardness",
}

PARAM_ADVICE = {
    "NO3":   {"cause": "Agricultural fertilizers or sewage contamination.",
               "health": "Can cause methemoglobinemia (blue baby syndrome) in infants.",
               "action": "Use RO filtration. Do NOT boil — boiling concentrates nitrate."},
    "F_mgL": {"cause": "Naturally occurring in certain rock formations.",
               "health": "Long-term exposure causes dental and skeletal fluorosis.",
               "action": "Use defluoridation filter (Nalgonda technique) or RO system."},
    "Cl_mgL":{"cause": "Saltwater intrusion or industrial discharge.",
               "health": "Causes salty taste; harmful for hypertensive patients.",
               "action": "Unsuitable for drinking. Use RO or seek alternate supply."},
    "SO4":   {"cause": "Geological sources or industrial runoff.",
               "health": "Can cause laxative effects at high levels.",
               "action": "Dilute with clean water or use RO treatment."},
    "pH":    {"cause": "Water is too acidic or too alkaline.",
               "health": "Corrosive water leaches heavy metals from pipes.",
               "action": "Use pH-correcting filter. Acidic water needs neutralization."},
    "Ca_mgL":{"cause": "High calcium contributing to water hardness.",
               "health": "Not harmful; causes scaling in pipes and appliances.",
               "action": "Water softener or RO system recommended."},
    "Mg_mgL":{"cause": "High magnesium contributing to water hardness.",
               "health": "Very high levels may have a laxative effect.",
               "action": "Water softener recommended."},
    "Na_mgL":{"cause": "Saltwater intrusion or industrial contamination.",
               "health": "Risky for people with hypertension or kidney disease.",
               "action": "RO filtration removes sodium effectively."},
    "K_mgL": {"cause": "Elevated potassium — may indicate pollution.",
               "health": "May affect kidney function at very high levels.",
               "action": "RO filtration reduces potassium. Further testing advised."},
    "Total_Hardness_mgL": {"cause": "High combined calcium and magnesium.",
               "health": "Not directly harmful; associated with kidney stones.",
               "action": "Water softener or RO recommended."},
}


# ============================================================
# UTILITIES
# ============================================================
def to_python(obj):
    if isinstance(obj, dict):
        return {k: to_python(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_python(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    return obj


def check_exceedances(parameters: dict) -> dict:
    exceedances = {}
    for param, value in parameters.items():
        if value is None or (isinstance(value, float) and np.isnan(value)):
            exceedances[param] = None
            continue
        std = BIS_STANDARDS.get(param)
        if not std:
            exceedances[param] = False
            continue
        if param == "pH":
            exceedances[param] = not (std["min"] <= value <= std["max"])
        else:
            exceedances[param] = value > std["max"]
    return exceedances


def build_parameter_summary(parameters: dict, exceedances: dict) -> list:
    rows = []
    for param, val in parameters.items():
        if val is None or (isinstance(val, float) and np.isnan(val)):
            continue
        std = BIS_STANDARDS.get(param, {})
        rows.append({
            "parameter": param,
            "name":      PARAM_NAMES.get(param, param),
            "value":     round(val, 3),
            "unit":      std.get("unit", ""),
            "bis_limit": std.get("limit", "—"),
            "status":    "EXCEEDED" if exceedances.get(param) is True
                         else ("OK" if exceedances.get(param) is False else "N/A"),
        })
    return rows


def generate_explanation(parameters, exceedances, risk_label,
                         method="ML", ml_probabilities=None):
    exceeded   = [p for p, v in exceedances.items() if v is True]
    safe_count = sum(1 for v in exceedances.values() if v is False)

    if risk_label == "SAFE":
        summary = "All parameters are within BIS IS 10500:2012 safe limits. Water appears suitable for drinking."
    elif risk_label == "MODERATE":
        if exceeded:
            names = [PARAM_NAMES.get(p, p) for p in exceeded]
            summary = f"Moderate risk — {len(exceeded)} parameter(s) exceed safe limits: {', '.join(names)}."
        else:
            # ML detected MODERATE from combined chemical pattern — no single parameter crossed threshold
            # Find params closest to their limits to explain why
            close_params = []
            for p, val in parameters.items():
                if val is None: continue
                std = BIS_STANDARDS.get(p)
                if not std: continue
                if p == "pH":
                    ratio = max(abs(val - std["min"]), abs(val - std["max"])) / (std["max"] - std["min"])
                    if val < std["min"] + 1.5 or val > std["max"] - 1.0:
                        close_params.append(PARAM_NAMES.get(p, p))
                else:
                    if std["max"] > 0 and val / std["max"] >= 0.80:
                        close_params.append(PARAM_NAMES.get(p, p))
            if close_params:
                summary = (f"Moderate risk — no single parameter exceeds BIS limits, but the ML model "
                           f"detects a risky combined chemical pattern. Parameters near their limits: "
                           f"{', '.join(close_params[:3])}.")
            else:
                summary = ("Moderate risk — no individual parameter exceeds BIS IS 10500:2012 limits, "
                           "but the ML model detects a risky combined chemical signature in this sample.")
    elif risk_label == "HIGH":
        if exceeded:
            names = [PARAM_NAMES.get(p, p) for p in exceeded]
            summary = f"HIGH risk — {len(exceeded)} parameter(s) significantly exceed safe limits: {', '.join(names)}. Do NOT use without treatment."
        else:
            summary = ("HIGH risk — the ML model detects a severely unsafe combined chemical pattern, "
                       "even though individual parameters may appear borderline. Do NOT use without treatment.")
    else:
        summary = "Insufficient spatial data for a confident assessment at this location."

    exceeded_details = []
    for param in exceeded:
        val = parameters.get(param)
        std = BIS_STANDARDS.get(param, {})
        adv = PARAM_ADVICE.get(param, {})
        exceeded_details.append({
            "parameter":   param,
            "name":        PARAM_NAMES.get(param, param),
            "value":       round(val, 3) if val is not None else None,
            "unit":        std.get("unit", ""),
            "bis_limit":   std.get("limit", "N/A"),
            "cause":       adv.get("cause", "Exceeds BIS drinking water standard."),
            "health_risk": adv.get("health", "May be harmful to health."),
            "action":      adv.get("action", "Consult a water quality expert."),
        })

    top_ml_factors = []
    if method in ("ML", "Hybrid") and parameters:
        scored = [(p, FEATURE_IMPORTANCE.get(p, 0)) for p in FEATURE_ORDER
                  if parameters.get(p) is not None]
        scored.sort(key=lambda x: x[1], reverse=True)
        for param, imp in scored[:3]:
            val = parameters.get(param)
            top_ml_factors.append({
                "parameter":  param,
                "name":       PARAM_NAMES.get(param, param),
                "value":      round(val, 3) if val is not None else None,
                "importance": round(imp * 100, 1),
                "exceeded":   exceedances.get(param, False),
            })

    probability_note = None
    if ml_probabilities:
        dominant = max(ml_probabilities, key=ml_probabilities.get)
        pct = round(ml_probabilities[dominant] * 100, 1)
        probability_note = f"Model is {pct}% confident this sample is {dominant}."

    if risk_label == "SAFE":
        overall_advice = ("Water quality appears acceptable. Regular testing every 6–12 months "
                         "is recommended to monitor for seasonal changes.")
    elif risk_label == "MODERATE":
        overall_advice = ("Treat water before drinking. RO filtration is advisable. "
                         "Avoid giving this water to infants or immunocompromised individuals.")
    else:
        overall_advice = ("Do NOT use this water for drinking or cooking without comprehensive treatment. "
                         "Seek an alternate water source immediately.")

    return {
        "summary":          summary,
        "exceeded_params":  exceeded_details,
        "top_ml_factors":   top_ml_factors,
        "probability_note": probability_note,
        "overall_advice":   overall_advice,
        "exceeded_count":   len(exceeded),
        "safe_count":       safe_count,
    }


def run_ml(chemistry: dict):
    x = np.array([[float(chemistry.get(f, 0.0)) for f in FEATURE_ORDER]])
    x_scaled = scaler.transform(x)
    probs = ml_model.predict_proba(x_scaled)[0]
    idx = int(np.argmax(probs))
    prob_dict = {LABELS[i]: float(probs[i]) for i in range(len(LABELS))}
    exceedances = check_exceedances(chemistry)
    return LABELS[idx], float(np.max(probs)), prob_dict, exceedances


# ============================================================
# LOAD MODELS
# ============================================================
ML_MODEL_PATH      = PROJECT_ROOT / "models/ml/best_risk_classifier.joblib"
SCALER_PATH        = PROJECT_ROOT / "models/ml/feature_scaler.joblib"
SPATIAL_MODEL_PATH = PROJECT_ROOT / "outputs/spatial_predictions/spatial_index_model.joblib"

ml_model       = joblib.load(ML_MODEL_PATH)
scaler         = joblib.load(SCALER_PATH)
spatial_bundle = joblib.load(SPATIAL_MODEL_PATH)
spatial_estimator: SpatialParameterEstimator = spatial_bundle["estimator"]
risk_predictor = ConfidenceAwareRiskPredictor(spatial_estimator)


# ============================================================
# APP
# ============================================================
app = FastAPI(
    title="Groundwater Risk Assessment DSS",
    version="2.0",
    description="Confidence-aware groundwater quality risk prediction (BIS IS 10500:2012)",
)


class PredictionRequest(BaseModel):
    latitude:  Optional[float] = None
    longitude: Optional[float] = None
    chemistry: Optional[Dict[str, float]] = None


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "version": "2.0", "model": "XGBoost (Macro F1=0.97)"}


@app.get("/standards", tags=["Reference"])
def get_standards():
    return {"source": "BIS IS 10500:2012", "standards": BIS_STANDARDS}


@app.post("/predict", tags=["Prediction"])
def predict(req: PredictionRequest):
    has_latlon = req.latitude is not None and req.longitude is not None
    has_chem   = bool(req.chemistry)

    if not has_latlon and not has_chem:
        raise HTTPException(
            status_code=400,
            detail="Provide 'chemistry' parameters and/or 'latitude'+'longitude'."
        )

    # --- CASE 1: ML ONLY ---
    if has_chem and not has_latlon:
        risk_label, confidence, prob_dict, exceedances = run_ml(req.chemistry)
        explanation = generate_explanation(
            req.chemistry, exceedances, risk_label,
            method="ML", ml_probabilities=prob_dict
        )
        return to_python({
            "method":            "ML",
            "risk_label":        risk_label,
            "confidence":        round(confidence, 4),
            "explanation":       explanation,
            "parameter_summary": build_parameter_summary(req.chemistry, exceedances),
            "metadata": {
                "probabilities": prob_dict,
                "model":         "XGBoost",
                "standards":     "BIS IS 10500:2012",
            }
        })

    # --- CASE 2: SPATIAL ONLY ---
    if has_latlon and not has_chem:
        spatial     = risk_predictor.predict_risk_with_confidence(req.latitude, req.longitude)
        parameters  = spatial.get("parameters", {})
        exceedances = spatial.get("exceedances", {})

        if spatial["risk_label"] == "UNKNOWN":
            return to_python({
                "method": "Spatial", "risk_label": "UNKNOWN", "confidence": 0.0,
                "explanation": {
                    "summary": "No reference stations found within 50 km of this location.",
                    "overall_advice": "Provide water chemistry parameters directly for ML prediction.",
                    "exceeded_params": [], "top_ml_factors": [],
                    "probability_note": None, "exceeded_count": 0, "safe_count": 0,
                },
                "parameter_summary": [],
                "metadata": spatial.get("metadata", {}),
            })

        explanation = generate_explanation(parameters, exceedances,
                                           spatial["risk_label"], method="Spatial")
        return to_python({
            "method":            "Spatial",
            "risk_label":        spatial["risk_label"],
            "confidence":        round(spatial["confidence"], 4),
            "explanation":       explanation,
            "parameter_summary": build_parameter_summary(parameters, exceedances),
            "metadata": {
                "neighbor_count":            spatial["metadata"].get("neighbor_count"),
                "mean_neighbor_distance_km": spatial["metadata"].get("mean_neighbor_distance_km"),
                "spatial_confidence":        spatial["metadata"].get("overall_confidence"),
                "note": "Parameters interpolated from nearest CGWB stations via IDW.",
                "standards": "BIS IS 10500:2012",
            }
        })

    # --- CASE 3: HYBRID ---
    spatial      = risk_predictor.predict_risk_with_confidence(req.latitude, req.longitude)
    spatial_conf = spatial.get("confidence", 0.0)

    x_vals = [req.chemistry.get(f) for f in FEATURE_ORDER]
    if not all(v is not None for v in x_vals):
        parameters  = spatial.get("parameters", {})
        exceedances = spatial.get("exceedances", {})
        explanation = generate_explanation(parameters, exceedances,
                                           spatial["risk_label"], method="Spatial")
        return to_python({
            "method": "Hybrid", "decision_source": "Spatial (incomplete chemistry)",
            "risk_label": spatial["risk_label"],
            "confidence": round(spatial_conf, 4),
            "explanation": explanation,
            "parameter_summary": build_parameter_summary(parameters, exceedances),
            "metadata": {"reason": "Chemistry incomplete; spatial used.", "standards": "BIS IS 10500:2012"}
        })

    risk_label_ml, ml_conf, prob_dict, exceedances = run_ml(req.chemistry)

    if ml_conf >= 0.8:
        decision_source, final_label, final_conf = "ML", risk_label_ml, ml_conf
    else:
        decision_source = "Spatial"
        final_label     = spatial.get("risk_label", risk_label_ml)
        final_conf      = spatial_conf

    explanation = generate_explanation(
        req.chemistry, exceedances, final_label,
        method="Hybrid", ml_probabilities=prob_dict
    )
    return to_python({
        "method":            "Hybrid",
        "decision_source":   decision_source,
        "risk_label":        final_label,
        "confidence":        round(final_conf, 4),
        "explanation":       explanation,
        "parameter_summary": build_parameter_summary(req.chemistry, exceedances),
        "metadata": {
            "ml_label":           risk_label_ml,
            "ml_confidence":      round(ml_conf, 4),
            "spatial_label":      spatial.get("risk_label", "N/A"),
            "spatial_confidence": round(spatial_conf, 4),
            "probabilities":      prob_dict,
            "standards":          "BIS IS 10500:2012",
        }
    })