"""Movement Phase Analysis Engine for REPRIGHT AI.

Performs deterministic, real-time biomechanical phase detection across exercise repetitions.
Analyzes joint angles, movement direction, angle velocity, and telemetry states.
"""

from typing import Dict, Any, List, Optional
from collections import deque
import time

from core.exercise_registry import is_active_ai_supported


# Phase schemas per exercise
PHASE_DEFINITIONS: Dict[str, List[Dict[str, str]]] = {
    "SQUAT": [
        {"id": "START_POSITION", "label": "START", "focus": "Brace core and set stable tripod foot stance."},
        {"id": "DESCENT", "label": "DESCENT", "focus": "Controlled 2s eccentric lowering; knees tracking toes."},
        {"id": "BOTTOM_POSITION", "label": "BOTTOM", "focus": "Active parallel turnaround; avoid passive sitting."},
        {"id": "ASCENT", "label": "ASCENT", "focus": "Drive through midfoot; maintain proud chest angle."},
        {"id": "LOCKOUT", "label": "LOCKOUT", "focus": "Full hip extension at top with neutral spine."}
    ],
    "DEADLIFT": [
        {"id": "SETUP", "label": "SETUP", "focus": "Shins over midfoot, engage lats, neutral spinal posture."},
        {"id": "INITIATION", "label": "INITIATION", "focus": "Push floor away with legs; bar tight against shins."},
        {"id": "ASCENT", "label": "ASCENT", "focus": "Simultaneous knee and hip extension keeping spine locked."},
        {"id": "LOCKOUT", "label": "LOCKOUT", "focus": "Tall standing lockout; avoid lumbar hyperextension."},
        {"id": "DESCENT", "label": "DESCENT", "focus": "Controlled hip hinge return to ground."}
    ],
    "BICEP_CURL": [
        {"id": "EXTENDED", "label": "EXTENDED", "focus": "Arms fully lengthened at side; elbows pinned at ribs."},
        {"id": "CONCENTRIC_CURL", "label": "CONCENTRIC", "focus": "Smooth upward curl powered strictly by biceps."},
        {"id": "PEAK_CONTRACTION", "label": "PEAK", "focus": "Squeeze biceps at apex; eliminate torso momentum."},
        {"id": "ECCENTRIC_RETURN", "label": "ECCENTRIC", "focus": "Controlled lowering back to full arm extension."}
    ],
    # Reference schemas for guided exercises
    "PUSH_UP": [
        {"id": "PLANK_SETUP", "label": "PLANK", "focus": "Rigid plank line; hands slightly outside shoulders."},
        {"id": "DESCENT", "label": "DESCENT", "focus": "Elbows at 45°; lower chest until fists-width from floor."},
        {"id": "BOTTOM_INFLECTION", "label": "BOTTOM", "focus": "Touch-and-go turnaround; maintain flat lumbar."},
        {"id": "PRESS_ASCENT", "label": "PRESS", "focus": "Drive straight up into full elbow extension."}
    ],
    "LUNGE": [
        {"id": "STANDING_SETUP", "label": "SETUP", "focus": "Feet hip-width apart; shoulders back and down."},
        {"id": "STRIDE_DESCENT", "label": "STRIDE", "focus": "Step forward; lower back knee toward floor."},
        {"id": "SPLIT_BOTTOM", "label": "BOTTOM", "focus": "Both knees at ~90°; front knee behind toes."},
        {"id": "DRIVE_RETURN", "label": "RETURN", "focus": "Push back off front foot to starting stance."}
    ],
    "PLANK": [
        {"id": "PRONE_SETUP", "label": "SETUP", "focus": "Elbows under shoulders; forearms parallel."},
        {"id": "CORE_BRACE", "label": "BRACE", "focus": "Squeeze glutes and quads; pull belly button in."},
        {"id": "ISOMETRIC_HOLD", "label": "HOLD", "focus": "Maintain straight head-to-heel biomechanical line."},
        {"id": "CONTROLLED_RELEASE", "label": "RELEASE", "focus": "Controlled lowering upon session completion."}
    ],
    "SHOULDER_PRESS": [
        {"id": "RACK_POSITION", "label": "RACK", "focus": "Weights at shoulder level; forearms vertical."},
        {"id": "OVERHEAD_DRIVE", "label": "DRIVE", "focus": "Press straight overhead without arching lower back."},
        {"id": "OVERHEAD_LOCKOUT", "label": "LOCKOUT", "focus": "Biceps beside ears; ribcage pulled down."},
        {"id": "ECCENTRIC_DESCENT", "label": "DESCENT", "focus": "Control descent back down to collarbone height."}
    ]
}


class MovementPhaseEngine:
    """Tracks joint angle transitions and telemetry to detect movement phases in real time."""

    def __init__(self):
        self._angle_history: deque = deque(maxlen=15)
        self._time_history: deque = deque(maxlen=15)
        self._current_phase_idx: int = 0
        self._last_exercise: Optional[str] = None
        self._rep_cycle_count: int = 0

    def reset(self, exercise_name: Optional[str] = None):
        """Resets phase tracking buffer."""
        self._angle_history.clear()
        self._time_history.clear()
        self._current_phase_idx = 0
        if exercise_name:
            self._last_exercise = exercise_name.upper().strip()

    def update(
        self,
        exercise_name: str,
        current_angle: Optional[float] = None,
        feedback_msg: str = "",
        stats_snapshot: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processes current frame signals to determine active movement phase.
        
        Returns:
            MovementPhaseResult dictionary.
        """
        ex = exercise_name.upper().strip()
        if ex != self._last_exercise:
            self.reset(ex)

        is_active = is_active_ai_supported(ex)
        phase_defs = PHASE_DEFINITIONS.get(ex, PHASE_DEFINITIONS["SQUAT"])
        phase_labels = [p["label"] for p in phase_defs]
        total_phases = len(phase_defs)

        now = time.time()

        # Handle Guided Reference Mode (Technical Honesty)
        if not is_active:
            return {
                "exercise": ex,
                "current_phase": phase_defs[0]["id"],
                "phase_label": phase_defs[0]["label"],
                "phase_index": 0,
                "total_phases": total_phases,
                "phase_list": phase_labels,
                "phase_progress": 100,
                "movement_direction": "STATIONARY",
                "confidence": 1.0,
                "coaching_focus": phase_defs[0]["focus"],
                "is_guided": True,
                "note": "GUIDED TRAINING MODE • REFERENCE BIOMECHANICAL TARGETS"
            }

        # Active AI Exercises: Evaluate live movement
        if current_angle is not None:
            self._angle_history.append(float(current_angle))
            self._time_history.append(now)

        # Compute movement direction and velocity
        direction = "STATIONARY"
        velocity = 0.0
        if len(self._angle_history) >= 4:
            recent_delta = self._angle_history[-1] - self._angle_history[-4]
            dt = max(self._time_history[-1] - self._time_history[-4], 0.001)
            velocity = recent_delta / dt

            if abs(velocity) > 8.0:  # degrees per second threshold
                direction = "UP" if velocity > 0 else "DOWN"

        msg_lower = feedback_msg.lower() if feedback_msg else ""
        angle = self._angle_history[-1] if self._angle_history else 160.0

        # Deterministic Phase Mapping per Exercise
        phase_idx = 0
        progress_pct = 50

        if ex == "SQUAT":
            # Standing baseline ~155-170, Depth ~90-100
            if "depth" in msg_lower or angle <= 102.0:
                phase_idx = 2  # BOTTOM_POSITION
                progress_pct = 100
            elif direction == "DOWN" or (105.0 < angle < 145.0 and direction != "UP"):
                phase_idx = 1  # DESCENT
                progress_pct = max(0, min(100, int((155.0 - angle) / (155.0 - 100.0) * 100)))
            elif direction == "UP" or ("drive" in msg_lower or (angle > 105.0 and self._current_phase_idx in (2, 3))):
                if angle >= 150.0:
                    phase_idx = 4  # LOCKOUT
                    progress_pct = 100
                else:
                    phase_idx = 3  # ASCENT
                    progress_pct = max(0, min(100, int((angle - 100.0) / (155.0 - 100.0) * 100)))
            elif angle >= 148.0:
                phase_idx = 0 if self._current_phase_idx in (0, 4) else 4
                progress_pct = 100
            else:
                phase_idx = self._current_phase_idx
                progress_pct = 50

        elif ex == "DEADLIFT":
            # Hinge initiation, pull ascent, lockout
            if "lockout" in msg_lower or (angle >= 165.0 and direction == "STATIONARY"):
                phase_idx = 3  # LOCKOUT
                progress_pct = 100
            elif direction == "UP" or ("drive" in msg_lower or "pull" in msg_lower):
                phase_idx = 2  # ASCENT
                progress_pct = max(0, min(100, int((angle - 100.0) / (165.0 - 100.0) * 100)))
            elif direction == "DOWN" or "hinge" in msg_lower:
                phase_idx = 4 if self._current_phase_idx in (3, 4) else 1  # DESCENT or INITIATION
                progress_pct = max(0, min(100, int((165.0 - angle) / (165.0 - 100.0) * 100)))
            elif angle >= 155.0:
                phase_idx = 0  # SETUP
                progress_pct = 100
            else:
                phase_idx = self._current_phase_idx
                progress_pct = 50

        elif ex == "BICEP_CURL":
            # Extension ~160, Flexion ~55
            if angle <= 65.0 or "peak" in msg_lower:
                phase_idx = 2  # PEAK_CONTRACTION
                progress_pct = 100
            elif direction == "DOWN" or (angle < 145.0 and self._current_phase_idx in (0, 1)):
                # Arm angle decreasing = concentric curl
                phase_idx = 1  # CONCENTRIC_CURL
                progress_pct = max(0, min(100, int((155.0 - angle) / (155.0 - 65.0) * 100)))
            elif direction == "UP" or (angle > 70.0 and self._current_phase_idx in (2, 3)):
                # Arm angle increasing = eccentric lowering
                if angle >= 150.0:
                    phase_idx = 0  # EXTENDED
                    progress_pct = 100
                else:
                    phase_idx = 3  # ECCENTRIC_RETURN
                    progress_pct = max(0, min(100, int((angle - 65.0) / (155.0 - 65.0) * 100)))
            else:
                phase_idx = 0  # EXTENDED
                progress_pct = 100

        self._current_phase_idx = max(0, min(total_phases - 1, phase_idx))
        active_phase_data = phase_defs[self._current_phase_idx]

        return {
            "exercise": ex,
            "current_phase": active_phase_data["id"],
            "phase_label": active_phase_data["label"],
            "phase_index": self._current_phase_idx,
            "total_phases": total_phases,
            "phase_list": phase_labels,
            "phase_progress": max(0, min(100, progress_pct)),
            "movement_direction": direction,
            "velocity_deg_s": round(velocity, 1),
            "confidence": 0.95,
            "coaching_focus": active_phase_data["focus"],
            "is_guided": False,
            "note": "AI-ESTIMATED MOVEMENT PHASE"
        }


# Singleton engine instance
_phase_engine_instance = MovementPhaseEngine()


def get_movement_phase_engine() -> MovementPhaseEngine:
    """Returns the singleton instance of the MovementPhaseEngine."""
    return _phase_engine_instance
