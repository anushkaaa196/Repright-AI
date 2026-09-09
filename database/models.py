"""REPRIGHT AI - Database Models.

Dataclass representations for Users, Workout Sessions, and Repetition Records.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
import sqlite3


@dataclass
class User:
    """Represents a registered REPRIGHT AI athlete."""
    id: int
    name: str
    email: str
    password_hash: str
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    fitness_goal: str = "GENERAL_FITNESS"
    created_at: str = ""
    updated_at: str = ""

    @property
    def bmi(self) -> Optional[float]:
        """Calculates Body Mass Index (BMI) if height and weight are provided."""
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = self.height_cm / 100.0
            return round(self.weight_kg / (height_m * height_m), 1)
        return None

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "User":
        """Instantiates a User from an sqlite3.Row."""
        return cls(
            id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            height_cm=row["height_cm"],
            weight_kg=row["weight_kg"],
            fitness_goal=row["fitness_goal"] or "GENERAL_FITNESS",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> Dict[str, Any]:
        """Converts user instance to serializable dictionary (omitting sensitive password)."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "height_cm": self.height_cm,
            "weight_kg": self.weight_kg,
            "bmi": self.bmi,
            "fitness_goal": self.fitness_goal,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class RepRecord:
    """Represents a single completed repetition with multidimensional biomechanical telemetry."""
    id: int
    session_id: int
    rep_number: int
    quality_score: float
    range_of_motion: float = 100.0
    joint_alignment: float = 100.0
    core_stability: float = 100.0
    movement_control: float = 100.0
    movement_cadence: float = 100.0
    is_clean: bool = True
    rep_result: str = "CLEAN"
    created_at: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "RepRecord":
        """Instantiates a RepRecord from an sqlite3.Row."""
        return cls(
            id=row["id"],
            session_id=row["session_id"],
            rep_number=row["rep_number"],
            quality_score=float(row["quality_score"]),
            range_of_motion=float(row["range_of_motion"]),
            joint_alignment=float(row["joint_alignment"]),
            core_stability=float(row["core_stability"]),
            movement_control=float(row["movement_control"]),
            movement_cadence=float(row["movement_cadence"]),
            is_clean=bool(row["is_clean"]),
            rep_result=row["rep_result"] or "CLEAN",
            created_at=row["created_at"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "rep_number": self.rep_number,
            "quality_score": self.quality_score,
            "range_of_motion": self.range_of_motion,
            "joint_alignment": self.joint_alignment,
            "core_stability": self.core_stability,
            "movement_control": self.movement_control,
            "movement_cadence": self.movement_cadence,
            "is_clean": self.is_clean,
            "rep_result": self.rep_result,
            "created_at": self.created_at,
        }


@dataclass
class WorkoutSession:
    """Represents an archived workout session with full telemetry and debrief insights."""
    id: int
    user_id: int
    exercise_name: str
    started_at: str
    completed_at: str
    duration_seconds: int = 0
    total_reps: int = 0
    clean_reps: int = 0
    average_quality: float = 0.0
    best_rep_quality: float = 0.0
    consistency_score: float = 0.0
    stability_score: float = 0.0
    fatigue_level: str = "LOW"
    risk_level: str = "LOW"
    session_trajectory: str = "STABLE"
    created_at: str = ""
    reps: List[RepRecord] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: sqlite3.Row, reps: Optional[List[RepRecord]] = None) -> "WorkoutSession":
        """Instantiates a WorkoutSession from an sqlite3.Row."""
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            exercise_name=row["exercise_name"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            duration_seconds=row["duration_seconds"],
            total_reps=row["total_reps"],
            clean_reps=row["clean_reps"],
            average_quality=float(row["average_quality"]),
            best_rep_quality=float(row["best_rep_quality"]),
            consistency_score=float(row["consistency_score"]),
            stability_score=float(row["stability_score"]),
            fatigue_level=row["fatigue_level"] or "LOW",
            risk_level=row["risk_level"] or "LOW",
            session_trajectory=row["session_trajectory"] or "STABLE",
            created_at=row["created_at"],
            reps=reps or [],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "exercise_name": self.exercise_name,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": self.duration_seconds,
            "total_reps": self.total_reps,
            "clean_reps": self.clean_reps,
            "average_quality": self.average_quality,
            "best_rep_quality": self.best_rep_quality,
            "consistency_score": self.consistency_score,
            "stability_score": self.stability_score,
            "fatigue_level": self.fatigue_level,
            "risk_level": self.risk_level,
            "session_trajectory": self.session_trajectory,
            "created_at": self.created_at,
            "rep_count": len(self.reps),
        }


@dataclass
class NutritionProfile:
    """Represents user dietary baseline and lifestyle parameters."""
    id: int
    user_id: int
    age: int = 25
    gender: str = "MALE"
    activity_level: str = "MODERATELY_ACTIVE"
    diet_preference: str = "VEGETARIAN"
    restrictions: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "NutritionProfile":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            age=int(row["age"] or 25),
            gender=row["gender"] or "MALE",
            activity_level=row["activity_level"] or "MODERATELY_ACTIVE",
            diet_preference=row["diet_preference"] or "VEGETARIAN",
            restrictions=row["restrictions"] or "",
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "age": self.age,
            "gender": self.gender,
            "activity_level": self.activity_level,
            "diet_preference": self.diet_preference,
            "restrictions": self.restrictions,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


@dataclass
class NutritionPlan:
    """Represents a generated and archived nutritional plan."""
    id: int
    user_id: int
    calorie_target: int
    protein_target: float
    carb_target: float
    fat_target: float
    bmi: float
    bmr: float
    tdee: float
    goal: str
    meal_plan_json: str = "{}"
    generated_at: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "NutritionPlan":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            calorie_target=int(row["calorie_target"]),
            protein_target=float(row["protein_target"]),
            carb_target=float(row["carb_target"]),
            fat_target=float(row["fat_target"]),
            bmi=float(row["bmi"]),
            bmr=float(row["bmr"]),
            tdee=float(row["tdee"]),
            goal=row["goal"],
            meal_plan_json=row["meal_plan_json"] or "{}",
            generated_at=row["generated_at"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "calorie_target": self.calorie_target,
            "protein_target": self.protein_target,
            "carb_target": self.carb_target,
            "fat_target": self.fat_target,
            "bmi": self.bmi,
            "bmr": self.bmr,
            "tdee": self.tdee,
            "goal": self.goal,
            "meal_plan_json": self.meal_plan_json,
            "generated_at": self.generated_at
        }


@dataclass
class HydrationLog:
    """Represents daily water consumption tracking."""
    id: int
    user_id: int
    date: str
    target_ml: int
    consumed_ml: int = 0
    updated_at: str = ""

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "HydrationLog":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            date=row["date"],
            target_ml=int(row["target_ml"]),
            consumed_ml=int(row["consumed_ml"] or 0),
            updated_at=row["updated_at"]
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "target_ml": self.target_ml,
            "consumed_ml": self.consumed_ml,
            "updated_at": self.updated_at
        }

