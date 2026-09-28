"""
Workout Plan Generator Core Module.

This module handles input validation, prompt design, Groq API communication,
and exception handling for generating personalized workout plans.
"""

import os
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional, List
from dotenv import load_dotenv
from groq import Groq, APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_MODEL = "qwen/qwen3.8-27b"
AVAILABLE_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b",
    "allam-2-7b"
]

VALID_GOALS = [
    "Build muscle",
    "Lose fat",
    "General fitness",
    "Improve endurance",
    "Strength & Power"
]

VALID_EXPERIENCE = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

VALID_EQUIPMENT = [
    "No equipment / Bodyweight",
    "Home dumbbells",
    "Full gym",
    "Kettlebells & Resistance Bands"
]


@dataclass
class WorkoutInput:
    """Structured container for user workout preferences."""
    fitness_goal: str
    experience_level: str
    days_per_week: int
    equipment: str
    injuries_limitations: Optional[str] = None
    session_duration: int = 45  # in minutes


def validate_workout_inputs(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str
) -> Tuple[bool, str]:
    """
    Validates user inputs before passing to the LLM.

    Args:
        fitness_goal (str): Selected fitness goal.
        experience_level (str): User experience level.
        days_per_week (int): Days per week available for workout.
        equipment (str): Equipment available to user.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not fitness_goal or fitness_goal.strip() not in VALID_GOALS:
        return False, f"Please select a valid fitness goal from: {', '.join(VALID_GOALS)}."

    if not experience_level or experience_level.strip() not in VALID_EXPERIENCE:
        return False, f"Please select a valid experience level from: {', '.join(VALID_EXPERIENCE)}."

    if not isinstance(days_per_week, int) or days_per_week < 1 or days_per_week > 7:
        return False, "Days available per week must be an integer between 1 and 7."

    if not equipment or equipment.strip() not in VALID_EQUIPMENT:
        return False, f"Please select valid equipment access from: {', '.join(VALID_EQUIPMENT)}."

    return True, ""


def build_workout_prompt(inputs: WorkoutInput) -> Tuple[str, str]:
    """
    Constructs a highly structured system prompt and user prompt for Groq LLM.

    Args:
        inputs (WorkoutInput): Validated user input data.

    Returns:
        Tuple[str, str]: (system_prompt, user_prompt)
    """
    system_prompt = (
        "You are an elite, certified personal trainer and strength & conditioning specialist. "
        "Your goal is to create highly tailored, realistic, safe, and effective weekly workout plans.\n\n"
        "RULES & CONSTRAINTS YOU MUST ABSOLUTELY FOLLOW:\n"
        "1. STRICT EQUIPMENT COMPLIANCE: Only prescribe exercises that can be performed using the specified equipment. "
        "If equipment is 'No equipment / Bodyweight', do NOT suggest barbells or cable machines.\n"
        "2. INJURY & LIMITATION ADAPTATION: If the user lists injuries or limitations, strictly modify exercise selection "
        "to protect those areas (e.g., if 'bad knees', exclude high-impact jumps or heavy deep squats; if 'no overhead pressing', replace overhead movements with lateral raises or incline presses).\n"
        "3. STRUCTURED OUTPUT FORMAT: Output a clean, well-organized Markdown plan. Break down the plan day-by-day for the exact number of days specified.\n"
        "4. EXERCISE DETAILS: For every exercise, include: Exercise Name, Sets, Reps (or Time), Rest Interval, and a key Form Technique tip.\n"
        "5. SAFETY & MEDICAL DISCLAIMER: Always start the plan with a brief, clear safety/medical disclaimer if injuries or limitations are mentioned.\n"
        "6. PRACTICALITY: Include Warm-up (3-5 mins) and Cool-down (3-5 mins) for each session scoped within the session duration.\n"
        "7. SCOPE & TONE: Be encouraging, structured, realistic, and clear. Avoid generic walls of text or non-actionable advice."
    )

    injuries_text = inputs.injuries_limitations.strip() if inputs.injuries_limitations else "None specified"

    user_prompt = f"""Generate a personalized weekly workout plan based on the following client profile:

- Fitness Goal: {inputs.fitness_goal}
- Experience Level: {inputs.experience_level}
- Workout Frequency: {inputs.days_per_week} day(s) per week
- Equipment Access: {inputs.equipment}
- Target Session Duration: ~{inputs.session_duration} minutes per session
- Injuries / Limitations: {injuries_text}

Please provide the plan using the following structure:
1. **Overview & Strategy Summary**: Brief explanation of the split (e.g., Full Body, Upper/Lower, Push/Pull/Legs) and why it fits their goal.
2. **Medical & Safety Disclaimer**: (Mandatory if injuries/limitations are present).
3. **Weekly Workout Breakdown**:
   For each day (e.g., Day 1, Day 2 up to Day {inputs.days_per_week}):
   - Focus Area / Target Muscle Groups
   - Warm-up routine
   - Main Exercises (Table or Bulleted list with Exercise Name | Sets | Reps | Rest | Key Form Tip)
   - Cool-down / Mobility routine
4. **Progression & Recovery Advice**: 2-3 practical tips for continuous progress and recovery tailored to their experience level.
"""

    return system_prompt, user_prompt


def generate_workout_plan(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    injuries_limitations: Optional[str] = None,
    session_duration: int = 45,
    api_key: Optional[str] = None,
    model_name: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Calls the Groq LLM API to generate a personalized workout plan.

    Args:
        fitness_goal (str): Fitness goal.
        experience_level (str): Experience level.
        days_per_week (int): Days per week.
        equipment (str): Equipment available.
        injuries_limitations (Optional[str]): Free-text injuries or limitations.
        session_duration (int): Target minutes per workout.
        api_key (Optional[str]): Groq API Key.
        model_name (str): Groq LLM model ID to use.

    Returns:
        Dict[str, Any]: Dictionary with keys: success, plan, error, raw_inputs.
    """
    raw_inputs = {
        "fitness_goal": fitness_goal,
        "experience_level": experience_level,
        "days_per_week": days_per_week,
        "equipment": equipment,
        "injuries_limitations": injuries_limitations,
        "session_duration": session_duration,
        "model_name": model_name
    }

    # 1. Input Validation
    is_valid, validation_error = validate_workout_inputs(
        fitness_goal=fitness_goal,
        experience_level=experience_level,
        days_per_week=days_per_week,
        equipment=equipment
    )
    if not is_valid:
        return {
            "success": False,
            "plan": "",
            "error": validation_error,
            "raw_inputs": raw_inputs
        }

    # 2. Determine API Key
    resolved_api_key = api_key if api_key is not None else os.getenv("GROQ_API_KEY")
    if not resolved_api_key or not resolved_api_key.strip():
        return {
            "success": False,
            "plan": "",
            "error": "Groq API Key is missing. Please enter your API key in the sidebar or set the GROQ_API_KEY environment variable.",
            "raw_inputs": raw_inputs
        }

    # 3. Create WorkoutInput dataclass
    user_input = WorkoutInput(
        fitness_goal=fitness_goal,
        experience_level=experience_level,
        days_per_week=days_per_week,
        equipment=equipment,
        injuries_limitations=injuries_limitations,
        session_duration=session_duration
    )

    # 4. Build Prompt
    system_prompt, user_prompt = build_workout_prompt(user_input)

    # 5. Call Groq API with robust error handling
    try:
        client = Groq(api_key=resolved_api_key.strip())

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model_name,
            temperature=0.7,
            max_tokens=2500,
        )

        if not response or not response.choices:
            return {
                "success": False,
                "plan": "",
                "error": "Received an empty response from the AI model. Please try again.",
                "raw_inputs": raw_inputs
            }

        plan_content = response.choices[0].message.content
        if not plan_content or not plan_content.strip():
            return {
                "success": False,
                "plan": "",
                "error": "The AI model generated an empty plan. Please try clicking Regenerate.",
                "raw_inputs": raw_inputs
            }

        return {
            "success": True,
            "plan": plan_content.strip(),
            "error": "",
            "raw_inputs": raw_inputs
        }

    except AuthenticationError:
        logger.error("Groq Authentication Error")
        return {
            "success": False,
            "plan": "",
            "error": "Invalid Groq API Key. Please verify your key at https://console.groq.com/keys and try again.",
            "raw_inputs": raw_inputs
        }
    except RateLimitError:
        logger.error("Groq Rate Limit Exceeded")
        return {
            "success": False,
            "plan": "",
            "error": "Groq API rate limit exceeded. Please wait a few moments and try again.",
            "raw_inputs": raw_inputs
        }
    except APIConnectionError:
        logger.error("Groq Connection Error")
        return {
            "success": False,
            "plan": "",
            "error": "Could not connect to Groq API. Please check your internet connection and try again.",
            "raw_inputs": raw_inputs
        }
    except APIStatusError as e:
        logger.error(f"Groq API Status Error: {e.status_code} - {e.message}")
        return {
            "success": False,
            "plan": "",
            "error": f"Groq API returned an error (Code {e.status_code}): {e.message}",
            "raw_inputs": raw_inputs
        }
    except Exception as e:
        logger.exception("Unexpected error during plan generation")
        return {
            "success": False,
            "plan": "",
            "error": f"An unexpected error occurred: {str(e)}",
            "raw_inputs": raw_inputs
        }


def swap_exercise(
    original_exercise: str,
    target_muscle_group: str,
    equipment: str,
    injuries_limitations: Optional[str] = None,
    api_key: Optional[str] = None,
    model_name: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Mini-feature (Stretch Goal): Swaps a specific exercise with a suitable alternative.
    """
    resolved_api_key = api_key if api_key is not None else os.getenv("GROQ_API_KEY")
    if not resolved_api_key or not resolved_api_key.strip():
        return {"success": False, "error": "Groq API Key is missing."}

    injuries_text = injuries_limitations if injuries_limitations else "None"

    system_prompt = (
        "You are an expert fitness coach. Suggest 1 high-quality alternative exercise to replace "
        "a specific exercise, strictly adhering to available equipment and physical limitations."
    )

    user_prompt = f"""I want to replace the exercise '{original_exercise}' (Target Muscle Group/Movement: {target_muscle_group}).

Constraints:
- Available Equipment: {equipment}
- Injuries / Limitations: {injuries_text}

Provide:
1. **Replacement Exercise Name**
2. **Why it's a good alternative**
3. **Recommended Sets & Reps**
4. **Key Execution Tip**
"""

    try:
        client = Groq(api_key=resolved_api_key.strip())
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model_name,
            temperature=0.7,
            max_tokens=500
        )
        content = response.choices[0].message.content if response and response.choices else ""
        if not content:
            return {"success": False, "error": "Received empty suggestion."}

        return {"success": True, "suggestion": content.strip()}
    except Exception as e:
        return {"success": False, "error": f"Failed to swap exercise: {str(e)}"}
