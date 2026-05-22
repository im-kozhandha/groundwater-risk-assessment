"""
Spatial Models for Groundwater Risk Assessment
==============================================

This module provides reusable, serializable spatial inference components
for groundwater parameter estimation using nearest-neighbor search and
distance-weighted interpolation.

Extracted from Notebook 04 for:
- Reproducibility
- Joblib serialization
- Cross-notebook integration
- Deployment readiness

Author: Groundwater Risk Assessment Project
"""

import numpy as np
from sklearn.neighbors import BallTree
from math import radians
from datetime import datetime


# ------------------------------------------------------------------
# Utility: Haversine Distance (km)
# ------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2):
    """
    Compute Haversine distance between two points in kilometers.
    """
    R = 6371.0  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(
        radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )

    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


# ------------------------------------------------------------------
# Spatial Indexer
# ------------------------------------------------------------------
class SpatialIndexer:
    """
    Spatial index using BallTree with Haversine metric.
    """

    def __init__(self, coordinates):
        """
        Parameters
        ----------
        coordinates : array-like of shape (n_samples, 2)
            Latitude and Longitude in decimal degrees
        """
        self.coordinates_deg = np.array(coordinates)

        # Convert to radians for BallTree
        self.coordinates_rad = np.radians(self.coordinates_deg)

        self.tree = BallTree(
            self.coordinates_rad,
            metric="haversine"
        )

    def query(self, latitude, longitude, k=5):
        """
        Query nearest neighbors.

        Returns
        -------
        distances_km : ndarray
        indices : ndarray
        """
        point_rad = np.radians([[latitude, longitude]])
        distances, indices = self.tree.query(point_rad, k=k)

        # Convert radians to km
        distances_km = distances[0] * 6371.0
        return distances_km, indices[0]


# ------------------------------------------------------------------
# Spatial Parameter Estimator
# ------------------------------------------------------------------
class SpatialParameterEstimator:
    """
    Distance-weighted spatial interpolation with confidence estimation.
    """

    def __init__(self, spatial_indexer, data, parameter_columns):
        """
        Parameters
        ----------
        spatial_indexer : SpatialIndexer
        data : pandas.DataFrame
            Must contain Latitude, Longitude and parameter columns
        parameter_columns : list[str]
            Hydrochemical parameters to estimate
        """
        self.indexer = spatial_indexer
        self.data = data.reset_index(drop=True)
        self.parameter_columns = parameter_columns

        self.created_at = datetime.now().isoformat()

    def estimate_parameters(self, lat, lon, k=5, max_dist_km=50):
        """
        Estimate parameters at a given location.

        Returns
        -------
        dict with:
          - parameters
          - neighbor_count
          - neighbor_stats
          - metadata
        """
        distances, indices = self.indexer.query(lat, lon, k=k)

        # Filter neighbors by distance
        mask = distances <= max_dist_km
        distances = distances[mask]
        indices = indices[mask]

        neighbor_count = len(indices)

        if neighbor_count == 0:
            return {
                "parameters": {},
                "neighbor_count": 0,
                "neighbor_stats": {},
                "metadata": {
                    "overall_confidence": 0.0,
                    "reason": "No neighbors within distance threshold"
                }
            }

        # Inverse distance weights
        weights = 1 / (distances + 1e-6)
        weights = weights / weights.sum()

        estimated_params = {}
        availability_scores = []

        for param in self.parameter_columns:
            values = self.data.loc[indices, param].values
            valid_mask = ~np.isnan(values)

            if valid_mask.sum() == 0:
                estimated_params[param] = np.nan
                availability_scores.append(0.0)
                continue

            weighted_value = np.sum(
                values[valid_mask] * weights[valid_mask]
            )
            estimated_params[param] = float(weighted_value)

            availability_scores.append(valid_mask.mean())

        # Confidence components
        distance_score = max(
            0.0,
            1.0 - (distances.mean() / max_dist_km)
        )
        neighbor_score = min(1.0, neighbor_count / k)
        availability_score = float(np.mean(availability_scores))

        overall_confidence = float(
            0.4 * distance_score
            + 0.3 * neighbor_score
            + 0.3 * availability_score
        )

        return {
            "parameters": estimated_params,
            "neighbor_count": neighbor_count,
            "neighbor_stats": {
                "mean_distance_km": float(distances.mean()),
                "min_distance_km": float(distances.min()),
                "max_distance_km": float(distances.max())
            },
            "metadata": {
                "overall_confidence": overall_confidence,
                "distance_score": distance_score,
                "neighbor_score": neighbor_score,
                "availability_score": availability_score,
                "method": "IDW + confidence weighting"
            }
        }
