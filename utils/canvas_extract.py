"""Extract an ordered polyline from streamlit-drawable-canvas (Fabric draw order + raster positions)."""

from __future__ import annotations

import re
from typing import Any

import numpy as np


def _path_commands_to_xy(path: Any) -> list[tuple[float, float]]:
    """Parse Fabric ``path`` (list of SVG-style commands) to ordered (x, y) in canvas pixels."""
    if path is None:
        return []
    if isinstance(path, str):
        return _path_string_to_xy(path)
    if not isinstance(path, (list, tuple)):
        return []

    points: list[tuple[float, float]] = []
    for cmd in path:
        if not cmd:
            continue
        op = str(cmd[0]).upper()
        nums: list[float] = []
        for x in cmd[1:]:
            try:
                nums.append(float(x))
            except (TypeError, ValueError):
                pass
        if op == "M" and len(nums) >= 2:
            points.append((nums[0], nums[1]))
        elif op == "L" and len(nums) >= 2:
            points.append((nums[0], nums[1]))
        elif op == "Q" and len(nums) >= 4:
            points.append((nums[2], nums[3]))
        elif op == "C" and len(nums) >= 6:
            points.append((nums[4], nums[5]))
    return points


def _path_string_to_xy(s: str) -> list[tuple[float, float]]:
    pts: list[tuple[float, float]] = []
    for m in re.finditer(
        r"[MmLl]\s*([\d.+-]+)\s*[,\s]\s*([\d.+-]+)", s, flags=re.IGNORECASE
    ):
        pts.append((float(m.group(1)), float(m.group(2))))
    return pts


def _collect_fabric_guide_points(objects: Any) -> list[tuple[float, float]]:
    """
    Ordered path vertices from Fabric JSON.

    Coordinates are used only as a **polyline guide** for sorting raster ink; we do
    not apply left/top/scale/angle (those shifted positions vs the RGBA layer).
    """
    if not isinstance(objects, list):
        return []
    all_pts: list[tuple[float, float]] = []
    for obj in objects:
        if not isinstance(obj, dict):
            continue
        t = str(obj.get("type", "")).lower()
        if t == "group":
            all_pts.extend(_collect_fabric_guide_points(obj.get("objects") or []))
            continue
        if t != "path":
            continue
        all_pts.extend(_path_commands_to_xy(obj.get("path")))
    return all_pts


def _dedup_consecutive(
    pts: list[tuple[float, float]], eps: float = 0.25
) -> list[tuple[float, float]]:
    if len(pts) < 2:
        return pts
    out: list[tuple[float, float]] = [pts[0]]
    for p in pts[1:]:
        q = out[-1]
        if abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps:
            continue
        out.append(p)
    return out


def fabric_guide_polyline(raw: Any) -> np.ndarray:
    """(M, 2) float32 polyline from ``json_data`` for ordering; may be empty."""
    if raw is None or not isinstance(raw, dict):
        return np.zeros((0, 2), dtype=np.float32)
    pts = _dedup_consecutive(_collect_fabric_guide_points(raw.get("objects")))
    if len(pts) < 2:
        return np.zeros((0, 2), dtype=np.float32)
    return np.asarray(pts, dtype=np.float32)


def _ink_pixels_unordered(
    image_data: np.ndarray | None,
    *,
    alpha_threshold: int = 40,
    max_points: int = 4000,
) -> np.ndarray:
    """All stroke pixels (N, 2) as float32 (u, v); arbitrary order."""
    if image_data is None:
        return np.zeros((0, 2), dtype=np.float32)
    rgba = np.asarray(image_data)
    if rgba.ndim != 3 or rgba.shape[2] < 4:
        return np.zeros((0, 2), dtype=np.float32)
    alpha = rgba[:, :, 3]
    ys, xs = np.where(alpha > alpha_threshold)
    if xs.size == 0:
        return np.zeros((0, 2), dtype=np.float32)
    pts = np.column_stack([xs.astype(np.float32), ys.astype(np.float32)])
    if pts.shape[0] > max_points:
        sel = np.linspace(0, pts.shape[0] - 1, max_points).astype(np.int64)
        pts = pts[sel]
    return pts


def _arc_positions_along_polyline(poly: np.ndarray, pts: np.ndarray) -> np.ndarray:
    """
    For each point in ``pts``, distance along ``poly`` (piecewise linear) to the
    closest projection. ``poly`` is (M, 2), ``pts`` is (N, 2).
    """
    if poly.shape[0] < 2 or pts.shape[0] == 0:
        return np.zeros(pts.shape[0], dtype=np.float64)
    a = poly[:-1]
    b = poly[1:]
    seg = b - a
    seg_len = np.sqrt(np.sum(seg**2, axis=1))
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])
    out = np.zeros(pts.shape[0], dtype=np.float64)
    for j in range(pts.shape[0]):
        p = pts[j]
        best_d2 = np.inf
        best_s = 0.0
        for i in range(poly.shape[0] - 1):
            ai = a[i]
            vi = seg[i]
            lab2 = float(np.dot(vi, vi))
            if lab2 < 1e-18:
                proj = ai
                t = 0.0
            else:
                t = float(np.clip(np.dot(p - ai, vi) / lab2, 0.0, 1.0))
                proj = ai + t * vi
            d2 = float(np.sum((p - proj) ** 2))
            if d2 < best_d2:
                best_d2 = d2
                best_s = float(cum[i] + t * seg_len[i])
        out[j] = best_s
    return out


def ordered_stroke_from_canvas(canvas_result: Any) -> np.ndarray:
    """
    Order stroke pixels using Fabric path **sequence** (true draw order) while keeping
    **pixel positions** from the RGBA layer (matches ``mapper.batch``).

    Falls back to raster-only heuristic if Fabric has no usable polyline.
    """
    rgba = getattr(canvas_result, "image_data", None)
    raw = getattr(canvas_result, "json_data", None)

    ink = _ink_pixels_unordered(rgba)
    if ink.shape[0] < 4:
        return ink

    guide = fabric_guide_polyline(raw)
    if guide.shape[0] < 2:
        return ordered_stroke_from_rgba(rgba)

    s = _arc_positions_along_polyline(guide, ink)
    order = np.argsort(s, kind="stable")
    return ink[order].astype(np.float32)


def ordered_stroke_from_rgba(
    image_data: np.ndarray | None,
    *,
    alpha_threshold: int = 40,
    max_points: int = 4000,
) -> np.ndarray:
    """
    ``image_data`` is (H, W, 4) RGBA from ``st_canvas`` (drawing only, transparent bg).

    Returns (N, 2) float32 ``(u, v)`` in canvas pixel coords. Order is a bounding-box
    start plus greedy nearest-neighbor (legacy fallback).
    """
    pts = _ink_pixels_unordered(
        image_data, alpha_threshold=alpha_threshold, max_points=max_points
    )
    if pts.shape[0] < 4:
        return pts

    start = int(np.argmin(pts[:, 0] + pts[:, 1] * 1e-6))
    remaining = set(range(pts.shape[0]))
    remaining.discard(start)
    order = [start]
    cur = start
    while remaining:
        best = min(remaining, key=lambda j: float(np.sum((pts[j] - pts[cur]) ** 2)))
        order.append(best)
        remaining.remove(best)
        cur = best

    return pts[order]
