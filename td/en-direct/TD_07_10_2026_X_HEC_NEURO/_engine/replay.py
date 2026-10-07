from __future__ import annotations
import numpy as np
from .cca import ssvep_score
from .data import EEGDataset, iter_causal_windows


def score_dataset(ds: EEGDataset, channels, window_s, step_s=0.25, freq=12.0, harmonics=2):
    times, scores, states = [], [], []
    for t, w, state in iter_causal_windows(ds, channels, window_s, step_s):
        times.append(t)
        scores.append(ssvep_score(w, ds.sfreq, freq=freq, harmonics=harmonics))
        states.append(state)
    return np.asarray(times), np.asarray(scores), np.asarray(states, dtype=int)
