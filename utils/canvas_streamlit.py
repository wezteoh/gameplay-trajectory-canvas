"""
Wrap streamlit-drawable-canvas so the court background uses stable MediaFile coordinates.

The stock package registers backgrounds as ``drawable-canvas-bg-{md5}-{key}``. Each new
pixel buffer gets a new id, so Streamlit drops older files while the iframe can still
request them → ``MediaFileHandler: Missing file``. We register under one coordinate per
widget key so the manager replaces media in place for that slot.
"""

from __future__ import annotations

import numpy as np
import streamlit as st
import streamlit.elements.image as st_image
from PIL import Image

import streamlit_drawable_canvas as _sdc

_component_func = _sdc._component_func
_data_url_to_image = _sdc._data_url_to_image
_resize_img = _sdc._resize_img
CanvasResult = _sdc.CanvasResult


def gameplay_st_canvas(
    *,
    background_image: Image.Image,
    media_coordinate_key: str,
    fill_color: str = "#eee",
    stroke_width: int = 20,
    stroke_color: str = "black",
    update_streamlit: bool = True,
    height: int = 400,
    width: int = 600,
    drawing_mode: str = "freedraw",
    initial_drawing: dict | None = None,
    display_toolbar: bool = True,
    point_display_radius: int = 3,
    key: str | None = None,
) -> CanvasResult:
    """Same contract as ``streamlit_drawable_canvas.st_canvas`` with stable background media id."""
    bg = _resize_img(background_image.copy(), height, width)
    coord = f"gameplay-court-bg::{media_coordinate_key}"
    rel = st_image.image_to_url(bg, width, True, "RGB", "JPEG", coord)
    background_image_url = st._config.get_option("server.baseUrlPath") + rel
    background_color = ""

    initial_drawing = (
        {"version": "4.4.0"} if initial_drawing is None else initial_drawing
    )
    initial_drawing["background"] = background_color

    component_value = _component_func(
        fillColor=fill_color,
        strokeWidth=stroke_width,
        strokeColor=stroke_color,
        backgroundColor=background_color,
        backgroundImageURL=background_image_url,
        realtimeUpdateStreamlit=update_streamlit and (drawing_mode != "polygon"),
        canvasHeight=height,
        canvasWidth=width,
        drawingMode=drawing_mode,
        initialDrawing=initial_drawing,
        displayToolbar=display_toolbar,
        displayRadius=point_display_radius,
        key=key,
        default=None,
    )
    if component_value is None:
        return CanvasResult()

    return CanvasResult(
        np.asarray(_data_url_to_image(component_value["data"])),
        component_value["raw"],
    )
