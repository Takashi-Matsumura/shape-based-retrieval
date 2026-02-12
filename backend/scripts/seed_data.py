"""Seed the database with sample CAD files via the upload API."""

import logging
import sys
from pathlib import Path

import requests

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_samples import generate_all_samples

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def seed_data() -> None:
    """Generate sample STL files and upload them to the API."""
    # Check API health
    try:
        resp = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        resp.raise_for_status()
        logger.info("API is healthy: %s", resp.json())
    except requests.RequestException as e:
        logger.error("Cannot reach API at %s: %s", API_BASE_URL, e)
        sys.exit(1)

    # Generate sample files
    logger.info("Generating sample CAD files...")
    sample_files = generate_all_samples()
    logger.info("Generated %d sample files", len(sample_files))

    # Upload each file
    success_count = 0
    skip_count = 0
    fail_count = 0

    for file_path in sample_files:
        try:
            with open(file_path, "rb") as f:
                resp = requests.post(
                    f"{API_BASE_URL}/api/upload",
                    files={"file": (file_path.name, f, "application/octet-stream")},
                    timeout=120,
                )

            if resp.status_code == 200:
                data = resp.json()
                logger.info(
                    "Uploaded: %s (id=%d, vertices=%s, faces=%s)",
                    file_path.name,
                    data["id"],
                    data.get("vertex_count"),
                    data.get("face_count"),
                )
                success_count += 1
            elif resp.status_code == 409:
                logger.info("Skipped (duplicate): %s", file_path.name)
                skip_count += 1
            else:
                logger.warning(
                    "Failed to upload %s: %d %s",
                    file_path.name,
                    resp.status_code,
                    resp.text,
                )
                fail_count += 1

        except requests.RequestException as e:
            logger.error("Error uploading %s: %s", file_path.name, e)
            fail_count += 1

    logger.info(
        "Seeding complete: %d uploaded, %d skipped, %d failed (total: %d)",
        success_count,
        skip_count,
        fail_count,
        len(sample_files),
    )


if __name__ == "__main__":
    seed_data()
