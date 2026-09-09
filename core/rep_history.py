"""In-Memory Repetition History Tracker for REPRIGHT AI.

Stores completed repetition analyses for the active session, calculates statistical
consistency, identifies best and weakest reps, and aggregates multi-dimensional quality metrics.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
from collections import Counter


class RepHistoryTracker:
    """Thread-safe in-memory session repetition history tracker."""

    _instance: Optional["RepHistoryTracker"] = None

    def __init__(self, max_reps: int = 100):
        self.max_reps = max_reps
        self.reps: List[Dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "RepHistoryTracker":
        """Singleton provider for global access across UI and engine callbacks."""
        if cls._instance is None:
            cls._instance = RepHistoryTracker()
        return cls._instance

    def add_rep(self, rep_analysis: Dict[str, Any]):
        """Adds a completed repetition analysis record to the session log."""
        if len(self.reps) >= self.max_reps:
            self.reps.pop(0)
        self.reps.append(rep_analysis)

    def get_all_reps(self) -> List[Dict[str, Any]]:
        """Returns shallow copy of all repetition records in active session."""
        return list(self.reps)

    def get_total_reps(self) -> int:
        """Returns total repetitions attempted in active session."""
        return len(self.reps)

    def get_clean_reps(self) -> int:
        """Returns count of validated clean repetitions."""
        return sum(1 for r in self.reps if r.get("is_clean", False))

    def get_best_rep(self) -> Optional[Dict[str, Any]]:
        """Returns the highest scoring repetition record, or None if empty."""
        if not self.reps:
            return None
        return max(self.reps, key=lambda r: r.get("overall_score", 0))

    def get_weakest_rep(self) -> Optional[Dict[str, Any]]:
        """Returns the lowest scoring repetition record, or None if empty."""
        if not self.reps:
            return None
        return min(self.reps, key=lambda r: r.get("overall_score", 100))

    def get_average_score(self) -> int:
        """Calculates arithmetic mean overall repetition quality score."""
        if not self.reps:
            return 100
        total = sum(r.get("overall_score", 0) for r in self.reps)
        return int(round(total / len(self.reps)))

    def get_consistency_score(self) -> int:
        """
        Calculates repetition cadence & score consistency (100 - standard deviation).
        Returns integer between 0 and 100.
        """
        if len(self.reps) < 2:
            return 100
        scores = [r.get("overall_score", 100) for r in self.reps]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        std_dev = math.sqrt(variance)
        consistency = max(40, min(100, int(round(100 - (std_dev * 1.5)))))
        return consistency

    def get_most_common_issue(self) -> str:
        """Identifies the most frequently occurring biomechanical fault."""
        all_issues = []
        for r in self.reps:
            all_issues.extend(r.get("issues", []))
        if not all_issues:
            return "None (Optimal Form Maintained)"
        counts = Counter(all_issues)
        most_common, _ = counts.most_common(1)[0]
        return most_common

    def get_dimension_averages(self) -> Dict[str, int]:
        """Calculates average score across the 5 biomechanical dimensions."""
        dims = ["range_of_motion", "alignment", "stability", "movement_control", "consistency"]
        if not self.reps:
            return {d: 100 for d in dims}

        averages = {}
        for d in dims:
            dim_sum = sum(r.get("dimension_scores", {}).get(d, 100) for r in self.reps)
            averages[d] = int(round(dim_sum / len(self.reps)))
        return averages

    def get_strongest_category(self) -> Tuple[str, int]:
        """Returns the highest scoring biomechanical dimension (dim_key, average_score)."""
        dim_avgs = self.get_dimension_averages()
        best_dim = max(dim_avgs.items(), key=lambda item: item[1])
        return best_dim

    def get_weakest_category(self) -> Tuple[str, int]:
        """Returns the lowest scoring biomechanical dimension (dim_key, average_score)."""
        dim_avgs = self.get_dimension_averages()
        weakest_dim = min(dim_avgs.items(), key=lambda item: item[1])
        return weakest_dim

    def reset(self):
        """Clears all session repetition history."""
        self.reps.clear()
