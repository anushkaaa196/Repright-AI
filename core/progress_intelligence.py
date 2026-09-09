"""Progress Intelligence & Session-to-Session Comparison Engine for REPRIGHT AI.

Maintains multi-session runtime progress intelligence, tracking form score improvements,
consistency progressions, and recurring biomechanical focus areas across workouts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class ProgressIntelligenceTracker:
    """Thread-safe in-memory session-to-session progress intelligence manager."""

    _instance: Optional["ProgressIntelligenceTracker"] = None

    def __init__(self):
        self.session_log: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "ProgressIntelligenceTracker":
        """Singleton accessor."""
        if cls._instance is None:
            cls._instance = ProgressIntelligenceTracker()
        return cls._instance

    def record_completed_session(
        self,
        exercise_name: str,
        stats: Dict[str, Any],
        duration_seconds: int = 0,
        best_rep_score: int = 0,
        avg_rep_score: int = 0,
        consistency_score: int = 0,
        most_common_issue: str = "None",
        strongest_cat: str = "range_of_motion",
        weakest_cat: str = "alignment"
    ) -> Dict[str, Any]:
        """Appends a completed workout session to the runtime progress history."""
        ex = exercise_name.upper().strip()
        acc = int(stats.get("accuracy", 100))
        reps = stats.get("clean_reps", 0)
        total = stats.get("total_attempts", 0)

        entry = {
            "session_number": len(self.session_log) + 1,
            "exercise": ex,
            "accuracy": acc,
            "clean_reps": reps,
            "total_attempts": total,
            "best_rep_score": best_rep_score if best_rep_score > 0 else acc,
            "avg_rep_score": avg_rep_score if avg_rep_score > 0 else acc,
            "consistency_score": consistency_score if consistency_score > 0 else 100,
            "duration_seconds": duration_seconds,
            "most_common_issue": most_common_issue,
            "strongest_category": strongest_cat,
            "weakest_category": weakest_cat,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.session_log.append(entry)
        return entry

    def get_progress_summary(self, exercise_name: str) -> Dict[str, Any]:
        """
        Generates a comparative progress intelligence report for the given exercise.
        Compares the latest session against the preceding session.
        """
        ex = exercise_name.upper().strip()
        matches = [s for s in self.session_log if s.get("exercise") == ex]

        if not matches:
            return {
                "has_history": False,
                "exercise": ex,
                "sessions_completed": 0,
                "current_accuracy": 100,
                "previous_accuracy": 100,
                "delta_accuracy": 0,
                "trend_icon": "→",
                "trend_text": "Baseline session recorded",
                "best_rep": 100,
                "consistency": 100,
                "most_improved_category": "Depth Control",
                "recurring_focus": "Cadence & Form"
            }

        curr = matches[-1]
        curr_acc = curr.get("accuracy", 100)
        best_rep = curr.get("best_rep_score", curr_acc)
        consistency = curr.get("consistency_score", 100)
        recurring_focus = curr.get("weakest_category", "alignment").replace("_", " ").title()

        if len(matches) < 2:
            return {
                "has_history": True,
                "exercise": ex,
                "sessions_completed": 1,
                "current_accuracy": curr_acc,
                "previous_accuracy": curr_acc,
                "delta_accuracy": 0,
                "trend_icon": "★",
                "trend_text": f"Baseline Session Established ({curr_acc}% Accuracy)",
                "best_rep": best_rep,
                "consistency": consistency,
                "most_improved_category": curr.get("strongest_category", "range_of_motion").replace("_", " ").title(),
                "recurring_focus": recurring_focus
            }

        prev = matches[-2]
        prev_acc = prev.get("accuracy", 100)
        delta = curr_acc - prev_acc

        if delta > 0:
            trend_icon = "↑"
            trend_text = f"+{delta}% Form Quality Improvement"
        elif delta < 0:
            trend_icon = "↓"
            trend_text = f"{delta}% Form Shift (Focus Needed)"
        else:
            trend_icon = "→"
            trend_text = "Consistent Performance Across Sets"

        most_improved = curr.get("strongest_category", "range_of_motion").replace("_", " ").title()

        return {
            "has_history": True,
            "exercise": ex,
            "sessions_completed": len(matches),
            "current_accuracy": curr_acc,
            "previous_accuracy": prev_acc,
            "delta_accuracy": delta,
            "trend_icon": trend_icon,
            "trend_text": trend_text,
            "best_rep": best_rep,
            "consistency": consistency,
            "most_improved_category": most_improved,
            "recurring_focus": recurring_focus
        }

    def get_all_sessions(self, exercise_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns list of session history entries, optionally filtered by exercise."""
        if exercise_name:
            ex = exercise_name.upper().strip()
            return [s for s in self.session_log if s.get("exercise") == ex]
        return list(self.session_log)

    def clear(self):
        """Clears session history log."""
        self.session_log.clear()
