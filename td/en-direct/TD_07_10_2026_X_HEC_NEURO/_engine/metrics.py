from __future__ import annotations
import numpy as np


def binary_metrics(y_true, score, threshold):
    """Window-level metrics on *uniform, labelled* windows only."""
    y_true = np.asarray(y_true)
    score = np.asarray(score, dtype=float)
    mask = y_true >= 0
    y = y_true[mask].astype(int)
    s = score[mask]
    pred = (s >= threshold).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    hit_rate = tp / max(tp + fn, 1)
    false_positive_rate = fp / max(fp + tn, 1)
    specificity = 1.0 - false_positive_rate
    return {
        "n": int(len(y)),
        "accuracy": (tp + tn) / max(len(y), 1),
        "balanced_accuracy": 0.5 * (hit_rate + specificity),
        "hit_rate": hit_rate,
        "false_positive_rate": false_positive_rate,
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
    }


def event_action_metrics(target_intervals, action_times, duration_s: float | None = None):
    """Event-level metrics for the game/controller.

    A target block is detected by the *first* executed action inside that block.
    Additional actions inside the same block count as false/unnecessary actions.
    Actions outside target blocks are also false actions.
    """
    intervals = [(float(a), float(b)) for a, b in target_intervals]
    actions = sorted(float(t) for t in action_times)
    detected = set()
    latencies = []
    false_actions = 0

    for t in actions:
        match = None
        for i, (a, b) in enumerate(intervals):
            if a <= t <= b:
                match = i
                break
        if match is None or match in detected:
            false_actions += 1
            continue
        detected.add(match)
        latencies.append(t - intervals[match][0])

    target_blocks = len(intervals)
    detected_blocks = len(detected)
    missed_blocks = target_blocks - detected_blocks
    if duration_s is None:
        duration_s = max([b for _, b in intervals] + actions + [0.0])
    commands_per_min = len(actions) / max(float(duration_s), 1e-9) * 60.0

    return {
        "target_blocks": target_blocks,
        "detected_blocks": detected_blocks,
        "missed_target_blocks": missed_blocks,
        "false_jumps": false_actions,
        "actions": len(actions),
        "commands_per_min": commands_per_min,
        "median_latency_s": float(np.median(latencies)) if latencies else float("nan"),
        "latencies_s": latencies,
    }
