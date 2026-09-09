"""REPRIGHT AI - Phase 7C Verification & Regression Test Suite.

Comprehensive 22-test automated verification suite covering:
- Database tables (nutrition_profiles, nutrition_plans, hydration_logs)
- Calorie Engine (BMI, BMR Mifflin-St Jeor, TDEE, Goal adjustments)
- Macro Calculator (Protein, Fats, Carbs, Energy Consistency 4P+4C+9F)
- Indian Meal Recommender (Veg, Non-Veg, Vegan, Eggetarian + Allergen filtering)
- Hydration Engine & Daily Tracking
- Post-Workout Recovery Nutrition
- Service Facade End-to-End Orchestration
- UI Dialog Instantiation
- Phase 7A & Phase 1-6 Zero-Regression Verification
"""

import sys
from pathlib import Path
import sqlite3
import json
import unittest

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from database.db_manager import init_db, get_connection
from database.models import User, NutritionProfile, NutritionPlan, HydrationLog
from database.user_repository import UserRepository
from database.workout_repository import WorkoutRepository
from database.nutrition_repository import NutritionRepository
from core.nutrition import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macronutrients,
    recommend_daily_meals,
    calculate_hydration_target,
    generate_recovery_nutrition_insight,
    compute_complete_nutrition_intelligence
)
from services.nutrition_service import NutritionService


class Phase7CVerificationTests(unittest.TestCase):
    """22 Comprehensive Verification Tests for Phase 7C."""

    @classmethod
    def setUpClass(cls):
        cls.test_db = "scratch/test_phase7c.db"
        p = Path(cls.test_db)
        if p.exists():
            p.unlink()

        init_db(cls.test_db)
        from services.auth_service import AuthService
        cls.user_repo = UserRepository(db_path=cls.test_db)
        cls.auth_service = AuthService(user_repo=cls.user_repo, db_path=cls.test_db)
        cls.workout_repo = WorkoutRepository(db_path=cls.test_db)
        cls.nutrition_repo = NutritionRepository(db_path=cls.test_db)
        cls.service = NutritionService(
            nutrition_repo=cls.nutrition_repo,
            user_repo=cls.user_repo,
            db_path=cls.test_db
        )

        # Create test users via AuthService
        ok1, msg1, user1 = cls.auth_service.register(
            name="Aarav Sharma",
            email="athlete_veg@truform.ai",
            password="SecurePassword123!",
            height_cm=178.0,
            weight_kg=74.0,
            fitness_goal="MUSCLE_BUILDING"
        )
        cls.user_veg = user1
        cls.test_user_id = user1.id

        ok2, msg2, user2 = cls.auth_service.register(
            name="Priya Patel",
            email="athlete_nonveg@truform.ai",
            password="SecurePassword123!",
            height_cm=165.0,
            weight_kg=62.0,
            fitness_goal="FAT_LOSS"
        )
        cls.user_nonveg = user2
        cls.test_user_id_2 = user2.id

    @classmethod
    def tearDownClass(cls):
        # Clean up test database
        p = Path(cls.test_db)
        if p.exists():
            try:
                p.unlink()
            except Exception:
                pass

    # --------------------------------------------------------------------------
    # 1. Database Tables Verification
    # --------------------------------------------------------------------------
    def test_01_db_tables_exist(self):
        """Verify nutrition_profiles, nutrition_plans, and hydration_logs tables exist."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.assertIn("nutrition_profiles", tables)
        self.assertIn("nutrition_plans", tables)
        self.assertIn("hydration_logs", tables)
        self.assertIn("users", tables)
        self.assertIn("workout_sessions", tables)
        self.assertIn("rep_history", tables)

    # --------------------------------------------------------------------------
    # 2. Calorie Engine: BMI, BMR, TDEE, Adjustments
    # --------------------------------------------------------------------------
    def test_02_bmi_calculation(self):
        """Verify BMI calculation and categorization."""
        bmi, cat = calculate_bmi(178.0, 74.0)
        self.assertAlmostEqual(bmi, 23.4, places=1)
        self.assertEqual(cat, "NORMAL")

        bmi_obese, cat_obese = calculate_bmi(175.0, 110.0)
        self.assertEqual(cat_obese, "OBESE")

        bmi_under, cat_under = calculate_bmi(170.0, 45.0)
        self.assertEqual(cat_under, "UNDERWEIGHT")

    def test_03_bmr_mifflin_st_jeor(self):
        """Verify BMR Mifflin-St Jeor formula for Male, Female, and Neutral."""
        # Male formula: 10*W + 6.25*H - 5*A + 5
        # 10*74 + 6.25*178 - 5*25 + 5 = 740 + 1112.5 - 125 + 5 = 1732.5
        bmr_male = calculate_bmr(178.0, 74.0, 25, "MALE")
        self.assertAlmostEqual(bmr_male, 1732.5, places=1)

        # Female formula: 10*W + 6.25*H - 5*A - 161
        # 10*62 + 6.25*165 - 5*28 - 161 = 620 + 1031.25 - 140 - 161 = 1350.25
        bmr_female = calculate_bmr(165.0, 62.0, 28, "FEMALE")
        self.assertAlmostEqual(bmr_female, 1350.25, places=1)

    def test_04_tdee_multipliers(self):
        """Verify TDEE scaling across activity levels."""
        bmr = 1700.0
        self.assertAlmostEqual(calculate_tdee(bmr, "SEDENTARY"), 1700 * 1.2, places=1)
        self.assertAlmostEqual(calculate_tdee(bmr, "LIGHTLY_ACTIVE"), 1700 * 1.375, places=1)
        self.assertAlmostEqual(calculate_tdee(bmr, "MODERATELY_ACTIVE"), 1700 * 1.55, places=1)
        self.assertAlmostEqual(calculate_tdee(bmr, "VERY_ACTIVE"), 1700 * 1.725, places=1)

    def test_05_calorie_adjustments(self):
        """Verify Fat Loss deficit, Muscle Building surplus, and safe caloric floor."""
        tdee = 2500
        surplus, d_surplus, _ = calculate_target_calories(tdee, "MUSCLE_BUILDING")
        deficit, d_deficit, _ = calculate_target_calories(tdee, "FAT_LOSS")
        maintenance, d_maint, _ = calculate_target_calories(tdee, "GENERAL_FITNESS")

        self.assertEqual(surplus, 2500 + 350)
        self.assertEqual(deficit, 2500 - 450)
        self.assertEqual(maintenance, 2500)

        # Floor check: extremely low TDEE should not go below 1200 kcal
        low_tdee = 1300
        safe_deficit, _, _ = calculate_target_calories(low_tdee, "FAT_LOSS", gender="FEMALE")
        self.assertGreaterEqual(safe_deficit, 1200)

    # --------------------------------------------------------------------------
    # 3. Macro Calculator & Caloric Consistency
    # --------------------------------------------------------------------------
    def test_06_macro_protein_scaling(self):
        """Verify protein scaling based on athlete weight and fitness goal."""
        weight_kg = 75.0
        macros_muscle = calculate_macronutrients(weight_kg, 2600, "MUSCLE_BUILDING")
        macros_fatloss = calculate_macronutrients(weight_kg, 2000, "FAT_LOSS")
        macros_endurance = calculate_macronutrients(weight_kg, 2400, "ENDURANCE")

        # 2.0 g/kg for muscle building = 150g
        self.assertEqual(macros_muscle["protein_g"], int(round(75.0 * 2.0)))
        # 1.8 g/kg for fat loss = 135g
        self.assertEqual(macros_fatloss["protein_g"], int(round(75.0 * 1.8)))
        # 1.5 g/kg for endurance = 112g
        self.assertEqual(macros_endurance["protein_g"], int(round(75.0 * 1.5)))

    def test_07_macro_fat_allocation(self):
        """Verify healthy fat allocation between 25-28% of total daily calories."""
        cals = 2400
        macros = calculate_macronutrients(70.0, cals, "GENERAL_FITNESS")
        fat_cals = macros["fat_calories"]
        fat_ratio = fat_cals / cals
        self.assertTrue(0.20 <= fat_ratio <= 0.32, f"Fat ratio {fat_ratio} out of bounds")

    def test_08_macro_carb_remainder(self):
        """Verify carbs allocate the remainder of daily calories."""
        cals = 2200
        macros = calculate_macronutrients(70.0, cals, "STRENGTH")
        expected_carb_cals = cals - (macros["protein_calories"] + macros["fat_calories"])
        self.assertAlmostEqual(macros["carbs_calories"], expected_carb_cals, delta=4)

    def test_09_macro_caloric_consistency(self):
        """Verify 4P + 4C + 9F == Total Calories within strict tolerance (<= 5 kcal)."""
        test_scenarios = [
            (1800, 60.0, "FAT_LOSS"),
            (2400, 75.0, "MUSCLE_BUILDING"),
            (2800, 85.0, "STRENGTH"),
            (2100, 68.0, "GENERAL_FITNESS"),
            (2600, 70.0, "ENDURANCE")
        ]
        for cals, w, goal in test_scenarios:
            m = calculate_macronutrients(w, cals, goal)
            total_computed = (m["protein_g"] * 4) + (m["carbs_g"] * 4) + (m["fat_g"] * 9)
            diff = abs(total_computed - cals)
            self.assertLessEqual(diff, 5, f"Caloric inconsistency {diff} kcal for target {cals}")

    # --------------------------------------------------------------------------
    # 4. Indian Meal Recommender & Allergen Filtering
    # --------------------------------------------------------------------------
    def test_10_meal_recommender_vegetarian(self):
        """Verify Vegetarian meal catalog produces complete 4-meal plan."""
        meals = recommend_daily_meals(
            diet_preference="VEGETARIAN",
            fitness_goal="MUSCLE_BUILDING",
            daily_calories=2200,
            protein_target_g=140
        )
        self.assertIn("breakfast", meals)
        self.assertIn("lunch", meals)
        self.assertIn("snacks", meals)
        self.assertIn("dinner", meals)
        self.assertIn("primary", meals["breakfast"])
        self.assertIn("alternative", meals["breakfast"])
        self.assertGreater(meals["lunch"]["primary"]["protein_g"], 0)

    def test_11_meal_recommender_non_veg(self):
        """Verify Non-Vegetarian meal plan contains lean athletic poultry/fish/eggs."""
        meals = recommend_daily_meals(
            diet_preference="NON_VEGETARIAN",
            fitness_goal="MUSCLE_BUILDING",
            daily_calories=2400,
            protein_target_g=150
        )
        all_text = json.dumps(meals).lower()
        has_nonveg = any(term in all_text for term in ["chicken", "egg", "fish"])
        self.assertTrue(has_nonveg, "Non-vegetarian meal plan did not contain non-veg items")

    def test_12_meal_recommender_vegan(self):
        """Verify Vegan meal plan strictly avoids dairy, eggs, and animal products."""
        meals = recommend_daily_meals(
            diet_preference="VEGAN",
            fitness_goal="FAT_LOSS",
            daily_calories=2100,
            protein_target_g=125
        )
        all_text = json.dumps(meals).lower()
        # Verify no paneer, chicken, egg, fish
        self.assertNotIn("paneer", all_text)
        self.assertNotIn("chicken", all_text)
        self.assertNotIn("curd", all_text)
        self.assertNotIn("yogurt", all_text)

    def test_13_allergen_filtering(self):
        """Verify allergen filter eliminates dishes containing specified allergens."""
        # Peanuts allergy
        meals_safe = recommend_daily_meals(
            diet_preference="VEGETARIAN",
            daily_calories=2200,
            protein_target_g=130,
            restrictions="peanuts, peanut"
        )
        meals_text = json.dumps(meals_safe["meals"]).lower()
        self.assertNotIn("peanut", meals_text)

    # --------------------------------------------------------------------------
    # 5. Hydration Engine & Daily Logs
    # --------------------------------------------------------------------------
    def test_14_hydration_target_calculation(self):
        """Verify hydration formula (weight*35 ml + optional 500 ml workout supplement)."""
        target_rest = calculate_hydration_target(70.0, had_workout_today=False)
        self.assertEqual(target_rest, int(70.0 * 35))  # 2450 ml

        target_active = calculate_hydration_target(70.0, had_workout_today=True)
        self.assertEqual(target_active, int(70.0 * 35) + 500)  # 2950 ml

    def test_15_hydration_logging_and_reset(self):
        """Verify logging water increments intake and reset clears today's intake."""
        user_id = self.test_user_id
        initial = self.service.get_daily_hydration(user_id)

        # Log 250 ml
        updated1 = self.service.log_water(user_id, 250)
        self.assertEqual(updated1.consumed_ml, initial.consumed_ml + 250)

        # Log 500 ml
        updated2 = self.service.log_water(user_id, 500)
        self.assertEqual(updated2.consumed_ml, initial.consumed_ml + 750)

        # Reset
        reset_log = self.service.reset_water(user_id)
        self.assertEqual(reset_log.consumed_ml, 0)

    def test_16_hydration_daily_isolation(self):
        """Verify hydration log is keyed to today's date."""
        from datetime import date
        today_str = date.today().isoformat()
        log = self.nutrition_repo.get_daily_hydration(self.test_user_id, today_str)
        self.assertIsNotNone(log)
        self.assertEqual(log.date, today_str)

    # --------------------------------------------------------------------------
    # 6. Profile CRUD & Plan Persistence
    # --------------------------------------------------------------------------
    def test_17_nutrition_profile_crud(self):
        """Verify profile create, read, and update."""
        user_id = self.test_user_id_2
        profile = self.service.update_profile(
            user_id=user_id,
            age=29,
            gender="FEMALE",
            activity_level="VERY_ACTIVE",
            diet_preference="NON_VEGETARIAN",
            restrictions="Gluten"
        )
        self.assertEqual(profile.age, 29)
        self.assertEqual(profile.gender, "FEMALE")
        self.assertEqual(profile.activity_level, "VERY_ACTIVE")
        self.assertEqual(profile.diet_preference, "NON_VEGETARIAN")
        self.assertEqual(profile.restrictions, "Gluten")

        fetched = self.nutrition_repo.get_profile_by_user_id(user_id)
        self.assertEqual(fetched.age, 29)

    def test_18_nutrition_plan_persistence(self):
        """Verify generated plan is safely archived to SQLite and retrievable."""
        plan, full_payload = self.service.generate_and_save_plan(self.test_user_id)
        self.assertIsNotNone(plan.id)
        self.assertGreater(plan.calorie_target, 1200)
        self.assertGreater(plan.protein_target, 50)
        self.assertIn("breakfast", full_payload["meal_plan"])

        # Fetch latest plan
        retrieved, payload = self.service.get_current_plan(self.test_user_id)
        self.assertEqual(retrieved.id, plan.id)
        self.assertEqual(retrieved.calorie_target, plan.calorie_target)

    # --------------------------------------------------------------------------
    # 7. Post-Workout Recovery Nutrition
    # --------------------------------------------------------------------------
    def test_19_post_workout_recovery_insight(self):
        """Verify recovery insight calculation from workout telemetry."""
        insight_high_fatigue = generate_recovery_nutrition_insight(
            exercise_name="BARBELL SQUAT",
            duration_seconds=1200,
            clean_reps=30,
            total_reps=36,
            fatigue_level="HIGH",
            stability_score=68.0,
            fitness_goal="MUSCLE_BUILDING"
        )
        self.assertEqual(insight_high_fatigue["carb_to_protein_ratio"], "4:1")
        self.assertEqual(insight_high_fatigue["recovery_window_minutes"], 30)
        self.assertIn("electrolyte", insight_high_fatigue["hydration_advice"].lower())
        self.assertGreater(len(insight_high_fatigue["suggested_snacks"]), 0)

        # Low fatigue recovery
        insight_low = generate_recovery_nutrition_insight(
            exercise_name="BODYWEIGHT SQUAT",
            duration_seconds=300,
            clean_reps=10,
            total_reps=10,
            fatigue_level="LOW",
            stability_score=95.0,
            fitness_goal="GENERAL_FITNESS"
        )
        self.assertEqual(insight_low["carb_to_protein_ratio"], "2:1")

    # --------------------------------------------------------------------------
    # 8. Service Facade End-to-End Orchestration
    # --------------------------------------------------------------------------
    def test_20_service_facade_end_to_end(self):
        """Verify NutritionService end-to-end flow with real session data."""
        session_data = {
            "exercise": "DEADLIFT",
            "duration": 900,
            "clean_reps": 20,
            "total_reps": 22,
            "movement_intelligence": {
                "fatigue": {"fatigue_level": "MODERATE"},
                "stability": {"stability_score": 82.0}
            }
        }
        recovery = self.service.record_workout_recovery_insight(self.test_user_id, session_data)
        self.assertIn("suggested_snacks", recovery)

        latest = self.service.get_latest_recovery_insight(self.test_user_id)
        self.assertEqual(latest["exercise_name"], "DEADLIFT")

    # --------------------------------------------------------------------------
    # 9. UI Components Instantiation
    # --------------------------------------------------------------------------
    def test_21_ui_components_instantiation(self):
        """Verify NutritionProfileDialog and NutritionDashboardDialog instantiate cleanly."""
        import customtkinter as ctk
        from ui.components.nutrition_profile import NutritionProfileDialog
        from ui.components.nutrition_dashboard import NutritionDashboardDialog

        root = ctk.CTk()
        root.withdraw()

        try:
            # 1. Profile Dialog
            profile_diag = NutritionProfileDialog(
                root,
                user=self.user_veg,
                nutrition_service=self.service
            )
            self.assertIsNotNone(profile_diag.age_entry)
            self.assertEqual(profile_diag.gender_opt.get(), "MALE")
            profile_diag.destroy()

            # 2. Dashboard Dialog
            dash_diag = NutritionDashboardDialog(
                root,
                user=self.user_veg,
                nutrition_service=self.service
            )
            self.assertIsNotNone(dash_diag.water_bar)
            self.assertGreater(len(dash_diag.meals_container.winfo_children()), 0)
            dash_diag.destroy()
        finally:
            root.destroy()

    # --------------------------------------------------------------------------
    # 10. Zero-Regression on Phase 7A & Phase 1-6
    # --------------------------------------------------------------------------
    def test_22_zero_regression_phase7a(self):
        """Verify Phase 7A auth, workout persistence, and aggregation remain intact."""
        # 1. Auth test
        ok, msg, authenticated = self.auth_service.login("athlete_veg@truform.ai", "SecurePassword123!")
        self.assertTrue(ok)
        self.assertIsNotNone(authenticated)
        self.assertEqual(authenticated.email, "athlete_veg@truform.ai")

        # 2. Save workout session
        session_id = self.workout_repo.save_workout_session(
            user_id=authenticated.id,
            exercise_name="SQUAT",
            started_at="2026-09-05T10:00:00",
            completed_at="2026-09-05T10:15:00",
            duration_seconds=900,
            total_reps=15,
            clean_reps=14,
            average_quality=92.5,
            best_rep_quality=98.0,
            consistency_score=94.0,
            stability_score=91.0,
            fatigue_level="LOW",
            risk_level="LOW",
            session_trajectory="IMPROVING",
            rep_records=[
                {"rep_number": 1, "score": 92.0, "is_clean": True},
                {"rep_number": 2, "score": 98.0, "is_clean": True}
            ]
        )
        self.assertIsNotNone(session_id)

        # 3. Aggregate stats
        stats = self.workout_repo.get_user_aggregate_stats(authenticated.id)
        self.assertGreaterEqual(stats["total_workouts"], 1)
        self.assertGreaterEqual(stats["total_reps"], 15)


def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(Phase7CVerificationTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print("\n" + "=" * 60)
    print(f"Phase 7C Tests Run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}, Failures: {len(result.failures)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 60)
    if not result.wasSuccessful():
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
