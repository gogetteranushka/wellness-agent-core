# File: hybrid_recommender.py

import pandas as pd
import numpy as np
import joblib
from recipe_recommender import MedicalAwareRecipeRecommender
from collaborative_models import SimpleUserCF, SimpleSVD

class HybridRecommender:
    """
    Combines TIER 2 (content-based) + TIER 3 (collaborative filtering)
    
    Strategy:
    1. TIER 2: Filter recipes by nutrition + medical safety (hard constraints)
    2. TIER 3: Predict user ratings for filtered recipes (personalization)
    3. Combine: 70% nutrition match + 30% predicted rating
    """
    
    def __init__(self, recipes_df, collaborative_model_path='models/collaborative_filter_best.pkl'):
        """Initialize hybrid recommender"""
        
        # Initialize TIER 2 recommender
        self.tier2 = MedicalAwareRecipeRecommender(recipes_df)
        self.recipes_df = recipes_df
        
        # Load TIER 3 model
        try:
            self.tier3_model = joblib.load(collaborative_model_path)
            self.has_tier3 = True
            print(f"✓ Loaded TIER 3 model: {collaborative_model_path}")
        except Exception as e:
            print(f"⚠️  Could not load TIER 3 model: {e}")
            print("   Falling back to TIER 2 only (content-based)")
            self.has_tier3 = False
    
    def recommend_hybrid(self, user_id, user_targets, medical_conditions=[], top_n=10):
        """
        Generate hybrid recommendations
        
        Args:
            user_id: User ID for personalization (can be None for new users)
            user_targets: Dict with nutrition targets
            medical_conditions: List of medical conditions
            top_n: Number of recommendations
        
        Returns:
            DataFrame with hybrid recommendations
        """
        
        # STEP 1: TIER 2 - Get nutritionally-safe candidates
        print(f"\n[TIER 2] Filtering recipes by nutrition + medical safety...")
        tier2_results = self.tier2.recommend(
            user_targets,
            medical_conditions=medical_conditions,
            top_n=50  # Get more candidates for TIER 3 to rank
        )
        
        if len(tier2_results) == 0:
            print("⚠️  No recipes found matching criteria")
            return pd.DataFrame()
        
        print(f"✓ TIER 2 found {len(tier2_results)} safe recipes")
        
        # STEP 2: TIER 3 - Predict user ratings (if available)
        if self.has_tier3 and user_id is not None:
            print(f"[TIER 3] Predicting ratings for User {user_id}...")
            tier2_results = self._add_tier3_scores(user_id, tier2_results)
            print(f"✓ TIER 3 predictions complete")
        else:
            # No TIER 3 or new user - use neutral score
            tier2_results['tier3_score'] = 50.0
            print("⚠️  Using TIER 2 only (no user history)")
        
        # STEP 3: Combine scores (70% nutrition, 30% preference)
        tier2_results['hybrid_score'] = (
            tier2_results['match_score'] * 0.7 + 
            tier2_results['tier3_score'] * 0.3
        )
        
        # STEP 4: Sort and return top N
        results = tier2_results.sort_values('hybrid_score', ascending=False).head(top_n)
        
        print(f"✓ Generated {len(results)} hybrid recommendations")
        return results
    
    def _add_tier3_scores(self, user_id, recipes_df):
        """Add TIER 3 collaborative filtering scores"""
        
        tier3_scores = []
        
        for idx, recipe in recipes_df.iterrows():
            try:
                # Get recipe ID from the DataFrame index
                recipe_id = recipe.name if hasattr(recipe, 'name') else idx
                
                # Get the actual recipe ID from Srno column
                if 'Srno' in recipe:
                    recipe_id = int(recipe['Srno'])
                
                # Predict rating using TIER 3 model
                predicted_rating = self.tier3_model.predict(user_id, recipe_id)
                
                # Convert rating (1-5) to score (0-100)
                tier3_score = (predicted_rating - 1) / 4 * 100
                tier3_scores.append(tier3_score)
                
            except Exception as e:
                # If prediction fails, use neutral score
                tier3_scores.append(50.0)
        
        recipes_df = recipes_df.copy()
        recipes_df['tier3_score'] = tier3_scores
        return recipes_df
    
    def explain_recommendation(self, recipe_name, tier2_score, tier3_score, hybrid_score):
        """Generate human-readable explanation"""
        
        explanation = f"\n🍽️  {recipe_name}\n"
        explanation += f"   Overall Score: {hybrid_score:.1f}/100\n\n"
        explanation += f"   Why recommended:\n"
        
        # Nutrition match
        if tier2_score >= 80:
            explanation += f"   ✓ Excellent nutrition match ({tier2_score:.1f}/100)\n"
        elif tier2_score >= 70:
            explanation += f"   ✓ Good nutrition match ({tier2_score:.1f}/100)\n"
        else:
            explanation += f"   ⚠️  Moderate nutrition match ({tier2_score:.1f}/100)\n"
        
        # Preference match
        if self.has_tier3:
            if tier3_score >= 80:
                explanation += f"   ✓ Predicted you'll love it ({tier3_score:.1f}/100)\n"
            elif tier3_score >= 70:
                explanation += f"   ✓ Predicted you'll like it ({tier3_score:.1f}/100)\n"
            elif tier3_score >= 60:
                explanation += f"   • Based on similar users ({tier3_score:.1f}/100)\n"
            else:
                explanation += f"   ⚠️  Might not match your taste ({tier3_score:.1f}/100)\n"
        
        return explanation


# Test function
def test_hybrid_recommender():
    """Test the hybrid recommender"""
    print("="*80)
    print("TESTING HYBRID RECOMMENDER (TIER 2 + TIER 3)")
    print("="*80)
    
    # Load data
    recipes_df = pd.read_csv('data/recipe_nutrients_cleaned.csv')
    
    # Initialize hybrid recommender
    hybrid = HybridRecommender(recipes_df)
    
    # Test user profile
    user_targets = {
        'course': 'Breakfast',
        'calories': 400,
        'protein_g': 20,
        'carbs_g': 40,
        'fat_g': 15,
        'diet': 'Vegetarian',
        'max_time_mins': 45
    }
    
    medical_conditions = ['diabetes', 'hypertension']
    user_id = 1  # Test with User 1 from synthetic data
    
    # Get recommendations
    print(f"\n🔍 Getting hybrid recommendations for User {user_id}...")
    print(f"   Medical conditions: {', '.join(medical_conditions)}")
    print(f"   Dietary preference: {user_targets['diet']}")
    
    results = hybrid.recommend_hybrid(
        user_id=user_id,
        user_targets=user_targets,
        medical_conditions=medical_conditions,
        top_n=5
    )
    
    if len(results) > 0:
        print("\n" + "="*80)
        print("📊 TOP 5 HYBRID RECOMMENDATIONS")
        print("="*80)
        
        for i, (_, recipe) in enumerate(results.iterrows(), 1):
            print(hybrid.explain_recommendation(
                recipe['RecipeName'],
                recipe['match_score'],
                recipe.get('tier3_score', 50),
                recipe['hybrid_score']
            ))
            
            # Show nutrition details
            print(f"   📊 Nutrition: {recipe['energy_per_serving']:.0f} cal | "
                  f"{recipe['protein_per_serving']:.1f}g P | "
                  f"{recipe['carbohydrate_per_serving']:.1f}g C | "
                  f"{recipe['fat_per_serving']:.1f}g F")
            print(f"   ⏱️  Time: {recipe['TotalTimeInMins']:.0f} minutes")
            print()
    
    print("="*80)
    print("✅ HYBRID RECOMMENDER TEST COMPLETE")
    print("="*80)


if __name__ == '__main__':
    test_hybrid_recommender()
