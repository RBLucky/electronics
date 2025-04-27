"""
Utilities for matching similar products across different websites.
"""
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def group_similar_products(df, similarity_threshold=0.7):
    """
    Group similar products using text similarity on normalized names.
    
    Args:
        df (DataFrame): DataFrame containing product data
        similarity_threshold (float): Threshold for considering products similar (0.0-1.0)
        
    Returns:
        list: List of groups, where each group is a list of similar products
    """
    if df.empty or 'normalized_name' not in df.columns:
        return []
        
    # Extract names for vectorization
    names = df['normalized_name'].fillna('').tolist()
    
    # Use TF-IDF vectorization for better matching
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    
    try:
        tfidf_matrix = vectorizer.fit_transform(names)
    except ValueError:
        # Handle case where all names are empty or contain only stop words
        return []
    
    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Group similar products (similarity > threshold)
    groups = []
    used_indices = set()
    
    for i in range(len(names)):
        if i in used_indices:
            continue
            
        # Find similar products
        group = [i]
        used_indices.add(i)
        
        for j in range(len(names)):
            if j != i and j not in used_indices and similarity_matrix[i, j] > similarity_threshold:
                group.append(j)
                used_indices.add(j)
        
        if len(group) > 1:  # Only keep groups with multiple products
            groups.append([df.iloc[idx] for idx in group])
    
    return groups


def find_exact_matches(df, keys=None):
    """
    Find exact matches based on specific keys.
    
    Args:
        df (DataFrame): DataFrame containing product data
        keys (list): List of columns to use for matching
        
    Returns:
        list: List of groups of matching products
    """
    if df.empty:
        return []
        
    if keys is None:
        keys = ['normalized_name']
    
    # Ensure all keys exist in the DataFrame
    valid_keys = [k for k in keys if k in df.columns]
    if not valid_keys:
        return []
    
    # Group by the specified keys
    grouped = df.groupby(valid_keys)
    
    # Extract groups with more than one item
    result = []
    for _, group in grouped:
        if len(group) > 1:
            result.append(group.to_dict('records'))
    
    return result


def enhance_product_matching(df):
    """
    Enhanced product matching combining multiple techniques.
    
    Args:
        df (DataFrame): DataFrame containing product data
        
    Returns:
        list: List of groups of matching products
    """
    # First try exact matches on normalized names
    exact_matches = find_exact_matches(df, ['normalized_name'])
    
    # Then use similarity matching for remaining products
    used_indices = set()
    for group in exact_matches:
        for item in group:
            idx = df[df['name'] == item['name']].index
            if not idx.empty:
                used_indices.add(idx[0])
    
    remaining_df = df.drop(list(used_indices))
    similarity_matches = group_similar_products(remaining_df)
    
    # Combine results
    all_matches = exact_matches + similarity_matches
    
    return all_matches