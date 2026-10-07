"""Minimal CCA utilities for the SSVEP classroom TD.

The implementation is deliberately explicit: students can inspect every
transformation from an EEG window to a canonical-correlation score.
"""
from __future__ import annotations

import numpy as np


def make_reference(n_samples: int, sfreq: float, freq: float, harmonics: int = 2) -> np.ndarray:
    """Return sin/cos reference signals with shape (n_samples, 2*harmonics)."""
    if n_samples < 3:
        raise ValueError("n_samples must be >= 3")
    if sfreq <= 0 or freq <= 0:
        raise ValueError("sfreq and freq must be positive")
    t = np.arange(n_samples, dtype=float) / float(sfreq)
    cols = []
    for h in range(1, harmonics + 1):
        phase = 2.0 * np.pi * h * freq * t
        cols.extend([np.sin(phase), np.cos(phase)])
    return np.column_stack(cols)


def _inv_sqrt_psd(a: np.ndarray, reg: float) -> np.ndarray:
    vals, vecs = np.linalg.eigh(a)
    vals = np.maximum(vals, reg)
    return (vecs * (1.0 / np.sqrt(vals))) @ vecs.T


def cca_score(x: np.ndarray, y: np.ndarray, reg: float = 1e-6) -> float:
    """Largest canonical correlation between X and Y.

    Parameters
    ----------
    x : array, shape (samples, eeg_channels)
    y : array, shape (samples, reference_channels)
    reg : small covariance regularizer
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.ndim != 2 or y.ndim != 2 or x.shape[0] != y.shape[0]:
        raise ValueError("x and y must be 2D with the same number of samples")
    if x.shape[0] < 4:
        return float("nan")

    x = x - x.mean(axis=0, keepdims=True)
    y = y - y.mean(axis=0, keepdims=True)
    # Scale each variable to avoid a numerically dominant channel.
    xs = x.std(axis=0, ddof=1)
    ys = y.std(axis=0, ddof=1)
    x = x / np.where(xs > 1e-12, xs, 1.0)
    y = y / np.where(ys > 1e-12, ys, 1.0)

    denom = max(x.shape[0] - 1, 1)
    cxx = (x.T @ x) / denom + reg * np.eye(x.shape[1])
    cyy = (y.T @ y) / denom + reg * np.eye(y.shape[1])
    cxy = (x.T @ y) / denom

    wx = _inv_sqrt_psd(cxx, reg)
    wy = _inv_sqrt_psd(cyy, reg)
    s = np.linalg.svd(wx @ cxy @ wy, compute_uv=False)
    return float(np.clip(s[0], 0.0, 1.0))


def ssvep_score(window: np.ndarray, sfreq: float, freq: float = 12.0, harmonics: int = 2) -> float:
    ref = make_reference(len(window), sfreq, freq, harmonics=harmonics)
    return cca_score(window, ref)
