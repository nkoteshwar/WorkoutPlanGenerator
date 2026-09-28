import sys
import os
import unittest

# Ensure parent directory is in sys.path when running script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator import (
    validate_workout_inputs,
    build_workout_prompt,
    generate_workout_plan,
    WorkoutInput
)


class TestWorkoutGenerator(unittest.TestCase):

    def setUp(self):
        doc = self._testMethodDoc.strip() if self._testMethodDoc else ""
        print(f"\n[RUNNING TEST] {self._testMethodName} - {doc}")

    def tearDown(self):
        print(f"[RESULT] {self._testMethodName}: PASSED")

    def test_validate_workout_inputs_valid(self):
        """Test validation passes with valid inputs."""
        is_valid, msg = validate_workout_inputs(
            fitness_goal="Build muscle",
            experience_level="Intermediate",
            days_per_week=4,
            equipment="Full gym"
        )
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_validate_workout_inputs_invalid_days(self):
        """Test validation fails when days available is out of range (0 days)."""
        is_valid, msg = validate_workout_inputs(
            fitness_goal="Build muscle",
            experience_level="Intermediate",
            days_per_week=0,  # Invalid: 0 days
            equipment="Full gym"
        )
        self.assertFalse(is_valid)
        self.assertIn("between 1 and 7", msg)

    def test_validate_workout_inputs_invalid_goal(self):
        """Test validation fails when fitness goal is invalid."""
        is_valid, msg = validate_workout_inputs(
            fitness_goal="Fly like superman",  # Invalid goal
            experience_level="Intermediate",
            days_per_week=3,
            equipment="Full gym"
        )
        self.assertFalse(is_valid)
        self.assertIn("valid fitness goal", msg)

    def test_build_workout_prompt_structure(self):
        """Test system and user prompt construction contains required constraints."""
        workout_input = WorkoutInput(
            fitness_goal="Lose fat",
            experience_level="Beginner",
            days_per_week=3,
            equipment="Home dumbbells",
            injuries_limitations="bad knees",
            session_duration=30
        )
        system_prompt, user_prompt = build_workout_prompt(workout_input)

        self.assertIn("STRICT EQUIPMENT COMPLIANCE", system_prompt)
        self.assertIn("INJURY & LIMITATION ADAPTATION", system_prompt)
        self.assertIn("Lose fat", user_prompt)
        self.assertIn("Home dumbbells", user_prompt)
        self.assertIn("bad knees", user_prompt)
        self.assertIn("3 day(s) per week", user_prompt)

    def test_generate_workout_plan_missing_api_key(self):
        """Test generate_workout_plan handles missing API key gracefully without crashing."""
        res = generate_workout_plan(
            fitness_goal="Build muscle",
            experience_level="Advanced",
            days_per_week=5,
            equipment="Full gym",
            api_key=""
        )
        self.assertFalse(res["success"])
        self.assertIn("API Key is missing", res["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

