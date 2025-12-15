"""
workout_engine.py

Rule-based workout planner for FitMindAI.
Uses a curated exercise library and evidence-based training principles
to build safe, progressive weekly workout plans.
"""

from __future__ import annotations
from typing import Dict, Any, List
import random


# ----------------------------------------------------------------------
# EXERCISE LIBRARY (SAFE, BASIC MOVES)
# ----------------------------------------------------------------------

EXERCISES: List[Dict[str, Any]] = [
    # Lower body
    {
        "name": "Bodyweight Squat",
        "muscle_group": "legs",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["knee"],
        "category": "lower",
    },
    {
        "name": "Sit-to-Stand from Chair",
        "muscle_group": "legs",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": [],
        "category": "lower",
    },
    {
        "name": "Glute Bridge",
        "muscle_group": "glutes",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["lower_back"],
        "category": "lower",
    },
    {
        "name": "Wall Sit",
        "muscle_group": "legs",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["knee"],
        "category": "lower",
    },
    {
        "name": "Step-ups (Low Step)",
        "muscle_group": "legs",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["knee", "ankle"],
        "category": "lower",
    },
    {
        "name": "Static Lunge (Short Range)",
        "muscle_group": "legs",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "intermediate",
        "avoid_if_injuries": ["knee"],
        "category": "lower",
    },
    {
        "name": "Dumbbell Goblet Squat",
        "muscle_group": "legs",
        "type": "strength",
        "equipment": "dumbbells",
        "level_min": "intermediate",
        "avoid_if_injuries": ["knee"],
        "category": "lower",
    },
    {
        "name": "Dumbbell Romanian Deadlift",
        "muscle_group": "posterior_chain",
        "type": "strength",
        "equipment": "dumbbells",
        "level_min": "intermediate",
        "avoid_if_injuries": ["lower_back"],
        "category": "lower",
    },

    # Upper body - push
    {
        "name": "Wall Push-up",
        "muscle_group": "chest",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["shoulder", "wrist"],
        "category": "upper",
    },
    {
        "name": "Incline Push-up (Hands on Table)",
        "muscle_group": "chest",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["shoulder", "wrist"],
        "category": "upper",
    },
    {
        "name": "Knee Push-up",
        "muscle_group": "chest",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["shoulder", "wrist"],
        "category": "upper",
    },
    {
        "name": "Dumbbell Chest Press (Floor)",
        "muscle_group": "chest",
        "type": "strength",
        "equipment": "dumbbells",
        "level_min": "intermediate",
        "avoid_if_injuries": ["shoulder"],
        "category": "upper",
    },
    {
        "name": "Dumbbell Shoulder Press (Seated)",
        "muscle_group": "shoulders",
        "type": "strength",
        "equipment": "dumbbells",
        "level_min": "intermediate",
        "avoid_if_injuries": ["shoulder"],
        "category": "upper",
    },

    # Upper body - pull
    {
        "name": "Dumbbell Bent-over Row",
        "muscle_group": "back",
        "type": "strength",
        "equipment": "dumbbells",
        "level_min": "beginner",
        "avoid_if_injuries": ["lower_back"],
        "category": "upper",
    },
    {
        "name": "Resistance Band Row",
        "muscle_group": "back",
        "type": "strength",
        "equipment": "machines",
        "level_min": "beginner",
        "avoid_if_injuries": ["lower_back"],
        "category": "upper",
        "home_friendly": False,  # Requires cable machine
    },
    {
        "name": "Superman Hold",
        "muscle_group": "back",
        "type": "strength",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["lower_back"],
        "category": "upper",
    },

    # Core
    {
        "name": "Plank (Knees or Full)",
        "muscle_group": "core",
        "type": "core",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["wrist", "shoulder"],
        "category": "core",
    },
    {
        "name": "Dead Bug",
        "muscle_group": "core",
        "type": "core",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": [],
        "category": "core",
    },
    {
        "name": "Bird Dog",
        "muscle_group": "core",
        "type": "core",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["wrist", "knee"],
        "category": "core",
    },
    {
        "name": "Side Plank (Knees)",
        "muscle_group": "core",
        "type": "core",
        "equipment": "bodyweight",
        "level_min": "beginner",
        "avoid_if_injuries": ["shoulder"],
        "category": "core",
    },
]


# ----------------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------------


def _pick_exercises(
    equipment_list: list[str],
    level: str,
    injuries: list[str],
    target_category: str,  # "upper", "lower", "core", "full"
    preferred_env: str | None,
    n_exercises: int = 4,
    exclude_names: list[str] = None,
) -> list[dict]:
    """
    Filter EXERCISES by equipment, experience level, injuries, and category.
    Returns up to n_exercises with variety.
    """
    injuries = injuries or []
    level = level or "beginner"
    equipment_list = equipment_list or ["bodyweight"]
    exclude_names = exclude_names or []

    allowed: list[dict] = []

    for ex in EXERCISES:
        # Skip if already used
        if ex["name"] in exclude_names:
            continue

        # Equipment filter
        if ex["equipment"] not in equipment_list:
            continue

        # Experience level filter
        if level == "beginner" and ex["level_min"] not in ("beginner",):
            continue

        # Injury filter
        if any(inj in ex.get("avoid_if_injuries", []) for inj in injuries):
            continue

        # Environment filter
        if preferred_env == "home" and ex.get("home_friendly") == False:
            continue

        # Category filter
        if target_category == "full":
            allowed.append(ex)
        elif ex.get("category") == target_category:
            allowed.append(ex)

    # Shuffle to add variety
    random.shuffle(allowed)

    # Pick up to n_exercises with distinct muscle groups where possible
    selected: list[dict] = []
    seen_muscles: set[str] = set()

    for ex in allowed:
        mg = ex["muscle_group"]
        if mg not in seen_muscles:
            selected.append(ex)
            seen_muscles.add(mg)
        if len(selected) >= n_exercises:
            break

    # If still need more, add remaining
    if len(selected) < n_exercises:
        for ex in allowed:
            if ex not in selected:
                selected.append(ex)
            if len(selected) >= n_exercises:
                break

    return selected


def _determine_sets_reps(goal: str, level: str) -> tuple[int, str]:
    """Return (sets, reps_range) based on goal and experience level."""
    if level == "beginner":
        base_sets = 2
    elif level == "intermediate":
        base_sets = 3
    else:
        base_sets = 3

    if goal == "muscle_gain":
        return (base_sets, "8-12")
    elif goal == "weight_loss":
        return (base_sets, "12-15")
    else:  # maintenance / general_health
        return (base_sets, "10-12")


def _build_strength_session(
    goal: str,
    equipment: list[str],
    level: str,
    injuries: list[str],
    preferred_env: str | None,
    session_length_mins: int,
    target_category: str = "full",  # "upper", "lower", "full"
    exclude_names: list[str] = None,
) -> list[dict]:
    """
    Build a single strength session with warm-up and exercises.
    """
    # Adjust exercise count based on session length
    if session_length_mins <= 30:
        n_exercises = 4
    elif session_length_mins <= 45:
        n_exercises = 5
    else:
        n_exercises = 6

    # For upper/lower splits, reduce by 1 since we're focusing on fewer muscle groups
    if target_category in ("upper", "lower"):
        n_exercises = max(3, n_exercises - 1)

    exercises = _pick_exercises(
        equipment, level, injuries, target_category, preferred_env, n_exercises, exclude_names
    )

    sets, reps = _determine_sets_reps(goal, level)

    session: list[dict] = []

    # Add warm-up
    session.append({
        "type": "warmup",
        "description": "5 min light cardio (marching in place, jumping jacks) + dynamic stretches",
    })

    # Add exercises
    for ex in exercises:
        session.append({
            "name": ex["name"],
            "muscle_group": ex["muscle_group"],
            "type": "strength",
            "sets": sets,
            "reps": reps,
        })

    # Add cooldown
    session.append({
        "type": "cooldown",
        "description": "3-5 min stretching (focus on trained muscles)",
    })

    return session


def _build_cardio_session(
    cardio_preference: str,
    session_length_mins: int,
    intensity: str = "moderate",
) -> list[dict]:
    """
    Build a simple cardio session description.
    """
    mode = cardio_preference or "walking"
    minutes = max(15, min(60, session_length_mins))

    return [
        {
            "type": "warmup",
            "description": "2 min slow pace, gradually increase",
        },
        {
            "type": "cardio",
            "mode": mode,
            "minutes": minutes - 4,  # Account for warmup/cooldown
            "intensity": intensity,
        },
        {
            "type": "cooldown",
            "description": "2 min slow pace + light stretching",
        },
    ]


def _determine_weekly_structure(goal: str, days: int, level: str) -> Dict[str, str]:
    """
    Determine what type of session each day should have.
    Returns dict like {"monday": "rest", "tuesday": "strength_full", ...}
    """
    # Enforce beginner safety caps
    if level == "beginner":
        days = min(days, 4)
    elif level == "intermediate":
        days = min(days, 5)
    else:
        days = min(days, 6)

    weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    structure: Dict[str, str] = {}

    if goal == "weight_loss":
        # Mix strength and cardio, prioritize cardio
        if days <= 3:
            # 3 days: S, C, S
            pattern = ["strength_full", "rest", "cardio", "rest", "strength_full", "rest", "rest"]
        elif days == 4:
            # 4 days: S, C, S, C
            pattern = ["strength_full", "cardio", "rest", "strength_full", "rest", "cardio", "rest"]
        else:  # 5 days
            # 5 days: S, C, S, C, S
            pattern = ["strength_full", "cardio", "strength_full", "rest", "cardio", "strength_full", "rest"]

    elif goal == "muscle_gain":
        # Prioritize strength, minimal cardio
        if days <= 3:
            # 3 days: S, rest, S, rest, S, rest, rest
            pattern = ["strength_full", "rest", "strength_full", "rest", "strength_full", "rest", "rest"]
        elif days == 4:
            # 4 days: Upper/Lower split
            pattern = ["strength_upper", "rest", "strength_lower", "rest", "strength_upper", "rest", "strength_lower"]
            # Adjust: put rest on Sunday
            pattern = ["strength_upper", "strength_lower", "rest", "strength_upper", "strength_lower", "rest", "rest"]
        else:  # 5 days
            # 5 days: U, L, rest, U, L, light cardio (optional), rest
            pattern = ["strength_upper", "strength_lower", "rest", "strength_upper", "strength_lower", "cardio_light", "rest"]

    else:  # maintenance / general_health
        # Balanced mix
        if days <= 3:
            pattern = ["strength_full", "rest", "cardio", "rest", "strength_full", "rest", "rest"]
        elif days == 4:
            pattern = ["strength_full", "cardio", "rest", "strength_full", "rest", "cardio", "rest"]
        else:  # 5 days
            pattern = ["strength_full", "cardio", "strength_full", "rest", "cardio", "strength_full", "rest"]

    for i, day in enumerate(weekday_names):
        structure[day] = pattern[i]

    return structure


# ----------------------------------------------------------------------
# MAIN ENTRYPOINT
# ----------------------------------------------------------------------


def generate_weekly_plan(
    user_profile: Dict[str, Any] | None,
    prefs: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Generate a safe, progressive weekly workout plan.

    user_profile: reserved for future use (age, medical conditions).
    prefs: structured workout preferences from WorkoutPreferenceParser.
    """
    goal = prefs.get("goal", "general_health")
    days = int(prefs.get("days_per_week", 3) or 3)
    days = max(2, min(7, days))  # Clamp to 2-7
    level = prefs.get("experience_level", "beginner")
    equipment = prefs.get("equipment") or ["bodyweight"]
    injuries = prefs.get("injuries") or []
    cardio_pref = prefs.get("cardio_preference") or "walking"
    session_len = int(prefs.get("session_length_mins", 30) or 30)
    preferred_env = prefs.get("preferred_env")

    print(f"\n🏋️ Generating Workout Plan:")
    print(f"   Goal: {goal}, Level: {level}, Days: {days}")
    print(f"   Equipment: {equipment}, Injuries: {injuries}")
    print(f"   Environment: {preferred_env}, Session: {session_len} mins")

    # Determine weekly structure
    structure = _determine_weekly_structure(goal, days, level)

    plan: Dict[str, Any] = {}
    used_exercises: list[str] = []  # Track to avoid repetition within the week

    for day, session_type in structure.items():
        if session_type == "rest":
            plan[day] = "rest"

        elif session_type == "strength_full":
            session = _build_strength_session(
                goal, equipment, level, injuries, preferred_env,
                session_len, target_category="full", exclude_names=used_exercises
            )
            # Track exercise names
            for item in session:
                if item.get("name"):
                    used_exercises.append(item["name"])
            plan[day] = session

        elif session_type == "strength_upper":
            session = _build_strength_session(
                goal, equipment, level, injuries, preferred_env,
                session_len, target_category="upper", exclude_names=used_exercises
            )
            for item in session:
                if item.get("name"):
                    used_exercises.append(item["name"])
            plan[day] = session

        elif session_type == "strength_lower":
            session = _build_strength_session(
                goal, equipment, level, injuries, preferred_env,
                session_len, target_category="lower", exclude_names=used_exercises
            )
            for item in session:
                if item.get("name"):
                    used_exercises.append(item["name"])
            plan[day] = session

        elif session_type == "cardio":
            plan[day] = _build_cardio_session(cardio_pref, session_len, intensity="moderate")

        elif session_type == "cardio_light":
            plan[day] = _build_cardio_session(cardio_pref, min(session_len, 25), intensity="light")

    # Add metadata
    metadata = {
        "weekly_plan": plan,
        "guidelines": [
            " Rest days are essential for muscle recovery and growth.",
            " Progress gradually: increase reps/sets before adding weight.",
            " Stop if you feel sharp pain—consult a healthcare provider if needed.",
            " Track your workouts and aim to improve slightly each week.",
            f" This plan is designed for {level} level with {goal.replace('_', ' ')} goal.",
        ]
    }

    return metadata
