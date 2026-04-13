"""
Trajectory conditioning tracer — Streamlit UI.

Run: ``uv run streamlit run streamlit_app.py``

Loads ``[b,t,a,c]`` trajectories, draws per-agent strokes on a court image,
saves under ``outputs/idx{K}_{timestamp}/``:
``conditioning_idx{K}_traj.npy``, ``conditioning_idx{K}_mask.npy``, and ``preview.jpg``.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from utils.canvas_extract import ordered_stroke_from_canvas
from utils.canvas_streamlit import gameplay_st_canvas
from utils.court_image import render_for_canvas
from utils.drawing import render_conditioning_preview, render_scene_to_rgb
from utils.streamlit_data_url import np_rgb_to_jpeg_data_url
from utils.resample import NUM_AGENTS, build_traj_and_mask, validate_trajectory_array

# Custom components default to a ~700px-wide iframe; wider pixel canvases are clipped.
_MAX_CANVAS_IFRAME_PX = 700


def _wrap_mapper_uv_scale(inner: object, sx: float, sy: float) -> object:
    if abs(sx - 1.0) < 1e-9 and abs(sy - 1.0) < 1e-9:
        return inner

    class _Scaled:
        @staticmethod
        def batch(uvs: np.ndarray) -> np.ndarray:
            uvs = np.asarray(uvs, dtype=np.float32)
            if uvs.size == 0:
                return np.zeros((0, 2), dtype=np.float32)
            uvs = uvs * np.array([sx, sy], dtype=np.float32)
            return inner.batch(uvs)

    return _Scaled()


def _on_active_agent_changed() -> None:
    """Remount drawable canvas so Fabric state resets without Python↔Fabric JSON round-trips."""
    st.session_state.canvas_rev = int(st.session_state.canvas_rev) + 1


def _canvas_for_iframe(pil_bg: Image.Image) -> tuple[Image.Image, int, int, object]:
    """
    Shrink the drawable canvas if needed so the full court fits Streamlit's iframe.
    Returns (pil for st_canvas, width, height, sx_sy scale factors vs full-res for mapper).
    """
    w_full, h_full = pil_bg.size
    scale = min(1.0, _MAX_CANVAS_IFRAME_PX / float(max(w_full, 1)))
    w_disp = max(1, int(round(w_full * scale)))
    h_disp = max(1, int(round(h_full * scale)))
    if scale < 1.0:
        pil_disp = pil_bg.resize((w_disp, h_disp), Image.Resampling.LANCZOS)
        sx = w_full / w_disp
        sy = h_full / h_disp
    else:
        pil_disp = pil_bg
        sx = sy = 1.0
    return pil_disp, w_disp, h_disp, (sx, sy)


@st.cache_data(show_spinner="Loading trajectory…")
def _load_trajectory_npy(path_str: str, mtime: float) -> np.ndarray:
    """
    Cached load keyed by resolved path and file mtime so reruns do not re-read
    disk unless the file changes (plan: guard np.load by path + mtime).
    """
    return np.load(path_str)


AGENT_LABELS = (
    "0 — Team 1 / P1",
    "1 — Team 1 / P2",
    "2 — Team 1 / P3",
    "3 — Team 1 / P4",
    "4 — Team 1 / P5",
    "5 — Team 2 / P1",
    "6 — Team 2 / P2",
    "7 — Team 2 / P3",
    "8 — Team 2 / P4",
    "9 — Team 2 / P5",
    "10 — Ball",
)


def _init_state() -> None:
    if "traj_data" not in st.session_state:
        st.session_state.traj_data = None
    if "strokes" not in st.session_state:
        st.session_state.strokes = {}
    if "canvas_rev" not in st.session_state:
        st.session_state.canvas_rev = 0
    if "preview_rgb" not in st.session_state:
        st.session_state.preview_rgb = None


def main() -> None:
    st.set_page_config(layout="wide", page_title="Trajectory conditioning")
    _init_state()

    st.title("Trajectory conditioning tracer")
    st.caption(
        "Row 0 of saved traj is always GT t=0; mask[0,:]=1. "
        "Untraced agents have zeros for t≥1. Pixel→feet uses the same matplotlib "
        "transform as the court background."
    )

    with st.sidebar:
        npy_path = st.text_input("Trajectory .npy path", "data/nba_test.npy")
        if st.button("Load data", type="primary"):
            p = Path(npy_path)
            if not p.is_file():
                st.error(f"File not found: {p}")
            else:
                try:
                    mtime = p.stat().st_mtime
                    arr = _load_trajectory_npy(str(p.resolve()), mtime)
                    validate_trajectory_array(arr)
                    st.session_state.traj_data = arr
                    st.session_state.strokes = {}
                    st.session_state.canvas_rev += 1
                    st.session_state.preview_rgb = None
                    st.success(f"Loaded shape {arr.shape}")
                except Exception as e:
                    st.error(str(e))

        data = st.session_state.traj_data
        idx = 0
        if data is not None:
            b = data.shape[0]
            idx = int(st.number_input("Batch index", min_value=0, max_value=b - 1, value=0, step=1))

        out_dir = st.text_input("Output directory", "outputs")

        st.divider()
        st.subheader("Drawing")
        agent_i = st.selectbox(
            "Active agent",
            range(NUM_AGENTS),
            format_func=lambda i: AGENT_LABELS[i],
            key="active_agent_pick",
            on_change=_on_active_agent_changed,
        )
        if st.button("Clear stroke for this agent"):
            st.session_state.strokes.pop(agent_i, None)
            st.session_state.canvas_rev += 1
            st.rerun()
        if st.button("Clear all strokes"):
            st.session_state.strokes = {}
            st.session_state.canvas_rev += 1
            st.rerun()

        if st.button("Preview (no save)"):
            if data is None:
                st.warning("Load data first.")
            else:
                gt0 = data[idx, 0, :, :2].astype(np.float32)
                traj, mask = build_traj_and_mask(gt0, st.session_state.strokes)
                st.session_state.preview_rgb = render_conditioning_preview(traj, mask)
                st.rerun()

        if st.button("Save .npy files"):
            if data is None:
                st.warning("Load data first.")
            else:
                gt0 = data[idx, 0, :, :2].astype(np.float32)
                traj, mask = build_traj_and_mask(gt0, st.session_state.strokes)
                od = Path(out_dir)
                od.mkdir(parents=True, exist_ok=True)
                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                run_dir = od / f"idx{idx}_{ts}"
                run_dir.mkdir(parents=True, exist_ok=False)
                stem = f"conditioning_idx{idx}"
                np.save(run_dir / f"{stem}_traj.npy", traj)
                np.save(run_dir / f"{stem}_mask.npy", mask)
                preview_rgb = render_conditioning_preview(traj, mask)
                st.session_state.preview_rgb = preview_rgb
                Image.fromarray(preview_rgb).save(
                    run_dir / "preview.jpg", format="JPEG", quality=92
                )
                st.toast(
                    f"Saved to {run_dir.relative_to(od)}/ ({stem}_*.npy, preview.jpg)",
                    icon="✅",
                )

    col_draw, col_ref, col_prev = st.columns([2.35, 1.0, 1.0])

    if data is None:
        col_draw.info("Load a `[b,t,a,c]` .npy` from the sidebar (e.g. `data/nba_test.npy`).")
        col_ref.empty()
        col_prev.empty()
        return

    gt0 = data[idx, 0, :, :2].astype(np.float32)
    traj_xy = data[idx, :, :, :2].astype(np.float32)

    extra = dict(st.session_state.strokes)
    pil_bg, _res, mapper = render_for_canvas(
        gt0,
        extra_paths=extra,
        highlight_agent=agent_i,
    )
    w_full, h_full = pil_bg.size
    pil_canvas, w, h, (sx, sy) = _canvas_for_iframe(pil_bg)
    mapper = _wrap_mapper_uv_scale(mapper, sx, sy)
    _canvas_key = f"canvas_{st.session_state.canvas_rev}"

    with col_draw:
        st.subheader("Draw conditioning")
        cap = (
            f"Canvas {w}×{h} px — apply stroke for **{AGENT_LABELS[agent_i]}**"
            if (sx == 1.0 and sy == 1.0)
            else (
                f"Canvas {w}×{h} px (full res {w_full}×{h_full}, scaled to fit the view) — "
                f"**{AGENT_LABELS[agent_i]}**"
            )
        )
        st.caption(cap)
        canvas_result = gameplay_st_canvas(
            fill_color="rgba(255, 165, 0, 0.2)",
            stroke_width=3,
            stroke_color="#e62020",
            background_image=pil_canvas,
            media_coordinate_key=_canvas_key,
            update_streamlit=True,
            height=h,
            width=w,
            drawing_mode="freedraw",
            display_toolbar=True,
            key=_canvas_key,
        )

        if st.button("Apply stroke to active agent", key="apply_btn"):
            uv = ordered_stroke_from_canvas(canvas_result)
            if uv.shape[0] < 4:
                st.warning("Draw a longer stroke (more points) before applying.")
            else:
                ft = mapper.batch(uv)
                st.session_state.strokes[agent_i] = ft
                st.session_state.canvas_rev += 1
                st.rerun()

    with col_ref:
        st.subheader("Ground truth (reference)")
        try:
            ref_rgb = render_scene_to_rgb(traj_xy)
            st.image(
                np_rgb_to_jpeg_data_url(ref_rgb, quality=88),
                use_column_width=True,
            )
        except Exception as e:
            st.error(str(e))

    with col_prev:
        st.subheader("Preview (saved conditioning)")
        if st.session_state.preview_rgb is not None:
            st.image(
                np_rgb_to_jpeg_data_url(st.session_state.preview_rgb, quality=88),
                use_column_width=True,
            )
        else:
            st.info("Click **Preview** or **Save** in the sidebar to render the 30-step conditioning.")

    with st.expander("Session strokes (feet)"):
        st.json(
            {
                AGENT_LABELS[k]: v.tolist()
                for k, v in sorted(st.session_state.strokes.items())
            }
        )


if __name__ == "__main__":
    main()
