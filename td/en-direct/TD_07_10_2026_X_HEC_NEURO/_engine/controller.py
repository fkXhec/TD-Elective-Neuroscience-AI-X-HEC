"""Decision and control logic: threshold -> confirmation -> one-shot latch -> cooldown.

A sustained SSVEP response should generate ONE action, not repeated jumps every
cooldown interval. After firing, the controller remains disarmed until the score
has returned below threshold for several consecutive windows.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class JumpController:
    threshold: float
    confirm: int = 2
    cooldown_s: float = 1.0
    release_confirm: int = 3
    _streak: int = 0
    _release_streak: int = 0
    _last_action_t: float = -1e9
    _armed: bool = True

    def reset(self):
        self._streak = 0
        self._release_streak = 0
        self._last_action_t = -1e9
        self._armed = True

    def update(self, score: float, t: float) -> tuple[str, bool]:
        decision = "JUMP" if score >= self.threshold else "NONE"

        # Once an action has fired, wait for a genuine return to NONE before
        # allowing another action. This prevents one 5 s SSVEP block from
        # generating several jumps.
        if not self._armed:
            if decision == "NONE":
                self._release_streak += 1
                if (
                    self._release_streak >= self.release_confirm
                    and (t - self._last_action_t) >= self.cooldown_s
                ):
                    self._armed = True
                    self._release_streak = 0
            else:
                self._release_streak = 0
            return decision, False

        self._streak = self._streak + 1 if decision == "JUMP" else 0
        allowed = (t - self._last_action_t) >= self.cooldown_s
        action = self._streak >= self.confirm and allowed

        if action:
            self._last_action_t = t
            self._streak = 0
            self._release_streak = 0
            self._armed = False

        return decision, action


def decode_score_stream(times, scores, threshold: float, confirm: int = 2,
                        cooldown_s: float = 1.0, release_confirm: int = 3):
    """Decode a score stream exactly once per score sample.

    This is intentionally independent of display frame rate or replay speed.
    `confirm=2` therefore means two successive CCA windows, not two video frames.
    """
    ctrl = JumpController(
        threshold=float(threshold),
        confirm=int(confirm),
        cooldown_s=float(cooldown_s),
        release_confirm=int(release_confirm),
    )
    decisions = []
    action_flags = []
    action_times = []

    for t, score in zip(times, scores):
        decision, action = ctrl.update(float(score), float(t))
        decisions.append(decision)
        action_flags.append(bool(action))
        if action:
            action_times.append(float(t))

    return decisions, action_flags, action_times
