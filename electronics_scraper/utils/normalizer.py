"""
Utilities for normalizing product names and descriptions.
"""
import re


def normalize_product_name(name):
    """
    Normalize product names for better matching.
    
    Args:
        name (str): The product name to normalize
        
    Returns:
        str: Normalized product name
    """
    if not isinstance(name, str):
        return ""
        
    # Convert to lowercase
    name = name.lower()
    
    # Remove common words that don't help with matching
    stopwords = ['new', 'used', 'refurbished', 'like', 'condition', 'grade', 'certified']
    for word in stopwords:
        name = re.sub(r'\b' + word + r'\b', '', name)
    
    # Standardize spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Standardize common product names
    patterns = {
        # iPhones
        r'iphone\s*(\d+)\s*(pro)?\s*(max)?': r'iphone \1 \2 \3',
        r'iphone\s*(\d+)\s*(plus)': r'iphone \1 plus',
        r'iphone\s*(\d+)\s*(mini)': r'iphone \1 mini',
        
        # Samsung Galaxy
        r'galaxy\s*s(\d+)': r'galaxy s\1',
        r'galaxy\s*note\s*(\d+)': r'galaxy note \1',
        r'galaxy\s*a(\d+)': r'galaxy a\1',
        
        # Apple Products
        r'airpods\s*(pro)?\s*(gen|generation)?\s*(\d+)?': r'airpods \1 \3',
        r'macbook\s*(pro|air)?\s*(\d+)?"?': r'macbook \1 \2"',
        r'apple\s*watch\s*(series)?\s*(\d+)': r'apple watch series \2',
        r'ipad\s*(pro|air|mini)?\s*(\d+)?': r'ipad \1 \2',
        
        # Storage capacity
        r'(\d+)\s*gb': r'\1gb',
        r'(\d+)\s*tb': r'\1tb',
        
        # Colors
        r'(black|white|gold|silver|gray|grey|blue|red|green|yellow|purple)': r'\1'
    }
    
    for pattern, replacement in patterns.items():
        name = re.sub(pattern, replacement, name)
    
    # Remove remaining special characters
    name = re.sub(r'[^\w\s]', ' ', name)
    
    # Final cleanup of spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name


def extract_specs(specs_text):
    """
    Extract specifications from text into a dictionary.
    
    Args:
        specs_text (str): Text containing product specifications
        
    Returns:
        dict: Extracted specifications
    """
    specs = {}
    if not specs_text or not isinstance(specs_text, str):
        return specs
        
    # Common patterns for electronics specs
    patterns = {
        'storage': r'(\d+)\s*(GB|TB|MB)',
        'ram': r'(\d+)\s*(GB|MB)\s*RAM',
        'processor': r'(i\d|ryzen|snapdragon|a\d+|m\d+)[\s\-](\d+)',
        'screen': r'(\d+\.?\d*)"',
        'battery': r'(\d+)\s*mAh',
        'camera': r'(\d+)\s*MP',
        'condition': r'(new|used|refurbished|like new|excellent|good|fair)',
        'model_year': r'(20\d\d)'
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, specs_text, re.IGNORECASE)
        if match:
            specs[key] = match.group(0).strip()
                
    return specs