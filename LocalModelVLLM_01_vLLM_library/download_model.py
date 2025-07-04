#!/usr/bin/env python3
"""
Script to download a specified model from HuggingFace to a local directory.
Uses the `huggingface_hub` library.
"""

import os
import sys
import logging
import constants as c
from huggingface_hub import snapshot_download

# === Configuration ===
LOCAL_DIRECTORY = c.LOCAL_DIRECTORY

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def download_model(model_name: str, local_dir: str) -> bool:
    """Download model from HuggingFace Hub into local directory."""
    try:
        logger.info(f"📦 Starting download of '{model_name}' to '{local_dir}'")

        # Build HuggingFace-style directory name
        model_subdir = f"models--{model_name.replace('/', '--')}"
        target_path = os.path.join(local_dir, model_subdir)

        os.makedirs(target_path, exist_ok=True)

        # Download model snapshot
        snapshot_download(
            repo_id=model_name,
            local_dir=target_path,
            local_dir_use_symlinks=False,  # Safer on Windows
            resume_download=True
        )

        logger.info(f"✅ Successfully downloaded '{model_name}' to '{local_dir}'")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to download model: {e}")
        return False


def main():
    # Use default model name or take from CLI args
    model_name = c.MODEL_NAME
    if len(sys.argv) > 1:
        model_name = sys.argv[1]

    logger.info(f"📁 Target download directory: {LOCAL_DIRECTORY}")
    logger.info(f"🧠 Model to download: {model_name}")

    success = download_model(model_name, LOCAL_DIRECTORY)

    if success:
        logger.info("🎉 Model download completed successfully!")
        return 0
    else:
        logger.error("🚨 Model download failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())