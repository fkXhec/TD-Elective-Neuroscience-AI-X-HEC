from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from .data import load_npz, target_intervals
from .replay import score_dataset
from .metrics import binary_metrics, event_action_metrics
from .game import run_replay_game
from .controller import decode_score_stream

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

FILES = {
    "tune": DATA / "sub-01_tune.npz",
    "game": DATA / "sub-01_game.npz",
    "generalization": DATA / "sub-02_generalization.npz",
}


def _missing_message(path: Path) -> str:
    return (
        f"\nDonnées de TD manquantes : {path.name}\n"
        "Les étudiants n'ont rien à télécharger pendant la séance.\n"
        "Demandez à l'enseignant de copier les fichiers préparés dans data/processed/.\n"
    )


def load_classroom_data(which: str):
    if which not in FILES:
        raise ValueError(f"which must be one of {list(FILES)}")
    path = FILES[which]
    if not path.exists():
        raise FileNotFoundError(_missing_message(path))
    return load_npz(path)


def show_posterior_eeg(ds, start_s: float = 20.0, duration_s: float = 8.0,
                       names=("P7", "O1", "O2", "P8")):
    names = [n for n in names if n in ds.channels]
    idx = ds.channel_indices(names)
    a = int(start_s * ds.sfreq)
    b = min(len(ds.eeg), int((start_s + duration_s) * ds.sfreq))
    t = np.arange(max(b-a, 0)) / ds.sfreq
    fig, ax = plt.subplots(figsize=(11, 4.5))
    offset = 0.0
    for name, j in zip(names, idx):
        x = ds.eeg[a:b, j]
        scale = np.nanstd(x) * 6 or 1.0
        ax.plot(t, x + offset, lw=.8, label=name)
        offset += scale
    ax.set(xlabel="Temps (s)", ylabel="µV + décalage visuel",
           title="Extrait d'EEG postérieur enregistré")
    ax.legend(ncol=len(names))
    ax.grid(alpha=.2)
    plt.show()


def compute_tune_scores(ds, channels, window_s, step_s=0.25, target_freq=12.0, harmonics=2):
    return score_dataset(ds, channels, window_s, step_s, target_freq, harmonics)


def plot_score_distributions(states, scores):
    mask0 = states == 0
    mask1 = states == 1
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(scores[mask0], bins=30, alpha=.6, density=True, label="NONE")
    ax.hist(scores[mask1], bins=30, alpha=.6, density=True, label="JUMP / cible 12 Hz")
    ax.set(xlabel="Score CCA à 12 Hz", ylabel="Densité",
           title="Données de réglage uniquement")
    ax.legend()
    ax.grid(alpha=.2)
    plt.show()


def evaluate_windows(states, scores, threshold):
    return binary_metrics(states, scores, threshold)


def compare_settings(ds, channels, windows=(1.0, 1.5, 2.0, 3.0),
                     thresholds=(0.25, 0.35, 0.45, 0.55, 0.65),
                     step_s=0.25, target_freq=12.0, harmonics=2):
    rows = []
    for ws in windows:
        _, scores, states = score_dataset(ds, channels, ws, step_s, target_freq, harmonics)
        for tau in thresholds:
            m = binary_metrics(states, scores, tau)
            rows.append({
                "window_s": ws,
                "threshold": tau,
                "hit_rate": m["hit_rate"],
                "false_positive_rate": m["false_positive_rate"],
                "balanced_accuracy": m["balanced_accuracy"],
                "accuracy": m["accuracy"],
            })
    return rows


def print_settings_table(rows):
    print("window | threshold | hit rate | false positive rate | balanced acc.")
    print("-------|-----------|----------|---------------------|--------------")
    for r in rows:
        print(f"{r['window_s']:>6.1f} | {r['threshold']:>9.2f} | "
              f"{r['hit_rate']:>8.2f} | {r['false_positive_rate']:>19.2f} | "
              f"{r['balanced_accuracy']:>12.2f}")


def evaluate_dataset(ds, channels, window_s, threshold, step_s=0.25,
                     target_freq=12.0, harmonics=2):
    times, scores, states = score_dataset(ds, channels, window_s, step_s, target_freq, harmonics)
    return times, scores, states, binary_metrics(states, scores, threshold)



def evaluate_controller(ds, channels, window_s, threshold, step_s=0.25,
                        target_freq=12.0, harmonics=2, confirm=2,
                        cooldown_s=1.0):
    """Event/action metrics on the full held-out timeline.

    Unlike the compact game, this evaluates the controller over the whole
    session, including long NONE periods.
    """
    times, scores, states = score_dataset(
        ds, channels, window_s, step_s, target_freq, harmonics
    )
    _, _, action_times = decode_score_stream(
        times, scores, threshold,
        confirm=confirm, cooldown_s=cooldown_s
    )
    intervals = target_intervals(ds, target_freq)
    duration = float(times[-1] - times[0]) if len(times) > 1 else 0.0
    return event_action_metrics(intervals, action_times, duration_s=duration)


def play_dataset(ds, channels, window_s, threshold, step_s=0.25,
                 target_freq=12.0, harmonics=2, confirm=2,
                 cooldown_s=1.0, speed=3.0, compact=True, max_targets=5):
    times, scores, states = score_dataset(ds, channels, window_s, step_s, target_freq, harmonics)
    intervals = target_intervals(ds, target_freq)
    return run_replay_game(
        times, scores, states,
        threshold=threshold,
        confirm=confirm,
        cooldown_s=cooldown_s,
        speed=speed,
        target_intervals=intervals,
        compact=compact,
        max_targets=max_targets,
        window_s=window_s,
        channels=channels,
    )
