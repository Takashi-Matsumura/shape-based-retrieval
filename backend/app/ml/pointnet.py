"""Simplified PointNet model for 3D point cloud feature extraction."""

import logging

import torch
import torch.nn as nn

from app.config import POINTNET_OUTPUT_DIM, POINTNET_SEED, POINTNET_WEIGHTS_PATH

logger = logging.getLogger(__name__)


class SimplePointNet(nn.Module):
    """Lightweight PointNet for extracting global features from point clouds.

    Architecture:
        Shared MLP: 3 -> 64 -> 128 -> 256
        Max Pooling over all points
        FC: 256 -> output_dim
    """

    def __init__(self, output_dim: int = POINTNET_OUTPUT_DIM) -> None:
        super().__init__()
        self.shared_mlp = nn.Sequential(
            nn.Linear(3, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
        )
        self.fc = nn.Sequential(
            nn.Linear(256, output_dim),
            nn.BatchNorm1d(output_dim),
        )
        self.output_dim = output_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Point cloud tensor of shape (batch, n_points, 3).

        Returns:
            Global feature vector of shape (batch, output_dim).
        """
        batch_size, n_points, _ = x.shape

        # Reshape to apply shared MLP per-point: (batch * n_points, 3)
        x = x.reshape(-1, 3)
        x = self.shared_mlp(x)

        # Reshape back: (batch, n_points, 256)
        x = x.reshape(batch_size, n_points, 256)

        # Max pooling over points: (batch, 256)
        x = x.max(dim=1)[0]

        # Final FC layer: (batch, output_dim)
        x = self.fc(x)
        return x


def load_or_create_model() -> SimplePointNet:
    """Load existing weights or create a new model with fixed random seed.

    The model weights are initialized once with a fixed seed and saved.
    Subsequent calls load the same weights to ensure consistent feature extraction.

    Returns:
        A SimplePointNet model in evaluation mode.
    """
    model = SimplePointNet(output_dim=POINTNET_OUTPUT_DIM)

    if POINTNET_WEIGHTS_PATH.exists():
        logger.info("Loading PointNet weights from %s", POINTNET_WEIGHTS_PATH)
        state_dict = torch.load(POINTNET_WEIGHTS_PATH, map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict)
    else:
        logger.info("Initializing PointNet with fixed seed %d", POINTNET_SEED)
        torch.manual_seed(POINTNET_SEED)
        model = SimplePointNet(output_dim=POINTNET_OUTPUT_DIM)
        POINTNET_WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), POINTNET_WEIGHTS_PATH)
        logger.info("Saved PointNet weights to %s", POINTNET_WEIGHTS_PATH)

    model.eval()
    return model
