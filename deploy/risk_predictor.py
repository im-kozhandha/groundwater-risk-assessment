
import numpy as np

class ConfidenceAwareRiskPredictor:
    """
    Confidence-aware groundwater risk predictor.

    Uses spatially estimated hydrochemical parameters
    and BIS drinking water standards to classify risk.
    """

    def __init__(self, spatial_estimator):
        """
        Parameters
        ----------
        spatial_estimator : SpatialParameterEstimator
            Pre-trained spatial estimator loaded from joblib
        """
        self.estimator = spatial_estimator

        # BIS drinking water standards (IS 10500:2012)
        self.standards = {
            'pH': {'min': 6.5, 'max': 8.5},
            'NO3': 45,
            'F_mgL': 1.5,
            'Cl_mgL': 250,
            'SO4': 200
        }

    def predict_risk_with_confidence(self, lat, lon, k=5, max_dist_km=50):
        """
        Predict groundwater risk and confidence for a location.

        Returns
        -------
        dict with:
            - risk_label
            - risk_score
            - confidence
            - parameters
            - exceedances
            - metadata
        """

        estimation = self.estimator.estimate_parameters(
            lat=lat,
            lon=lon,
            k=k,
            max_dist_km=max_dist_km
        )

        # Handle no-neighbor case
        if estimation["neighbor_count"] == 0:
            return {
                "risk_label": "UNKNOWN",
                "risk_score": None,
                "confidence": 0.0,
                "parameters": {},
                "exceedances": {},
                "metadata": {
                    "status": "NO_NEIGHBORS",
                    "neighbor_count": 0
                }
            }

        parameters = estimation["parameters"]
        confidence_map = estimation.get("confidence", {})
        exceedances = {}

        exceedance_count = 0
        valid_params = 0

        for param, value in parameters.items():
            if value is None or np.isnan(value):
                exceedances[param] = None
                continue

            valid_params += 1
            std = self.standards.get(param)
            exceeds = False

            if std:
                if param == "pH":
                    if value < std["min"] or value > std["max"]:
                        exceeds = True
                else:
                    if value > std:
                        exceeds = True

            exceedances[param] = exceeds
            if exceeds:
                exceedance_count += 1

        # Risk classification
        if exceedance_count == 0:
            risk_label = "SAFE"
        elif exceedance_count <= 2:
            risk_label = "MODERATE"
        else:
            risk_label = "HIGH"

        # Confidence computation (aligned with Notebook 4)
        base_conf = estimation["metadata"].get("overall_confidence", 0.0)
        neighbor_factor = min(estimation["neighbor_count"] / 5, 1.0)
        availability_factor = (
            valid_params / len(self.estimator.parameter_columns)
            if self.estimator.parameter_columns else 0.0
        )

        mean_dist = estimation["neighbor_stats"].get(
            "mean_distance_km", max_dist_km
        )
        distance_factor = max(0.0, 1.0 - (mean_dist / (2 * max_dist_km)))

        confidence = (
            0.4 * base_conf +
            0.2 * neighbor_factor +
            0.2 * availability_factor +
            0.2 * distance_factor
        )

        confidence = float(np.clip(confidence, 0.0, 1.0))

        return {
            "risk_label": risk_label,
            "risk_score": exceedance_count,
            "confidence": confidence,
            "parameters": parameters,
            "exceedances": exceedances,
            "metadata": {
                "neighbor_count": estimation["neighbor_count"],
                "mean_neighbor_distance_km": mean_dist,
                "overall_confidence": base_conf
            }
        }

    def predict_batch(self, locations, k=5, max_dist_km=50):
        """
        Batch prediction helper.

        locations : list[(lat, lon)]
        """
        results = []
        for lat, lon in locations:
            r = self.predict_risk_with_confidence(lat, lon, k, max_dist_km)
            r["latitude"] = lat
            r["longitude"] = lon
            results.append(r)
        return results