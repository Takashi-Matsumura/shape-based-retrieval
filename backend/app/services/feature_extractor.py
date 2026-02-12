"""Feature extraction service using PointNet."""

import logging

import numpy as np
import torch

from app.config import POINTNET_NUM_POINTS
from app.ml.pointnet import SimplePointNet, load_or_create_model

logger = logging.getLogger(__name__)

# Global model instance (loaded once at startup)
_model: SimplePointNet | None = None


def get_model() -> SimplePointNet:
    """Get the global PointNet model instance, loading it if needed.

    Returns:
        The PointNet model in evaluation mode.
    """
    global _model
    if _model is None:
        _model = load_or_create_model()
    return _model


def extract_features(point_cloud: np.ndarray) -> list[float]:
    """Extract a feature vector from a point cloud using PointNet.

    Args:
        point_cloud: Array of shape (n_points, 3).

    Returns:
        Feature vector as a list of floats with length = POINTNET_OUTPUT_DIM.
    """
    model = get_model()

    # Ensure correct number of points
    if len(point_cloud) != POINTNET_NUM_POINTS:
        if len(point_cloud) > POINTNET_NUM_POINTS:
            indices = np.random.choice(len(point_cloud), POINTNET_NUM_POINTS, replace=False)
            point_cloud = point_cloud[indices]
        else:
            indices = np.random.choice(len(point_cloud), POINTNET_NUM_POINTS, replace=True)
            point_cloud = point_cloud[indices]

    # Convert to tensor: (1, n_points, 3)
    tensor = torch.from_numpy(point_cloud).float().unsqueeze(0)

    with torch.no_grad():
        features = model(tensor)

    # Normalize feature vector to unit length for cosine similarity
    features = features / (features.norm(dim=1, keepdim=True) + 1e-8)

    return features.squeeze(0).tolist()
