"""Tiny Geometry-Dash-like visualization for a recorded EEG replay.

The game deliberately uses ground-truth event timings only for the *environment*
(obstacle placement + evaluation).  The decoder still receives EEG-derived
scores only.

For classroom use we default to an event-focused replay: the long original
recording is reduced to short causal snippets around the five 12-Hz target
blocks.  This preserves the decoder outputs and their relative timing while
avoiding several minutes of visually empty replay.
"""
from __future__ import annotations


def require_pygame():
    """Import pygame from the notebook kernel.

    Dependency installation belongs to setup_students.py, not to the game loop.
    """
    try:
        import pygame
        return pygame
    except ImportError as e:
        raise RuntimeError(
            "pygame n'est pas disponible dans le noyau Python du notebook. "
            "Sélectionnez le Python affiché par setup_students.py, ou exécutez "
            "dans une cellule : %pip install pygame"
        ) from e


def _compact_event_replay(times, scores, states, target_intervals,
                          pre_s=2.0, post_s=1.5, max_targets=5):
    """Return a compact timeline made of snippets around target events.

    The score at each retained point is unchanged; only long irrelevant gaps are
    removed.  Each snippet remains causal because scores were computed from the
    original past EEG before compaction.
    """
    import numpy as np

    times = np.asarray(times, dtype=float)
    scores = np.asarray(scores, dtype=float)
    states = np.asarray(states, dtype=int)
    intervals = sorted((float(a), float(b)) for a, b in target_intervals)[:max_targets]
    if not intervals:
        return times, scores, states, list(target_intervals)

    out_t, out_s, out_y = [], [], []
    out_intervals = []
    cursor = 0.0

    for a, b in intervals:
        seg_start = max(float(times[0]), a - pre_s)
        seg_stop = min(float(times[-1]), b + post_s)
        mask = (times >= seg_start) & (times <= seg_stop)
        if not mask.any():
            continue

        tt = times[mask]
        ss = scores[mask]
        yy = states[mask]
        local_t = cursor + (tt - seg_start)

        out_t.append(local_t)
        out_s.append(ss)
        out_y.append(yy)
        out_intervals.append((cursor + (a - seg_start), cursor + (b - seg_start)))

        # Next snippet starts immediately after this one.  Its 2 s pre-target
        # context already provides visible NONE time before the next obstacle.
        cursor = float(local_t[-1]) + (float(np.median(np.diff(tt))) if len(tt) > 1 else 0.25)

    if not out_t:
        return times, scores, states, intervals
    return np.concatenate(out_t), np.concatenate(out_s), np.concatenate(out_y), out_intervals


def run_replay_game(
    times,
    scores,
    states,
    threshold,
    confirm=2,
    cooldown_s=1.0,
    speed=3.0,
    target_intervals=None,
    compact=True,
    max_targets=5,
    pre_target_s=2.0,
    post_target_s=1.5,
    window_s=None,
    channels=None,
):
    pygame = require_pygame()
    from .controller import decode_score_stream
    from .metrics import event_action_metrics

    import numpy as np

    times = np.asarray(times, dtype=float)
    scores = np.asarray(scores, dtype=float)
    states = np.asarray(states, dtype=int)

    # Prefer true target onsets from dataset metadata. Fallback to rising edges.
    if target_intervals:
        target_intervals = [(float(a), float(b)) for a, b in target_intervals]
    else:
        rising = []
        prev = 0
        for t, s in zip(times, states):
            if s == 1 and prev != 1:
                rising.append(float(t))
            if s >= 0:
                prev = s
        target_intervals = [(t, t + 5.0) for t in rising]

    if compact and target_intervals:
        times, scores, states, target_intervals = _compact_event_replay(
            times, scores, states, target_intervals,
            pre_s=pre_target_s, post_s=post_target_s, max_targets=max_targets,
        )

    rising = [float(a) for a, _ in target_intervals]

    pygame.init()
    W, H = 960, 420
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("BCI SSVEP — JUMP / NONE")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 22)
    small = pygame.font.SysFont("Arial", 17)

    ground = H - 70
    px, py = 140, ground - 32
    vy = 0.0
    # The recorded decoder typically needs ~2-4 s of target evidence.
    # Give the avatar a deliberately forgiving, long jump so that a valid
    # decision within the 5 s target block can actually clear the obstacle.
    gravity = 500.0
    jump_v = -650.0
    # Decode the compact score stream once, at its native 0.25 s score cadence.
    # Replay speed and monitor refresh rate must never change BCI decisions.
    decisions, action_flags, action_times = decode_score_stream(
        times, scores, threshold,
        confirm=confirm, cooldown_s=cooldown_s
    )

    # Which target blocks have at least one valid controller action?
    detected_by_target = []
    for a, b in target_intervals:
        detected_by_target.append(any(a <= t <= b for t in action_times))

    obstacle_x = []

    # Each obstacle is spawned at the TRUE target onset, but is timed to reach
    # the avatar ~4.5 s later (near the end of the 5 s SSVEP block).  This is an
    # environment choice only; target labels are never given to the decoder.
    obstacle_spawn_x = float(W + 30)
    obstacle_collision_x = float(px + 28)
    obstacle_impact_delay_s = 5.0
    obstacle_speed_px = (obstacle_spawn_x - obstacle_collision_x) / obstacle_impact_delay_s
    spawned = 0
    game_hits = game_collisions = 0
    last_t = float(times[0]) if len(times) else 0.0
    idx = 0
    running = True

    end_t = float(times[-1]) if len(times) else 0.0
    while running and len(times):
        dt_real = clock.tick(60) / 1000.0
        sim_dt = dt_real * float(speed)
        target_t = min(last_t + sim_dt, end_t)
        while idx + 1 < len(times) and times[idx + 1] <= target_t:
            idx += 1
        t = float(times[idx])
        score = float(scores[idx])
        last_t = target_t

        while spawned < len(rising) and rising[spawned] <= t:
            obstacle_x.append([obstacle_spawn_x, spawned])
            spawned += 1

        decision = decisions[idx]
        action = bool(action_flags[idx])
        on_ground = py >= ground - 32 - 1
        if action and on_ground:
            vy = jump_v

        # Accelerate the whole simulation together with EEG replay.  Otherwise
        # obstacles would move faster but the jump physics would remain real-time.
        py += vy * sim_dt
        vy += gravity * sim_dt
        if py >= ground - 32:
            py = ground - 32
            vy = 0.0

        for obs in obstacle_x:
            obs[0] -= obstacle_speed_px * sim_dt

        kept = []
        for ox, target_idx in obstacle_x:
            # The obstacle result follows the BCI event logic:
            # a valid JUMP anywhere in that target block clears it.
            # The decorative jump arc does not redefine correctness.
            if ox <= px + 28:
                a, b = target_intervals[target_idx]
                detected_before_deadline = any(
                    a <= at <= min(t, b) for at in action_times
                )
                if detected_before_deadline:
                    game_hits += 1
                else:
                    game_collisions += 1
                continue
            kept.append([ox, target_idx])
        obstacle_x = kept

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

        screen.fill((247, 244, 235))
        pygame.draw.line(screen, (40, 40, 40), (0, ground), (W, ground), 3)
        pygame.draw.rect(screen, (31, 86, 117), (px, int(py), 32, 32), border_radius=4)
        for ox, target_idx in obstacle_x:
            a, b = target_intervals[target_idx]
            target_detected_so_far = any(a <= at <= min(t, b) for at in action_times)
            obstacle_color = (52, 145, 78) if target_detected_so_far else (225, 110, 37)
            pygame.draw.rect(screen, obstacle_color, (int(ox), ground-58, 30, 58))

        occurred_actions = [at for at in action_times if at <= t]
        interim = event_action_metrics(target_intervals, occurred_actions, duration_s=max(t, 1.0))
        med = interim["median_latency_s"]
        med_txt = "—" if med != med else f"{med:.2f}s"
        round_idx = min(spawned + 1, max(len(rising), 1)) if spawned < len(rising) else len(rising)
        challenge_score = interim["detected_blocks"] - interim["false_jumps"]
        hud = (
            f"round {round_idx}/{len(rising)}   score={score:.3f}   "
            f"{decision}{' → ACTION' if action else ''}   "
            f"targets={interim['detected_blocks']}/{interim['target_blocks']}   "
            f"false={interim['false_jumps']}   BCI={challenge_score:+d}"
        )
        screen.blit(font.render(hud, True, (25,25,25)), (24, 20))

        params = (
            f"window={window_s:.2f}s   threshold={threshold:.2f}   "
            f"channels={','.join(channels or [])}   replay x{speed:g}   latency={med_txt}"
            if window_s is not None else
            f"threshold={threshold:.2f}   replay x{speed:g}   latency={med_txt}"
        )
        screen.blit(small.render(params, True, (65,65,65)), (24, 48))

        # Score gauge makes the invisible decoder state visible.
        gx, gy, gw, gh = 24, 78, 300, 16
        pygame.draw.rect(screen, (205,205,205), (gx, gy, gw, gh), border_radius=4)
        score_clamped = max(0.0, min(1.0, score))
        pygame.draw.rect(screen, (106, 61, 138), (gx, gy, int(gw*score_clamped), gh), border_radius=4)
        tx = gx + int(gw * max(0.0, min(1.0, threshold)))
        pygame.draw.line(screen, (30, 120, 55), (tx, gy-5), (tx, gy+gh+5), 3)
        screen.blit(small.render(f"threshold={threshold:.2f}   ESC/Q = quitter", True, (70,70,70)), (gx, gy+24))

        pygame.display.flip()

        if target_t >= end_t and idx >= len(times) - 1:
            break

    pygame.quit()
    duration = float(times[-1] - times[0]) if len(times) > 1 else 0.0
    result = event_action_metrics(target_intervals, action_times, duration_s=duration)
    result.pop("commands_per_min", None)  # compact timeline: rate/min would be artificial
    result.update({
        "game_obstacles_cleared": int(game_hits),
        "game_collisions": int(game_collisions),
        "bci_score": int(result["detected_blocks"] - result["false_jumps"]),
        "replay_duration_s": duration,
        "replay_speed": float(speed),
        "window_s_used": float(window_s) if window_s is not None else None,
        "threshold_used": float(threshold),
        "metric_scope": "compact_replay_only",
    })
    return result
