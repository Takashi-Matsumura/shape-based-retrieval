"""Feature extraction using ONNX Runtime (no PyTorch dependency)."""

import logging

import numpy as np
import onnxruntime as ort

from .config import ONNX_MODEL_PATH, POINTNET_NUM_POINTS

logger = logging.getLogger(__name__)

# Singleton ONNX session
_session: ort.InferenceSession | None = None


def get_session() -> ort.InferenceSession:
    """Get the global ONNX inference session, creating it if needed."""
    global _session
    if _session is None:
        logger.info("Loading ONNX model from %s", ONNX_MODEL_PATH)
        _session = ort.InferenceSession(
            str(ONNX_MODEL_PATH),
            providers=["CPUExecutionProvider"],
        )
    return _session


def extract_features(point_cloud: np.ndarray) -> np.ndarray:
    """Extract a normalized feature vector from a point cloud.

    Args:
        point_cloud: Array of shape (n_points, 3).

    Returns:
        L2-normalized feature vector of shape (256,).
    """
    session = get_session()

    # Adjust point count to match model expectation
    n = len(point_cloud)
    if n != POINTNET_NUM_POINTS:
        if n > POINTNET_NUM_POINTS:
            indices = np.random.choice(n, POINTNET_NUM_POINTS, replace=False)
        else:
            indices = np.random.choice(n, POINTNET_NUM_POINTS, replace=True)
        point_cloud = point_cloud[indices]

    # Run inference: (1, 2048, 3) -> (1, 256)
    input_data = point_cloud.astype(np.float32).reshape(1, POINTNET_NUM_POINTS, 3)
    features = session.run(None, {"point_cloud": input_data})[0]

    # L2 normalize
    features = features.squeeze(0)
    norm = np.linalg.norm(features)
    if norm > 1e-8:
        features = features / norm

    return features
