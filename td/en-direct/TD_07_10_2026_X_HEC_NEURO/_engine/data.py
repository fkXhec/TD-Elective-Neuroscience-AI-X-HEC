"""Dataset loading and causal window iteration.

The classroom convention is:
  1 = JUMP target (attention to 12 Hz)
  0 = NONE (rest or another attended target)
 -1 = ignore / transition / mixed causal window

Important methodological point: a tuning/evaluation window is labelled only when
*every sample in the window* belongs to the same valid state.  A window that
straddles a transition is scored (as it would be online) but receives label -1
and is therefore excluded from supervised metrics.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np


@dataclass
class EEGDataset:
    eeg: np.ndarray          # (samples, channels), physical values in uV
    state: np.ndarray        # 1=JUMP target, 0=NONE, -1=ignore/transition
    sfreq: float
    channels: list[str]
    boundaries: np.ndarray   # sample indices where a new source record begins
    meta: dict

    def channel_indices(self, names: list[str]) -> list[int]:
        missing = [x for x in names if x not in self.channels]
        if missing:
            raise KeyError(f"Missing channels: {missing}. Available: {self.channels}")
        return [self.channels.index(x) for x in names]


def load_npz(path: str | Path) -> EEGDataset:
    z = np.load(path, allow_pickle=True)
    meta_raw = z["meta"].item() if z["meta"].shape == () else z["meta"].tolist()
    if isinstance(meta_raw, str):
        meta = json.loads(meta_raw)
    elif isinstance(meta_raw, dict):
        meta = meta_raw
    else:
        meta = {"raw_meta": meta_raw}
    return EEGDataset(
        eeg=np.asarray(z["eeg"], dtype=np.float32),
        state=np.asarray(z["state"], dtype=np.int8),
        sfreq=float(np.asarray(z["sfreq"]).item()),
        channels=[str(x) for x in z["channels"].tolist()],
        boundaries=np.asarray(z["boundaries"], dtype=np.int64),
        meta=meta,
    )


def _window_label(labels: np.ndarray) -> int:
    """Return 0/1 only if the whole causal window has one valid label."""
    labels = np.asarray(labels, dtype=np.int8)
    if len(labels) == 0:
        return -1
    if np.all(labels == 1):
        return 1
    if np.all(labels == 0):
        return 0
    return -1


def iter_causal_windows(ds: EEGDataset, channels: list[str], window_s: float, step_s: float = 0.25):
    """Yield ``(end_time_s, window, label)`` without crossing record boundaries.

    The EEG window is always causal: only samples up to the current end time are
    included.  The label is 0 or 1 only when the *entire* window belongs to the
    same valid state. Mixed/transition windows are labelled -1 so they can still
    flow through the online-like replay without contaminating tuning metrics.
    """
    idx = ds.channel_indices(channels)
    win = int(round(window_s * ds.sfreq))
    step = max(1, int(round(step_s * ds.sfreq)))
    if win < 4:
        raise ValueError("window_s is too short for this sampling rate")

    boundaries = list(ds.boundaries.astype(int)) + [len(ds.eeg)]
    for start_record, end_record in zip(boundaries[:-1], boundaries[1:]):
        first = start_record + win
        for end in range(first, end_record + 1, step):
            labels = ds.state[end - win:end]
            label = _window_label(labels)
            yield end / ds.sfreq, ds.eeg[end-win:end, idx], label


def target_intervals(ds: EEGDataset, target_freq: float | None = None, tol: float = 0.35) -> list[tuple[float, float]]:
    """Return true target intervals in seconds from metadata when available.

    These intervals are used only by the *environment/evaluation* to place
    obstacles and compute latency. They are never passed to the decoder.
    """
    if target_freq is None:
        target_freq = float(ds.meta.get("target_freq_hz", 12.0))
    intervals: list[tuple[float, float]] = []
    for seg in ds.meta.get("segments", []):
        # JSON turns tuples into lists: [record_name, start_sample, stop_sample, freq]
        if len(seg) != 4:
            continue
        _, start, stop, freq = seg
        if freq is None:
            continue
        if abs(float(freq) - float(target_freq)) <= tol:
            intervals.append((float(start) / ds.sfreq, float(stop) / ds.sfreq))
    return intervals
