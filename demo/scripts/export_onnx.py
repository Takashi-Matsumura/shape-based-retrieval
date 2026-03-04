"""Export PointNet model from PyTorch to ONNX format.

Requires PyTorch (dev dependency). Run once to generate data/pointnet.onnx.
"""

import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

DEMO_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = DEMO_DIR.parent

# Constants (must match backend/app/config.py)
POINTNET_OUTPUT_DIM = 256
POINTNET_NUM_POINTS = 2048
POINTNET_SEED = 42

OUTPUT_PATH = DEMO_DIR / "data" / "pointnet.onnx"
WEIGHTS_PATH = PROJECT_ROOT / "backend" / "data" / "pointnet_weights.pt"


class SimplePointNet(nn.Module):
    """Lightweight PointNet (copied from backend/app/ml/pointnet.py)."""

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
        batch_size, n_points, _ = x.shape
        x = x.reshape(-1, 3)
        x = self.shared_mlp(x)
        x = x.reshape(batch_size, n_points, 256)
        x = x.max(dim=1)[0]
        x = self.fc(x)
        return x


def export_onnx() -> None:
    """Export SimplePointNet to ONNX and verify output consistency."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Load or create model
    model = SimplePointNet(output_dim=POINTNET_OUTPUT_DIM)
    if WEIGHTS_PATH.exists():
        print(f"Loading existing weights from {WEIGHTS_PATH}")
        state_dict = torch.load(WEIGHTS_PATH, map_location="cpu", weights_only=True)
        model.load_state_dict(state_dict)
    else:
        print(f"No weights found. Initializing with seed={POINTNET_SEED}")
        torch.manual_seed(POINTNET_SEED)
        model = SimplePointNet(output_dim=POINTNET_OUTPUT_DIM)
        # Save weights for future use
        WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), WEIGHTS_PATH)
        print(f"Saved weights to {WEIGHTS_PATH}")

    model.eval()

    # Export to ONNX
    dummy_input = torch.randn(1, POINTNET_NUM_POINTS, 3)
    print(f"Exporting to ONNX: {OUTPUT_PATH}")
    torch.onnx.export(
        model,
        dummy_input,
        str(OUTPUT_PATH),
        input_names=["point_cloud"],
        output_names=["features"],
        dynamic_axes=None,
        opset_version=17,
    )
    print(f"ONNX model saved: {OUTPUT_PATH} ({OUTPUT_PATH.stat().st_size / 1024:.1f} KB)")

    # Verify ONNX output matches PyTorch
    import onnxruntime as ort

    session = ort.InferenceSession(str(OUTPUT_PATH))
    np.random.seed(0)
    test_input = np.random.randn(1, POINTNET_NUM_POINTS, 3).astype(np.float32)

    with torch.no_grad():
        pt_output = model(torch.from_numpy(test_input)).numpy()

    onnx_output = session.run(None, {"point_cloud": test_input})[0]

    max_diff = np.max(np.abs(pt_output - onnx_output))
    print(f"Max difference between PyTorch and ONNX: {max_diff:.2e}")
    assert max_diff < 1e-5, f"Output mismatch! Max diff: {max_diff}"
    print("Verification passed: PyTorch and ONNX outputs match.")


if __name__ == "__main__":
    export_onnx()
