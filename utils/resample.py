"""
Arc-length resampling and assembly of traj (30, 11, 2) + mask (30, 11) per plan.
"""

from __future__ import annotations

import numpy as np

NUM_AGENTS = 11
NUM_STEPS = 30


def resample_polyline_arc_length(points: np.ndarray, n: int = NUM_STEPS) -> np.ndarray:
    """
    Uniform arc-length resample of an open polyline. points: (M, 2), M >= 2.
    Returns (n, 2).
    """
    pts = np.asarray(points, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1] != 2:
        raise ValueError(f"points must be (M, 2), got {pts.shape}")
    if pts.shape[0] < 2:
        raise ValueError("Need at least 2 points to resample")

    d = np.sqrt(np.sum(np.diff(pts, axis=0) ** 2, axis=1))
    cum = np.concatenate([[0.0], np.cumsum(d)])
    total = float(cum[-1])
    if total < 1e-9:
        return np.repeat(pts[:1], n, axis=0)

    targets = np.linspace(0.0, total, n)
    out = np.empty((n, 2), dtype=np.float64)
    for i, t in enumerate(targets):
        idx = int(np.searchsorted(cum, t, side="right") - 1)
        idx = np.clip(idx, 0, len(pts) - 2)
        t0, t1 = cum[idx], cum[idx + 1]
        if t1 <= t0 + 1e-12:
            out[i] = pts[idx + 1]
        else:
            alpha = (t - t0) / (t1 - t0)
            out[i] = (1 - alpha) * pts[idx] + alpha * pts[idx + 1]
    return out.astype(np.float32)


def build_traj_and_mask(
    gt_t0: np.ndarray,
    strokes_ft: dict[int, np.ndarray],
    *,
    n_steps: int = NUM_STEPS,
    n_agents: int = NUM_AGENTS,
    prepend_eps_ft: float = 2.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    gt_t0: (11, 2) ground truth at t=0 for the clip.
    strokes_ft: agent_id -> (M, 2) user stroke in feet (may omit agents).

    Traced agent: polyline = [gt_t0[a]] + stroke (if first stroke point is not within
    prepend_eps_ft of gt, still prepend gt explicitly then stroke).
    Resample whole chain to n_steps. mask[:,a] = 1.

    Untraced: traj[0,a]=gt, traj[1:,a]=0, mask[0,a]=1, mask[1:,a]=0.
    """
    gt = np.asarray(gt_t0, dtype=np.float32)
    if gt.shape != (n_agents, 2):
        raise ValueError(f"gt_t0 must be ({n_agents}, 2), got {gt.shape}")

    traj = np.zeros((n_steps, n_agents, 2), dtype=np.float32)
    mask = np.zeros((n_steps, n_agents), dtype=np.uint8)

    traj[0, :, :] = gt
    mask[0, :] = 1

    for a in range(n_agents):
        stroke = strokes_ft.get(a)
        if stroke is None:
            continue
        s = np.asarray(stroke, dtype=np.float32)
        if s.size == 0 or s.shape[0] < 2:
            continue

        start = gt[a].astype(np.float64)
        if s.shape[0] < 2:
            continue
        if float(np.linalg.norm(s[0] - start)) <= prepend_eps_ft:
            chain = np.vstack([start[None, :], s[1:]])
        else:
            chain = np.vstack([start[None, :], s])
        if chain.shape[0] < 2:
            continue

        try:
            sampled = resample_polyline_arc_length(chain, n_steps)
        except ValueError:
            continue

        traj[:, a, :] = sampled
        mask[:, a] = 1

    return traj, mask


def validate_trajectory_array(data: np.ndarray) -> tuple[int, int, int, int]:
    """Return (b, t, a, c) after checks."""
    if data.ndim != 4:
        raise ValueError(f"Expected array ndim 4 [b,t,a,c], got shape {data.shape}")
    b, t, a, c = data.shape
    if a != NUM_AGENTS:
        raise ValueError(f"Expected a={NUM_AGENTS} agents, got {a}")
    if c < 2:
        raise ValueError(f"Expected c>=2 for x,y, got c={c}")
    return b, t, a, c
