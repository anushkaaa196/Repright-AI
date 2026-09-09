"""REPRIGHT AI - Personalized Meal Recommendation Engine.

Generates practical, culturally familiar Indian meal plans adapted to:
- Dietary Preference (Vegetarian, Non-Vegetarian, Vegan, Eggetarian)
- Fitness Goal (Hypertrophy, Fat Loss, Strength, General Fitness)
- Caloric & Protein Targets
- Food Restrictions & Allergies
All plans are educational guidelines for athletic nutrition, not clinical diets.
"""

from typing import Dict, Any, List, Optional


# Master repository of practical Indian athletic meals
# Tagged by diet category and allergen flags for deterministic filtering
MEAL_CATALOG = {
    "BREAKFAST": [
        # Non-Veg & Eggetarian
        {
            "id": "br_eggs_toast",
            "title": "Masala Egg Omelette with Whole Wheat Toast",
            "diet": ["NON_VEGETARIAN", "EGGETARIAN"],
            "items": [
                "3 Whole Eggs / 2 Egg Whites scrambled with onions, tomatoes & green chillies",
                "2 Slices Whole Grain / Multigrain Toast",
                "1 Small Bowl Steamed Sprouts or Papaya"
            ],
            "allergens": ["EGG", "GLUTEN"],
            "protein_base": 24,
            "cal_base": 380,
            "highlight": "Complete essential amino acid profile with bioavailable choline."
        },
        # Vegetarian & Eggetarian
        {
            "id": "br_paneer_chilla",
            "title": "Moong Dal Chilla Stuffed with Grated Paneer",
            "diet": ["VEGETARIAN", "EGGETARIAN"],
            "items": [
                "2 Sprouted Yellow Moong Dal Chillas cooked in minimal cold-pressed mustard oil",
                "75g Fresh Low-Fat Paneer stuffing",
                "Fresh Mint-Coriander Chutney (homemade)"
            ],
            "allergens": ["DAIRY", "LACTOSE"],
            "protein_base": 22,
            "cal_base": 390,
            "highlight": "High dietary fiber, complex slow-digesting carbs, and rich dairy casein."
        },
        # Vegan & Vegetarian
        {
            "id": "br_tofu_bhurji",
            "title": "Turmeric Spiced Tofu Bhurji with Multigrain Roti",
            "diet": ["VEGAN", "VEGETARIAN"],
            "items": [
                "150g Organic Sautéed Tofu crumbled with turmeric, cumin, and spinach",
                "2 Fresh Multigrain Rotis (or Millet Rotis)",
                "1 Small Cup Black Coffee or Green Tea"
            ],
            "allergens": ["SOY", "GLUTEN"],
            "protein_base": 20,
            "cal_base": 360,
            "highlight": "Plant-based isoflavones and anti-inflammatory curcumin."
        },
        # Vegan & Vegetarian (Gluten-Free)
        {
            "id": "br_oats_nuts",
            "title": "Rolled Oats Porridge with Chia Seeds & Sliced Almonds",
            "diet": ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"],
            "items": [
                "60g Rolled Oats cooked with water or almond milk",
                "1 Tbsp Chia Seeds & Flaxseeds",
                "15g Soaked Almonds & 1 Sliced Banana or Apple"
            ],
            "allergens": ["NUTS", "PEANUTS"],
            "protein_base": 14,
            "cal_base": 340,
            "highlight": "Beta-glucan soluble fiber for sustained energy release."
        }
    ],

    "LUNCH": [
        # Non-Veg
        {
            "id": "lu_chicken_rice",
            "title": "Grilled Herb Chicken Breast with Brown Basmati & Dal",
            "diet": ["NON_VEGETARIAN"],
            "items": [
                "150g Lean Chicken Breast seasoned with turmeric, ginger, garlic & cumin",
                "1 Cup Steamed Brown Basmati Rice (150g)",
                "1 Bowl Tadka Arhar/Toor Dal",
                "Large Cucumber, Carrot & Beetroot Salad"
            ],
            "allergens": [],
            "protein_base": 42,
            "cal_base": 580,
            "highlight": "High-leucine muscle synthesis fuel and iron-rich legumes."
        },
        # Vegetarian & Eggetarian
        {
            "id": "lu_paneer_dal_roti",
            "title": "Low-Fat Paneer Curry with Tadka Dal & Phulkas",
            "diet": ["VEGETARIAN", "EGGETARIAN"],
            "items": [
                "100g Fresh Low-Fat Paneer in light tomato-onion gravy",
                "1 Bowl Mixed Moong & Masoor Dal",
                "2 Whole Wheat Phulkas with 1/2 tsp Ghee",
                "1 Bowl Curd or Fresh Spiced Buttermilk (Chaas)"
            ],
            "allergens": ["DAIRY", "LACTOSE", "GLUTEN"],
            "protein_base": 30,
            "cal_base": 550,
            "highlight": "Synergistic pulse-dairy protein pairing for complete amino score."
        },
        # Vegan
        {
            "id": "lu_soya_chana_rice",
            "title": "Pindi Chole & Soya Chunk Masala with Jeera Rice",
            "diet": ["VEGAN", "VEGETARIAN"],
            "items": [
                "1 Cup Spiced Chickpeas (Chole / Garbanzo beans)",
                "50g Textured Soya Chunks sautéed with capsicum",
                "1 Cup Steamed Basmati Rice or Quinoa",
                "Green Salad with Lemon Dressing"
            ],
            "allergens": ["SOY"],
            "protein_base": 32,
            "cal_base": 520,
            "highlight": "Dense plant-based BCAAs, iron, and sustained polysaccharide fuel."
        }
    ],

    "SNACKS": [
        # Non-Veg & Eggetarian
        {
            "id": "sn_boiled_eggs",
            "title": "Hard-Boiled Eggs with Chaat Masala & Roasted Chana",
            "diet": ["NON_VEGETARIAN", "EGGETARIAN"],
            "items": [
                "2 Hard-Boiled Whole Eggs dusted with roasted cumin and rock salt",
                "30g Roasted Bengal Gram (Chana with skin)"
            ],
            "allergens": ["EGG"],
            "protein_base": 18,
            "cal_base": 240,
            "highlight": "Quick post-training protein delivery with zero glycemic spike."
        },
        # Vegetarian & Eggetarian
        {
            "id": "sn_sprouts_chaat",
            "title": "Zesty Sprouted Moong & Kala Chana Chaat",
            "diet": ["VEGETARIAN", "EGGETARIAN", "VEGAN", "NON_VEGETARIAN"],
            "items": [
                "1 Cup Steamed Moong & Kala Chana sprouts",
                "Finely diced onions, cucumber, coriander, and fresh lemon juice",
                "A pinch of roasted jeera and black pepper"
            ],
            "allergens": [],
            "protein_base": 14,
            "cal_base": 200,
            "highlight": "Active enzymes, bio-available micronutrients, and high fiber."
        },
        # Vegan & Vegetarian
        {
            "id": "sn_makhana_nuts",
            "title": "Dry Roasted Makhana with Almonds & Walnuts",
            "diet": ["VEGAN", "VEGETARIAN", "EGGETARIAN", "NON_VEGETARIAN"],
            "items": [
                "25g Foxnuts (Makhana) roasted in cold-pressed coconut oil with turmeric",
                "15g Walnuts & Pumpkin Seeds"
            ],
            "allergens": ["NUTS"],
            "protein_base": 8,
            "cal_base": 190,
            "highlight": "Rich magnesium and omega-3 alpha-linolenic acid (ALA)."
        }
    ],

    "DINNER": [
        # Non-Veg
        {
            "id": "di_fish_roti",
            "title": "Pan-Seared Rohu / Salmon with Mixed Sabzi & Rotis",
            "diet": ["NON_VEGETARIAN"],
            "items": [
                "140g Fresh Fish Fillet pan-seared with Indian herbs & lime",
                "2 Whole Wheat / Jowar Rotis",
                "1 Bowl Stir-Fried Green Beans, Carrots & Spinach",
                "Warm clear vegetable soup or rasam"
            ],
            "allergens": ["FISH", "GLUTEN"],
            "protein_base": 34,
            "cal_base": 480,
            "highlight": "High EPA/DHA Omega-3 fatty acids for joint and tendon recovery."
        },
        # Vegetarian & Eggetarian
        {
            "id": "di_rajma_roti",
            "title": "Authentic Rajma Masala with Methi Rotis & Curd",
            "diet": ["VEGETARIAN", "EGGETARIAN"],
            "items": [
                "1 Big Bowl Kashmiri Rajma (Kidney Beans) in tomato-ginger gravy",
                "2 Fresh Fenugreek (Methi) Whole Wheat Rotis",
                "Small Bowl Fresh Low-Fat Curd",
                "Sliced Cucumber & Onion Salad"
            ],
            "allergens": ["DAIRY", "LACTOSE", "GLUTEN"],
            "protein_base": 24,
            "cal_base": 460,
            "highlight": "Potassium-rich complex carbohydrates aiding overnight muscle glycogen."
        },
        # Vegan
        {
            "id": "di_lentil_tofu",
            "title": "Yellow Dal Tadka with Grilled Tofu & Jowar Rotis",
            "diet": ["VEGAN", "VEGETARIAN"],
            "items": [
                "1 Big Bowl Yellow Moong/Arhar Dal with garlic & cumin tempering",
                "100g Lightly Sautéed Tofu steaks",
                "2 Gluten-Free Sorghum (Jowar) Rotis",
                "Warm Steamed Broccoli & Zucchini"
            ],
            "allergens": ["SOY"],
            "protein_base": 26,
            "cal_base": 450,
            "highlight": "Gluten-free night fuel supporting steady growth hormone secretion."
        }
    ]
}


def _matches_allergens(meal: Dict[str, Any], restrictions: str) -> bool:
    """Returns True if the meal contains any food allergen indicated by the user."""
    if not restrictions:
        return False
    user_words = [w.strip().upper() for w in restrictions.replace(",", " ").split() if len(w.strip()) > 2]
    meal_allergens = [a.upper() for a in meal.get("allergens", [])]

    for uw in user_words:
        # Check direct allergen match or substring match
        for ma in meal_allergens:
            if uw in ma or ma in uw:
                return True
        # Check text in title and items
        if uw in meal["title"].upper():
            return True
    return False


def generate_meal_plan(
    diet_preference: str = "VEGETARIAN",
    fitness_goal: str = "GENERAL_FITNESS",
    daily_calories: int = 2200,
    protein_target_g: int = 120,
    restrictions: str = ""
) -> Dict[str, Any]:
    """Selects and portion-scales 4 distinct Indian meals matching the user profile."""
    pref = diet_preference.upper().strip() if diet_preference else "VEGETARIAN"
    if pref not in ("VEGETARIAN", "NON_VEGETARIAN", "VEGAN", "EGGETARIAN"):
        pref = "VEGETARIAN"

    # Meal calorie allocation splits: Breakfast 25%, Lunch 35%, Snacks 15%, Dinner 25%
    splits = {
        "BREAKFAST": 0.25,
        "LUNCH": 0.35,
        "SNACKS": 0.15,
        "DINNER": 0.25
    }

    selected_meals = {}

    for category, split_pct in splits.items():
        catalog_items = MEAL_CATALOG.get(category, [])
        valid_candidates = []

        for meal in catalog_items:
            # Check diet compatibility
            if pref in meal["diet"]:
                # Check restrictions/allergens
                if not _matches_allergens(meal, restrictions):
                    valid_candidates.append(meal)

        # Fallback if all candidates filtered by strict restrictions
        if not valid_candidates:
            # Pick first compatible with diet ignoring non-critical allergens
            for meal in catalog_items:
                if pref in meal["diet"]:
                    valid_candidates.append(meal)
                    break
        if not valid_candidates:
            valid_candidates = [catalog_items[0]]

        chosen = valid_candidates[0]
        alt_meal = valid_candidates[1] if len(valid_candidates) > 1 else valid_candidates[0]
        cat_target_cals = int(round(daily_calories * split_pct))
        scale_factor = cat_target_cals / float(chosen["cal_base"]) if chosen["cal_base"] > 0 else 1.0

        scaled_protein = int(round(chosen["protein_base"] * scale_factor))
        scaled_cals = cat_target_cals

        meal_entry = {
            "category": category,
            "title": chosen["title"],
            "items": list(chosen["items"]),
            "estimated_calories": scaled_cals,
            "estimated_protein_g": scaled_protein,
            "highlight": chosen["highlight"],
            "primary": {
                "name": chosen["title"],
                "portion": chosen["items"][0] if chosen["items"] else "1 portion",
                "protein_g": scaled_protein,
                "calories": scaled_cals,
                "notes": chosen["highlight"]
            },
            "alternative": {
                "name": alt_meal["title"],
                "portion": alt_meal["items"][0] if alt_meal["items"] else "1 portion",
                "protein_g": alt_meal["protein_base"],
                "calories": alt_meal["cal_base"]
            }
        }
        selected_meals[category] = meal_entry
        selected_meals[category.lower()] = meal_entry

    return {
        "diet_preference": pref,
        "fitness_goal": fitness_goal,
        "daily_calories": daily_calories,
        "protein_target_g": protein_target_g,
        "restrictions_applied": restrictions.strip() if restrictions else "None",
        "meals": selected_meals,
        "breakfast": selected_meals["BREAKFAST"],
        "lunch": selected_meals["LUNCH"],
        "snacks": selected_meals["SNACKS"],
        "dinner": selected_meals["DINNER"],
        "disclaimer": "Educational athletic nutrition guidance. Not a medical or therapeutic prescription."
    }
