"""
Render the NBA court with optional t=0 markers and extra polylines (feet coords).

Pixel ↔ foot mapping uses the matplotlib display transform at export time so
aspect-equal axes (letterboxing) stay consistent with the PNG.
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from PIL import Image

from utils.drawing import COLOR_AWAY, COLOR_BALL, COLOR_HOME, COURT_PAD_FT, Court

FIGSIZE = (7.5, 4.0)
DPI = 64
NUM_AGENTS = 11


@dataclass(frozen=True)
class CourtRenderResult:
    """RGB uint8 image (H, W, 3) and figure display bbox for the cropped axes region."""

    rgb: np.ndarray
    bbox_x0: float
    bbox_y0: float
    bbox_x1: float
    bbox_y1: float
    fig_h_px: int

    def canvas_uv_to_disp(self, u: float, v: float) -> tuple[float, float]:
        """
        Map pixel (u, v) with origin top-left of ``rgb`` to figure display coords
        (origin bottom-left, pixels).
        """
        h, w = self.rgb.shape[0], self.rgb.shape[1]
        disp_x = self.bbox_x0 + (u + 0.5) / max(w, 1) * (self.bbox_x1 - self.bbox_x0)
        # Top row of image v=0 corresponds to larger display y (top of axes).
        disp_y = self.bbox_y1 - (v + 0.5) / max(h, 1) * (self.bbox_y1 - self.bbox_y0)
        return float(disp_x), float(disp_y)


def _agent_color(idx: int) -> tuple:
    if idx < 5:
        return COLOR_HOME
    if idx < 10:
        return COLOR_AWAY
    return COLOR_BALL


def render_for_canvas(
    positions_t0: np.ndarray,
    *,
    extra_paths: dict[int, np.ndarray] | None = None,
    highlight_agent: int | None = None,
) -> tuple[Image.Image, CourtRenderResult, object]:
    """
    Return PIL RGB background, crop metadata, and a mapper with ``batch(uv Nx2) -> feet Nx2``.
    """
    positions_t0 = np.asarray(positions_t0, dtype=float)
    if positions_t0.shape != (NUM_AGENTS, 2):
        raise ValueError(f"positions_t0 must be (11, 2), got {positions_t0.shape}")

    fig, ax = plt.subplots(1, 1, figsize=FIGSIZE, dpi=DPI)
    fig.subplots_adjust(0, 0, 1, 1, wspace=0, hspace=0)
    ax.set_position([0, 0, 1, 1])

    court = Court(court_type="nba", origin="bottom-left", units="ft")
    court.draw(ax=ax, orientation="h", showaxis=False, pad=COURT_PAD_FT)

    extra_paths = extra_paths or {}
    for aid, path in sorted(extra_paths.items()):
        if aid == highlight_agent:
            continue
        pts = np.asarray(path, dtype=float)
        if pts.ndim != 2 or pts.shape[0] < 2 or pts.shape[1] != 2:
            continue
        c = _agent_color(aid)
        ax.add_line(
            Line2D(
                pts[:, 0],
                pts[:, 1],
                color=c,
                linewidth=2.0,
                alpha=0.55,
                zorder=2,
            )
        )

    if highlight_agent is not None:
        hp = extra_paths.get(highlight_agent)
        if hp is not None:
            pts = np.asarray(hp, dtype=float)
            if pts.ndim == 2 and pts.shape[0] >= 2 and pts.shape[1] == 2:
                c = _agent_color(highlight_agent)
                ax.add_line(
                    Line2D(
                        pts[:, 0],
                        pts[:, 1],
                        color=c,
                        linewidth=2.6,
                        alpha=0.92,
                        zorder=3,
                    )
                )

    for i in range(NUM_AGENTS):
        c = _agent_color(i)
        z = 5 if i == 10 else 4
        ax.scatter(
            [positions_t0[i, 0]],
            [positions_t0[i, 1]],
            s=120 if highlight_agent is None or i == highlight_agent else 70,
            c=[c],
            edgecolors="white",
            linewidths=1.0,
            zorder=z,
        )

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bbox = ax.get_window_extent(renderer=renderer)

    disp_to_data = ax.transData.inverted()

    rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8)
    # Use buffer shape, not get_width_height(): that API returns (width, height) but this
    # code historically assigned them as (height, width). After Streamlit configures
    # Matplotlib, the mismatch skews the Y crop to a ~32px-tall sliver.
    fig_h_px, fig_w_px = int(rgba.shape[0]), int(rgba.shape[1])
    plt.close(fig)

    bx0 = float(bbox.x0)
    bx1 = float(bbox.x1)
    by0 = float(bbox.y0)
    by1 = float(bbox.y1)

    ix0 = int(np.floor(bx0))
    ix1 = int(np.ceil(bx1))
    iy_bottom = int(np.floor(by0))
    iy_top = int(np.ceil(by1))
    ix0 = max(0, ix0)
    ix1 = min(rgba.shape[1], ix1)
    iy_bottom = max(0, iy_bottom)
    iy_top = min(rgba.shape[0], iy_top)

    row_top = fig_h_px - iy_top
    row_bottom = fig_h_px - iy_bottom
    row_top = max(0, row_top)
    row_bottom = min(fig_h_px, row_bottom)
    crop = rgba[row_top:row_bottom, ix0:ix1, :]
    rgb = crop[:, :, :3].copy()

    res = CourtRenderResult(
        rgb=rgb,
        bbox_x0=bx0,
        bbox_y0=by0,
        bbox_x1=bx1,
        bbox_y1=by1,
        fig_h_px=int(fig_h_px),
    )

    class _Map:
        @staticmethod
        def batch(uvs: np.ndarray) -> np.ndarray:
            uvs = np.asarray(uvs, dtype=float)
            if uvs.size == 0:
                return np.zeros((0, 2), dtype=np.float32)
            rows = []
            for u, v in uvs:
                dx, dy = res.canvas_uv_to_disp(float(u), float(v))
                xy = disp_to_data.transform((dx, dy))
                rows.append((float(xy[0]), float(xy[1])))
            return np.asarray(rows, dtype=np.float32)

    pil_img = Image.fromarray(rgb, mode="RGB")
    return pil_img, res, _Map()
