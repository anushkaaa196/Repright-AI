"""REPRIGHT AI - Workout Repository.

Data Access Object for Workout Sessions, Biomechanical Repetition Telemetry,
and Aggregate Athlete Analytics.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import sqlite3
from database.db_manager import get_connection
from database.models import WorkoutSession, RepRecord


class WorkoutRepository:
    """Repository managing WorkoutSession and RepRecord persistence in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    def save_workout_session(
        self,
        user_id: int,
        exercise_name: str,
        started_at: str,
        completed_at: str,
        duration_seconds: int,
        total_reps: int,
        clean_reps: int,
        average_quality: float,
        best_rep_quality: float,
        consistency_score: float,
        stability_score: float = 0.0,
        fatigue_level: str = "LOW",
        risk_level: str = "LOW",
        session_trajectory: str = "STABLE",
        rep_records: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """Saves a workout session debrief and its associated repetition telemetry."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO workout_sessions (
                        user_id, exercise_name, started_at, completed_at,
                        duration_seconds, total_reps, clean_reps,
                        average_quality, best_rep_quality, consistency_score,
                        stability_score, fatigue_level, risk_level,
                        session_trajectory, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        exercise_name.upper(),
                        started_at,
                        completed_at,
                        duration_seconds,
                        total_reps,
                        clean_reps,
                        round(float(average_quality), 2),
                        round(float(best_rep_quality), 2),
                        round(float(consistency_score), 2),
                        round(float(stability_score), 2),
                        fatigue_level,
                        risk_level,
                        session_trajectory,
                        now
                    )
                )
                session_id = cursor.lastrowid

                # Save rep-by-rep records if provided
                if rep_records:
                    rep_rows = []
                    for r in rep_records:
                        # Extract dimension breakdown (support dict or RepAnalysis)
                        rom = r.get("range_of_motion", 100.0)
                        alignment = r.get("joint_alignment", 100.0)
                        stability = r.get("core_stability", 100.0)
                        control = r.get("movement_control", 100.0)
                        cadence = r.get("movement_cadence", 100.0)

                        # Check nested dimensions dict if present
                        if "dimensions" in r and isinstance(r["dimensions"], dict):
                            dims = r["dimensions"]
                            rom = dims.get("range_of_motion", rom)
                            alignment = dims.get("joint_alignment", alignment)
                            stability = dims.get("core_stability", stability)
                            control = dims.get("movement_control", control)
                            cadence = dims.get("movement_cadence", cadence)

                        rep_rows.append((
                            session_id,
                            int(r.get("rep_number", 1)),
                            round(float(r.get("quality_score", r.get("overall_score", 100.0))), 2),
                            round(float(rom), 2),
                            round(float(alignment), 2),
                            round(float(stability), 2),
                            round(float(control), 2),
                            round(float(cadence), 2),
                            1 if r.get("is_clean", True) else 0,
                            str(r.get("rep_result", "CLEAN")),
                            now
                        ))

                    conn.executemany(
                        """
                        INSERT INTO rep_history (
                            session_id, rep_number, quality_score,
                            range_of_motion, joint_alignment, core_stability,
                            movement_control, movement_cadence,
                            is_clean, rep_result, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        rep_rows
                    )

                return session_id
        finally:
            conn.close()

    def get_workout_sessions_by_user(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        exercise: Optional[str] = None
    ) -> List[WorkoutSession]:
        """Retrieves past workout sessions for a given user, newest first."""
        conn = self._get_conn()
        try:
            if exercise:
                query = """
                    SELECT * FROM workout_sessions
                    WHERE user_id = ? AND exercise_name = ?
                    ORDER BY id DESC LIMIT ? OFFSET ?
                """
                rows = conn.execute(query, (user_id, exercise.upper(), limit, offset)).fetchall()
            else:
                query = """
                    SELECT * FROM workout_sessions
                    WHERE user_id = ?
                    ORDER BY id DESC LIMIT ? OFFSET ?
                """
                rows = conn.execute(query, (user_id, limit, offset)).fetchall()

            return [WorkoutSession.from_row(r) for r in rows]
        finally:
            conn.close()

    def get_workout_session_by_id(
        self,
        session_id: int,
        include_reps: bool = True
    ) -> Optional[WorkoutSession]:
        """Fetches a specific workout session and optionally its rep history."""
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM workout_sessions WHERE id = ?", (session_id,)).fetchone()
            if not row:
                return None

            reps = []
            if include_reps:
                reps = self.get_rep_records_for_session(session_id)

            return WorkoutSession.from_row(row, reps=reps)
        finally:
            conn.close()

    def get_rep_records_for_session(self, session_id: int) -> List[RepRecord]:
        """Fetches all repetition records for a specific workout session."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                "SELECT * FROM rep_history WHERE session_id = ? ORDER BY rep_number ASC",
                (session_id,)
            ).fetchall()
            return [RepRecord.from_row(r) for r in rows]
        finally:
            conn.close()

    def get_user_aggregate_stats(self, user_id: int) -> Dict[str, Any]:
        """Computes aggregate athlete analytics across all recorded sessions."""
        conn = self._get_conn()
        try:
            # 1. Total sessions, total reps, clean reps, total duration, avg quality
            summary_row = conn.execute(
                """
                SELECT
                    COUNT(*) as total_workouts,
                    COALESCE(SUM(total_reps), 0) as total_reps,
                    COALESCE(SUM(clean_reps), 0) as clean_reps,
                    COALESCE(SUM(duration_seconds), 0) as total_duration,
                    COALESCE(AVG(average_quality), 0.0) as overall_avg_quality,
                    COALESCE(MAX(best_rep_quality), 0.0) as highest_rep_score,
                    COALESCE(AVG(consistency_score), 0.0) as overall_consistency
                FROM workout_sessions
                WHERE user_id = ?
                """,
                (user_id,)
            ).fetchone()

            total_workouts = summary_row["total_workouts"] if summary_row else 0
            total_reps = summary_row["total_reps"] if summary_row else 0
            clean_reps = summary_row["clean_reps"] if summary_row else 0
            total_duration = summary_row["total_duration"] if summary_row else 0
            overall_avg_quality = round(summary_row["overall_avg_quality"], 1) if summary_row else 0.0
            highest_rep_score = round(summary_row["highest_rep_score"], 1) if summary_row else 0.0
            overall_consistency = round(summary_row["overall_consistency"], 1) if summary_row else 0.0

            clean_ratio = round((clean_reps / total_reps * 100.0), 1) if total_reps > 0 else 100.0

            # 2. Most performed exercise
            best_ex_row = conn.execute(
                """
                SELECT exercise_name, COUNT(*) as cnt, AVG(average_quality) as avg_q
                FROM workout_sessions
                WHERE user_id = ?
                GROUP BY exercise_name
                ORDER BY cnt DESC, avg_q DESC
                LIMIT 1
                """,
                (user_id,)
            ).fetchone()
            best_exercise = best_ex_row["exercise_name"] if best_ex_row else "SQUAT"

            # 3. Exercise distribution breakdown
            ex_dist_rows = conn.execute(
                """
                SELECT exercise_name, COUNT(*) as session_count, SUM(clean_reps) as total_clean
                FROM workout_sessions
                WHERE user_id = ?
                GROUP BY exercise_name
                ORDER BY session_count DESC
                """,
                (user_id,)
            ).fetchall()

            exercise_breakdown = {
                r["exercise_name"]: {"sessions": r["session_count"], "clean_reps": r["total_clean"]}
                for r in ex_dist_rows
            }

            return {
                "total_workouts": total_workouts,
                "total_reps": total_reps,
                "clean_reps": clean_reps,
                "clean_ratio": clean_ratio,
                "total_duration_seconds": total_duration,
                "overall_avg_quality": overall_avg_quality,
                "highest_rep_score": highest_rep_score,
                "overall_consistency": overall_consistency,
                "best_exercise": best_exercise,
                "exercise_breakdown": exercise_breakdown
            }
        finally:
            conn.close()

    def delete_workout_session(self, session_id: int, user_id: Optional[int] = None) -> bool:
        """Deletes a workout session and cascades its rep telemetry."""
        conn = self._get_conn()
        try:
            with conn:
                if user_id is not None:
                    cursor = conn.execute(
                        "DELETE FROM workout_sessions WHERE id = ? AND user_id = ?",
                        (session_id, user_id)
                    )
                else:
                    cursor = conn.execute(
                        "DELETE FROM workout_sessions WHERE id = ?",
                        (session_id,)
                    )
                return cursor.rowcount > 0
        finally:
            conn.close()
