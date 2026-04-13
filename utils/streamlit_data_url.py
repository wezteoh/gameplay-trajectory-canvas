"""Encode RGB arrays as data URLs so ``st.image`` skips MediaFileManager (fewer orphan /media requests)."""

from __future__ import annotations

import base64
import io

import numpy as np
from PIL import Image


def np_rgb_to_jpeg_data_url(rgb: np.ndarray, *, quality: int = 90) -> str:
    """``rgb`` uint8 H×W×3 → ``data:image/jpeg;base64,...`` for Streamlit."""
    arr = np.asarray(rgb, dtype=np.uint8)
    if arr.ndim != 3 or arr.shape[2] != 3:
        raise ValueError(f"expected HxWx3 uint8 RGB, got shape {arr.shape}")
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG", quality=quality, optimize=True)
    b64 = base64.standard_b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"
