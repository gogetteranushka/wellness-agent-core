# File: collaborative_models.py

import numpy as np
import pandas as pd

class SimpleSVD:
    """Simple SVD-based collaborative filter"""
    
    def __init__(self, U, sigma, Vt, user_means, user_ids, recipe_ids):
        self.U = U
        self.sigma = sigma
        self.Vt = Vt
        self.user_means = user_means
        self.user_ids = user_ids
        self.recipe_ids = recipe_ids
        self.user_id_to_idx = {uid: idx for idx, uid in enumerate(user_ids)}
        self.recipe_id_to_idx = {rid: idx for idx, rid in enumerate(recipe_ids)}
    
    def predict(self, user_id, recipe_id):
        """Predict rating for user-recipe pair"""
        try:
            user_idx = self.user_id_to_idx.get(user_id)
            recipe_idx = self.recipe_id_to_idx.get(recipe_id)
            
            if user_idx is None or recipe_idx is None:
                return 3.5
            
            pred = np.dot(np.dot(self.U[user_idx], self.sigma), self.Vt[:, recipe_idx])
            pred += self.user_means.iloc[user_idx]
            
            return np.clip(pred, 1, 5)
        
        except:
            return 3.5


class SimpleUserCF:
    """Simple user-based collaborative filter"""
    
    def __init__(self, rating_matrix, similarity_matrix, k=20):
        self.rating_matrix = rating_matrix
        self.similarity_matrix = similarity_matrix
        self.k = k
        self.global_mean = rating_matrix.replace(0, np.nan).mean().mean()
    
    def predict(self, user_id, recipe_id):
        """Predict rating using k nearest neighbors"""
        try:
            if user_id not in self.similarity_matrix.index:
                return self.global_mean
            
            if recipe_id not in self.rating_matrix.columns:
                return self.global_mean
            
            # Get top k similar users
            similar_users = self.similarity_matrix[user_id].sort_values(ascending=False)[1:self.k+1]
            
            # Get ratings from similar users
            ratings = []
            weights = []
            
            for sim_user, similarity in similar_users.items():
                if similarity > 0:
                    rating = self.rating_matrix.loc[sim_user, recipe_id]
                    if rating > 0:
                        ratings.append(rating)
                        weights.append(similarity)
            
            if len(ratings) == 0:
                return self.global_mean
            
            # Weighted average
            pred = np.average(ratings, weights=weights)
            return np.clip(pred, 1, 5)
        
        except:
            return self.global_mean
