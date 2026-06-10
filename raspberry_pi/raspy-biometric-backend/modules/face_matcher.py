"""
Face Matcher - Compare embeddings dan recognize faces
"""
import numpy as np
from scipy.spatial.distance import cosine


class FaceMatcher:
    """Match test embedding against database embeddings"""
    
    def __init__(self, similarity_threshold=0.5):
        self.similarity_threshold = similarity_threshold
    
    def calculate_similarity(self, embedding1, embedding2):
        """
        Calculate similarity between two embeddings (0-1)
        Using cosine similarity: 1 - cosine_distance
        
        Args:
            embedding1: numpy array (512-dim)
            embedding2: numpy array (512-dim)
        
        Returns:
            similarity: float (0-1), 1 = identical, 0 = completely different
        """
        try:
            # Normalize embeddings
            emb1 = np.array(embedding1) / np.linalg.norm(embedding1)
            emb2 = np.array(embedding2) / np.linalg.norm(embedding2)
            
            # Cosine similarity: dot product of normalized vectors
            similarity = np.dot(emb1, emb2)
            
            # Clamp to [0, 1]
            similarity = max(0.0, min(1.0, similarity))
            
            return similarity
        
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    
    def match_face(self, test_embedding, embeddings_dict):
        """
        Match test embedding against all database embeddings
        
        Args:
            test_embedding: numpy array (512-dim)
            embeddings_dict: dict from db_manager.get_all_embeddings()
                {
                    'user_001': {'name': 'Budi', 'embeddings': [...]},
                    'user_002': {'name': 'Rina', 'embeddings': [...]},
                    ...
                }
        
        Returns:
            {
                'matched': bool,
                'user_id': str or None,
                'name': str or None,
                'confidence': float,
                'all_matches': [...]  # List of all matches sorted by similarity
            }
        """
        if not embeddings_dict:
            return {
                'matched': False,
                'user_id': None,
                'name': None,
                'confidence': 0.0,
                'all_matches': []
            }
        
        test_emb = np.array(test_embedding)
        
        all_matches = []
        best_match = None
        best_similarity = 0.0
        
        # Compare dengan semua users
        for user_id, user_data in embeddings_dict.items():
            user_name = user_data['name']
            user_embeddings = user_data['embeddings']
            
            # Calculate average similarity to this user
            similarities = []
            for stored_emb in user_embeddings:
                sim = self.calculate_similarity(test_emb, stored_emb)
                similarities.append(sim)
            
            avg_similarity = np.mean(similarities)
            max_similarity = np.max(similarities)
            
            # Store match result
            match_result = {
                'user_id': user_id,
                'name': user_name,
                'avg_similarity': float(avg_similarity),
                'max_similarity': float(max_similarity),
                'num_embeddings': len(user_embeddings)
            }
            all_matches.append(match_result)
            
            # Update best match
            if avg_similarity > best_similarity:
                best_similarity = avg_similarity
                best_match = {
                    'user_id': user_id,
                    'name': user_name,
                    'similarity': avg_similarity
                }
        
        # Sort all matches by similarity
        all_matches.sort(key=lambda x: x['avg_similarity'], reverse=True)
        
        # Determine if match is good enough
        matched = best_similarity >= self.similarity_threshold if best_match else False
        
        return {
            'matched': matched,
            'user_id': best_match['user_id'] if best_match else None,
            'name': best_match['name'] if best_match else None,
            'confidence': float(best_similarity) if best_match else 0.0,
            'all_matches': all_matches
        }
    
    def batch_match(self, embeddings_list, embeddings_dict):
        """
        Match multiple embeddings
        
        Args:
            embeddings_list: list of embeddings
            embeddings_dict: database embeddings
        
        Returns:
            List of match results
        """
        results = []
        for emb in embeddings_list:
            result = self.match_face(emb, embeddings_dict)
            results.append(result)
        
        return results
    
    def set_threshold(self, threshold):
        """Set similarity threshold (0-1)"""
        if 0 <= threshold <= 1:
            self.similarity_threshold = threshold
        else:
            print(f"Invalid threshold {threshold}, keeping {self.similarity_threshold}")
