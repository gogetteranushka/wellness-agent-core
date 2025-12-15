import os
import json

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


class PreferenceParser:
    """
    Enhanced LLM parser that extracts comprehensive dietary preferences.
    Extracts fields including cuisines, allergies, time constraints, etc.
    """

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")

        # Define allowed values (enums)
        self.ALLOWED_ACTIVITY_LEVELS = [
            "sedentary",
            "lightly_active",
            "moderately_active",
            "very_active",
            "extra_active",
        ]

        self.ALLOWED_GOALS = ["weight_loss", "muscle_gain", "maintenance"]

        self.ALLOWED_DIET_TYPES = [
            "Vegetarian",
            "Vegan",
            "Non-vegetarian",
            "Eggetarian",
        ]

        # Match your recipe dataset cuisines
        self.ALLOWED_CUISINES = [
            "Indian",
            "South Indian Recipes",
            "Andhra",
            "Udupi",
            "Mexican",
            "Fusion",
            "Continental",
            "Bengali Recipes",
            "Punjabi",
            "Chettinad",
            "Tamil Nadu",
            "Maharashtrian Recipes",
            "North Indian Recipes",
            "Italian Recipes",
            "Sindhi",
            "Thai",
            "Chinese",
            "Kerala Recipes",
            "Gujarati Recipes",
            "Coorg",
            "Rajasthani",
            "Asian",
            "Middle Eastern",
            "Coastal Karnataka",
            "European",
            "Kashmiri",
            "Karnataka",
            "Lucknowi",
            "Hyderabadi",
            "Side Dish",
            "Goan Recipes",
            "Arab",
            "Assamese",
            "Bihari",
            "Malabar",
            "Himachal",
            "Awadhi",
            "Cantonese",
            "North East India Recipes",
            "Sichuan",
            "Mughlai",
            "Japanese",
            "Mangalorean",
            "Vietnamese",
            "British",
            "North Karnataka",
            "Parsi Recipes",
            "Greek",
            "Nepalese",
            "Oriya Recipes",
            "French",
            "Indo Chinese",
            "Konkan",
            "Mediterranean",
            "Sri Lankan",
            "Uttar Pradesh",
            "Malvani",
            "Indonesian",
            "African",
            "Shandong",
            "Korean",
            "American",
            "Kongunadu",
            "Pakistani",
            "Caribbean",
            "South Karnataka",
            "Haryana",
            "Uttarakhand-North Kumaon",
            "World Breakfast",
            "Malaysian",
            "Hunan",
            "Dinner",
            "Snack",
            "Jewish",
            "Burmese",
            "Afghan",
            "Brunch",
            "Jharkhand",
            "Nagaland",
            "Lunch",
        ]

        self.warnings: list[str] = []

    # --------- DIET PROMPT BUILDING ---------

    def build_prompt(self, user_text: str, fallback_profile: dict | None = None) -> str:
        """
        Build comprehensive prompt for extracting rich diet preferences.
        """
        fallback_str = json.dumps(fallback_profile) if fallback_profile else "None provided"

        prompt = f"""You are an advanced nutrition preference parser. Extract ALL relevant information from user text.

COMPREHENSIVE OUTPUT SCHEMA (JSON only, no markdown):

{{
  "activity_level": "sedentary" | "lightly_active" | "moderately_active" | "very_active" | "extra_active",
  "goal": "weight_loss" | "muscle_gain" | "maintenance",
  "diet_type": "Vegetarian" | "Vegan" | "Non-vegetarian" | "Eggetarian",
  "preferred_cuisines": ["array of cuisine names or null"],
  "disliked_ingredients": ["array of ingredient names or null"],
  "allergies": ["array of allergens or null"],
  "max_time_mins_breakfast": integer or null,
  "max_time_mins_lunch": integer or null,
  "max_time_mins_dinner": integer or null,
  "max_time_mins_snacks": integer or null,
  "spice_preference": "mild" | "medium" | "spicy" | null,
  "meal_prep_willing": true | false | null,
  "cooking_skill": "beginner" | "intermediate" | "advanced" | null,
  "budget_preference": "low" | "medium" | "high" | null
}}

ACTIVITY LEVEL MAPPING:
- "desk job", "sitting all day", "sedentary" → sedentary
- "light exercise", "walking", "yoga" → lightly_active
- "gym 3-5 days", "regular exercise" → moderately_active
- "athlete", "daily training", "very active" → very_active / extra_active

GOAL MAPPING:
- "lose weight", "cut", "fat loss", "slim down" → weight_loss
- "gain muscle", "bulk", "build muscle" → muscle_gain
- "maintain", "stay fit", "general health" → maintenance

DIET TYPE MAPPING:
- "veg", "vegetarian" → Vegetarian
- "vegan", "plant based" → Vegan
- "non-veg", "non vegetarian", "eat meat" → Non-vegetarian
- "eggetarian", "eggs but no meat" → Eggetarian

CUISINE EXTRACTION:
Use only known cuisine names when possible. If unsure, set preferred_cuisines to null.

ALLERGEN DETECTION:
Look for: peanuts, tree nuts, dairy, eggs, soy, wheat, gluten, shellfish, fish.

TIME CONSTRAINTS:
Look for phrases like "10 mins breakfast", "quick morning", "30 min dinner".
Extract numeric values (5–120 mins) or null.

SPICE PREFERENCE:
- "mild", "no spice", "bland" → mild
- "medium spice", "moderate" → medium
- "spicy", "love spice", "hot" → spicy
- Not mentioned → null

COOKING SKILL:
- "beginner", "new to cooking", "simple" → beginner
- "intermediate", "decent cook" → intermediate
- "advanced", "experienced", "great cook" → advanced
- Not mentioned → null

MEAL PREP:
- Mentions "meal prep", "batch cooking", "cook ahead" → true
- Says "no meal prep", "cook fresh" → false
- Not mentioned → null

EXAMPLES:

Input: "I'm 25, desk job but walk daily, vegetarian, want to lose weight, love South Indian food, hate mushrooms and oats, can cook only 10 mins in morning, allergic to peanuts"
Output: {{"activity_level": "lightly_active", "goal": "weight_loss", "diet_type": "Vegetarian", "preferred_cuisines": ["South Indian Recipes"], "disliked_ingredients": ["mushrooms", "oats"], "allergies": ["peanuts"], "max_time_mins_breakfast": 10, "max_time_mins_lunch": null, "max_time_mins_dinner": null, "max_time_mins_snacks": null, "spice_preference": null, "meal_prep_willing": null, "cooking_skill": null, "budget_preference": null}}

Input: "Gym 5 days a week, want to build muscle, non-veg, love Punjabi and North Indian food, can spend 30-40 mins on lunch and dinner, intermediate cook, willing to meal prep, love spicy food"
Output: {{"activity_level": "very_active", "goal": "muscle_gain", "diet_type": "Non-vegetarian", "preferred_cuisines": ["Punjabi", "North Indian Recipes"], "disliked_ingredients": null, "allergies": null, "max_time_mins_breakfast": null, "max_time_mins_lunch": 35, "max_time_mins_dinner": 35, "max_time_mins_snacks": null, "spice_preference": "spicy", "meal_prep_willing": true, "cooking_skill": "intermediate", "budget_preference": null}}

USER INPUT:
{user_text}

FALLBACK DEFAULTS (use if uncertain):
{fallback_str}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY a JSON object, no markdown, no comments.
2. Include ALL fields in the schema (use null if not mentioned).
3. Do not truncate; close all braces/brackets properly.
"""
        return prompt

    # --------- DIET PARSING ---------

    def parse_preferences_text(self, text: str, defaults: dict | None = None) -> dict:
        """
        Parse natural language diet preferences into structured format with retry logic.
        """
        print("\n🤖 LLM Preference Parser:")
        print(f"   User text: {text[:100]}...")
        print(f"   Has fallback: {defaults is not None}")

        prompt = self.build_prompt(text, defaults)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"   Attempt {attempt + 1}/{max_retries}...")

                temperature = 0.1 + (attempt * 0.1)

                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=2048,
                    ),
                )

                raw_response = response.text.strip()
                print(f"DEBUG: Raw response length: {len(raw_response)} chars")
                print(f"DEBUG: Raw response:\n{raw_response}")

                if raw_response.startswith("```"):
                    lines = raw_response.split("\n")
                    if lines.startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == ("```"):
                        lines = lines[:-1]
                    raw_response = "\n".join(lines).strip()

                try:
                    parsed = json.loads(raw_response)
                    print("   ✅ JSON parsed successfully")
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON Error: {e}")
                    if not raw_response.rstrip().endswith("}"):
                        print("   ⚠️  Response appears truncated, adding closing brace")
                        raw_response = raw_response.rstrip().rstrip(",") + "}"
                        parsed = json.loads(raw_response)
                    else:
                        raise

                cleaned = self.validate_and_clean(parsed, defaults)

                print("   ✅ Success!")
                print(f"   Activity: {cleaned.get('activity_level')}")
                print(f"   Goal: {cleaned.get('goal')}")
                print(f"   Diet: {cleaned.get('diet_type')}")
                print(f"   Warnings: {len(self.warnings)}")

                return cleaned

            except json.JSONDecodeError as e:
                print(f"   ❌ Attempt {attempt + 1} failed: Invalid JSON - {e}")
                if attempt == max_retries - 1:
                    print("   ⚠️  All retries failed, using fallback defaults")
                    if defaults:
                        return {
                            "activity_level": defaults.get(
                                "activity_level", "moderately_active"
                            ),
                            "goal": defaults.get("goal", "maintenance"),
                            "diet_type": defaults.get("diet_type", "Vegetarian"),
                            "preferred_cuisines": None,
                            "disliked_ingredients": None,
                            "allergies": None,
                            "max_time_mins_breakfast": None,
                            "max_time_mins_lunch": None,
                            "max_time_mins_dinner": None,
                            "max_time_mins_snacks": None,
                            "spice_preference": None,
                            "cooking_skill": None,
                            "budget_preference": None,
                            "meal_prep_willing": None,
                        }
                    raise Exception(f"LLM returned invalid JSON: {e}")

            except Exception as e:
                print(f"   ❌ Attempt {attempt + 1} failed: {type(e).__name__} - {e}")
                if attempt == max_retries - 1:
                    raise Exception(
                        f"LLM parsing failed after {max_retries} attempts: {e}"
                    )
                import time

                time.sleep(0.5 * (attempt + 1))

        raise Exception("Unexpected error in parse_preferences_text")

    def validate_and_clean(
        self, parsed: dict, fallback_profile: dict | None = None
    ) -> dict:
        """
        Comprehensive validation of all extracted diet fields.
        """
        warnings: list[str] = []
        cleaned: dict = {}
        fb = fallback_profile or {}

        # activity_level
        activity = (parsed.get("activity_level") or "").lower().replace(" ", "_")
        if activity in self.ALLOWED_ACTIVITY_LEVELS:
            cleaned["activity_level"] = activity
        else:
            fallback_activity = fb.get("activity_level", "moderately_active")
            cleaned["activity_level"] = fallback_activity
            if activity:
                warnings.append(
                    f"Invalid activity_level '{activity}'; using fallback '{fallback_activity}'"
                )

        # goal
        goal = (parsed.get("goal") or "").lower().replace(" ", "_")
        if goal in self.ALLOWED_GOALS:
            cleaned["goal"] = goal
        else:
            fallback_goal = fb.get("goal", "maintenance")
            cleaned["goal"] = fallback_goal
            if goal:
                warnings.append(
                    f"Invalid goal '{goal}'; using fallback '{fallback_goal}'"
                )

        # diet_type
        diet = parsed.get("diet_type") or ""
        if diet in self.ALLOWED_DIET_TYPES:
            cleaned["diet_type"] = diet
        else:
            fallback_diet = fb.get("diet_type", "Vegetarian")
            cleaned["diet_type"] = fallback_diet
            if diet:
                warnings.append(
                    f"Invalid diet_type '{diet}'; using fallback '{fallback_diet}'"
                )

        # preferred_cuisines
        cuisines = parsed.get("preferred_cuisines")
        if isinstance(cuisines, list) and cuisines:
            valid = [c for c in cuisines if c in self.ALLOWED_CUISINES]
            cleaned["preferred_cuisines"] = valid if valid else None
        else:
            cleaned["preferred_cuisines"] = None

        # simple list fields
        cleaned["disliked_ingredients"] = (
            parsed.get("disliked_ingredients")
            if isinstance(parsed.get("disliked_ingredients"), list)
            else None
        )
        cleaned["allergies"] = (
            parsed.get("allergies")
            if isinstance(parsed.get("allergies"), list)
            else None
        )

        # time constraints
        for meal in ["breakfast", "lunch", "dinner", "snacks"]:
            key = f"max_time_mins_{meal}"
            value = parsed.get(key)
            if value is None:
                cleaned[key] = None
            elif isinstance(value, (int, float)) and 5 <= value <= 120:
                cleaned[key] = int(value)
            else:
                cleaned[key] = None
                warnings.append(f"Invalid {key} '{value}'; set to null")

        # enums with null allowed
        spice = parsed.get("spice_preference")
        cleaned["spice_preference"] = (
            spice if spice in ["mild", "medium", "spicy"] else None
        )

        skill = parsed.get("cooking_skill")
        cleaned["cooking_skill"] = (
            skill if skill in ["beginner", "intermediate", "advanced"] else None
        )

        budget = parsed.get("budget_preference")
        cleaned["budget_preference"] = (
            budget if budget in ["low", "medium", "high"] else None
        )

        # boolean
        meal_prep = parsed.get("meal_prep_willing")
        cleaned["meal_prep_willing"] = (
            meal_prep if isinstance(meal_prep, bool) else None
        )

        self.warnings = warnings
        return cleaned


# Singleton diet parser instance
preference_parser = PreferenceParser()


# ======================================================================
# WORKOUT PREFERENCE PARSER
# ======================================================================


class WorkoutPreferenceParser:
    """
    LLM-based parser for workout preferences.
    Converts free text into a structured workout config.
    """

    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.warnings: list[str] = []

        self.ALLOWED_GOALS = [
            "weight_loss",
            "muscle_gain",
            "maintenance",
            "general_health",
        ]
        self.ALLOWED_LEVELS = ["beginner", "intermediate", "advanced"]
        self.ALLOWED_EQUIPMENT = [
            "bodyweight",
            "dumbbells",
            "barbell",
            "machines",
            "cardio_machines",
        ]
        self.ALLOWED_STYLES = [
            "full_body",
            "upper_lower",
            "push_pull_legs",
            "cardio_focus",
            "mixed",
        ]
        self.ALLOWED_ENV = ["home", "gym"]
        self.ALLOWED_CARDIO = ["walking", "running", "cycling", "mixed"]

    def build_prompt(self, user_text: str, fallback_profile: dict | None = None) -> str:
        fb_str = json.dumps(fallback_profile) if fallback_profile else "None"

        prompt = f"""You are a workout preference parser. Extract the user's workout preferences into JSON.

SCHEMA (JSON only, no markdown):

{{
  "goal": "weight_loss" | "muscle_gain" | "maintenance" | "general_health",
  "experience_level": "beginner" | "intermediate" | "advanced",
  "days_per_week": integer,
  "session_length_mins": integer,
  "equipment": ["bodyweight" | "dumbbells" | "barbell" | "machines" | "cardio_machines"],
  "preferred_env": "home" | "gym" | null,
  "injuries": ["knee" | "shoulder" | "lower_back" | "ankle" | "..."],
  "cardio_preference": "walking" | "running" | "cycling" | "mixed" | null,
  "workout_style": "full_body" | "upper_lower" | "push_pull_legs" | "cardio_focus" | "mixed",
  "notes": string | null
}}

MAPPINGS:
- "lose fat", "burn fat", "slim down" → goal = "weight_loss"
- "build muscle", "get bigger", "gain size" → goal = "muscle_gain"
- "stay fit", "be healthy" → goal = "general_health"
- "new to gym", "never worked out", "beginner" → experience_level = "beginner"
- "work out 3 days", "train 4x/week" → days_per_week = that number
- "only at home", "no gym" → preferred_env = "home"
- "go to the gym" → preferred_env = "gym"
- "have dumbbells" → include "dumbbells" in equipment
- "bodyweight only", "no equipment" → equipment includes "bodyweight"
- "treadmill", "cycle", "elliptical" → include "cardio_machines" in equipment
- "bad knees", "knee pain" → injuries include "knee"
- "lower back pain" → injuries include "lower_back"

FALLBACK DEFAULTS (use if uncertain):
{fb_str}

EXAMPLES:

Input: "I'm a complete beginner, want to lose fat, can train 3 days a week at home with just bodyweight. I have bad knees and prefer walking over running."
Output: {{
  "goal": "weight_loss",
  "experience_level": "beginner",
  "days_per_week": 3,
  "session_length_mins": 30,
  "equipment": ["bodyweight"],
  "preferred_env": "home",
  "injuries": ["knee"],
  "cardio_preference": "walking",
  "workout_style": "full_body",
  "notes": null
}}

Input: "I go to the gym 5 days, want to build muscle, intermediate lifter, okay with barbells and machines, no injuries."
Output: {{
  "goal": "muscle_gain",
  "experience_level": "intermediate",
  "days_per_week": 5,
  "session_length_mins": 60,
  "equipment": ["barbell", "machines"],
  "preferred_env": "gym",
  "injuries": [],
  "cardio_preference": null,
  "workout_style": "upper_lower",
  "notes": null
}}

USER INPUT:
{user_text}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY a JSON object, no markdown.
2. Include ALL fields in the schema (use null or [] if not mentioned).
3. Clamp days_per_week between 2 and 7; session_length_mins between 20 and 90 when unsure.
"""
        return prompt

    def parse_workout_preferences_text(
        self, text: str, defaults: dict | None = None
    ) -> dict:
        print("\n🤖 Workout Preference Parser:")
        print(f"   User text: {text[:100]}...")
        print(f"   Has fallback: {defaults is not None}")

        prompt = self.build_prompt(text, defaults)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"   Attempt {attempt + 1}/{max_retries}...")
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2 + 0.1 * attempt,
                        max_output_tokens=600,
                    ),
                )
                raw = response.text.strip()
                print(f"DEBUG: Raw workout response length: {len(raw)}")
                print(f"DEBUG: Raw workout response:\n{raw}")

                if raw.startswith("```"):
                    lines = raw.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == ("```"):
                        lines = lines[:-1]
                    raw = "\n".join(lines).strip()

                parsed = json.loads(raw)
                cleaned = self.validate_and_clean_workout(parsed, defaults)
                print("   ✅ Workout preferences parsed")
                print(f"   Goal: {cleaned.get('goal')}")
                print(f"   Days/week: {cleaned.get('days_per_week')}")
                print(f"   Equipment: {cleaned.get('equipment')}")
                return cleaned

            except Exception as e:
                print(f"   ❌ Workout parse attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    print("   ⚠️  Using workout fallback defaults")
                    return self.validate_and_clean_workout({}, defaults)

        raise Exception("Unexpected error in parse_workout_preferences_text")

    def validate_and_clean_workout(
        self, parsed: dict, defaults: dict | None = None
    ) -> dict:
        fb = defaults or {}
        self.warnings = []
        out: dict = {}

        # goal
        goal = (parsed.get("goal") or "").lower().replace(" ", "_")
        out["goal"] = (
            goal if goal in self.ALLOWED_GOALS else fb.get("goal", "general_health")
        )

        # experience_level
        level = (parsed.get("experience_level") or "").lower()
        out["experience_level"] = (
            level if level in self.ALLOWED_LEVELS else fb.get("experience_level", "beginner")
        )

        # days_per_week
        days = parsed.get("days_per_week", fb.get("days_per_week", 3))
        if isinstance(days, (int, float)):
            days_int = max(2, min(7, int(days)))
        else:
            days_int = 3
        out["days_per_week"] = days_int

        # session_length_mins
        sess = parsed.get("session_length_mins", fb.get("session_length_mins", 30))
        if isinstance(sess, (int, float)):
            sess_int = max(20, min(90, int(sess)))
        else:
            sess_int = 30
        out["session_length_mins"] = sess_int

        # equipment
        eq = parsed.get("equipment", fb.get("equipment", ["bodyweight"]))
        if not isinstance(eq, list):
            eq = [eq]
        eq_clean = [e for e in eq if e in self.ALLOWED_EQUIPMENT]
        out["equipment"] = eq_clean or ["bodyweight"]

        # preferred_env
        env = parsed.get("preferred_env", fb.get("preferred_env"))
        out["preferred_env"] = env if env in self.ALLOWED_ENV else None

        # injuries
        injuries = parsed.get("injuries", fb.get("injuries", []))
        if not isinstance(injuries, list):
            injuries = [injuries]
        out["injuries"] = injuries

        # cardio_preference
        cp = parsed.get("cardio_preference", fb.get("cardio_preference"))
        out["cardio_preference"] = cp if cp in self.ALLOWED_CARDIO else None

        # workout_style
        style = parsed.get("workout_style", fb.get("workout_style", "full_body"))
        if style not in self.ALLOWED_STYLES:
            style = "full_body"
        out["workout_style"] = style

        # notes
        notes = parsed.get("notes", fb.get("notes"))
        out["notes"] = notes if isinstance(notes, str) else None

        return out


# Optional singleton if you want to reuse
workout_preference_parser = WorkoutPreferenceParser()
