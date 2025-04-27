"""
Utilities for currency conversion and price handling.
"""
import logging
import os
import json
import requests
from datetime import datetime, timedelta

# Default exchange rates (in case API is unavailable)
DEFAULT_EXCHANGE_RATES = {
    'USD': 18.5,  # Example rate - 1 USD = 18.5 ZAR
    'EUR': 20.2,  # Example rate - 1 EUR = 20.2 ZAR
    'GBP': 23.4,  # Example rate - 1 GBP = 23.4 ZAR
    'ZAR': 1.0    # Base currency
}

# Path to cached exchange rates
CACHE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                         'data', 'exchange_rates.json')


def get_exchange_rates():
    """
    Get current exchange rates from API or cache.
    
    Returns:
        dict: Exchange rates with ZAR as base currency
    """
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    # Check if we have cached rates less than 24 hours old
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                
            # Check if cache is still valid (less than 24 hours old)
            cache_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cache_time < timedelta(hours=24):
                logging.info("Using cached exchange rates")
                return data['rates']
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logging.warning(f"Error reading cached exchange rates: {e}")
    
    # Try to get fresh rates from API
    try:
        # You would need to sign up for a free API key at exchangerate-api.com 
        # or a similar service
        API_KEY = os.environ.get('EXCHANGE_RATE_API_KEY', '')
        if not API_KEY:
            logging.warning("No API key for exchange rates, using default values")
            return DEFAULT_EXCHANGE_RATES
            
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/ZAR"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['result'] == 'success':
            # Convert to ZAR-based rates (invert because API gives rates for converting from ZAR)
            rates = {
                'ZAR': 1.0,
                'USD': 1.0 / data['conversion_rates']['USD'],
                'EUR': 1.0 / data['conversion_rates']['EUR'],
                'GBP': 1.0 / data['conversion_rates']['GBP']
            }
            
            # Cache the rates
            with open(CACHE_FILE, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'rates': rates
                }, f, indent=2)
                
            logging.info("Updated exchange rates from API")
            return rates
    except Exception as e:
        logging.error(f"Error fetching exchange rates: {e}")
    
    # If all else fails, use default rates
    logging.warning("Using default exchange rates")
    return DEFAULT_EXCHANGE_RATES


def convert_to_zar(price, currency='ZAR'):
    """
    Convert a price from any currency to ZAR.
    
    Args:
        price (float): The price to convert
        currency (str): Currency code (USD, EUR, GBP, ZAR)
        
    Returns:
        float: Price in ZAR
    """
    if price is None or price == 0:
        return None
        
    # Get current exchange rates
    rates = get_exchange_rates()
    
    # Apply exchange rate
    rate = rates.get(currency.upper(), 1.0)
    converted_price = price * rate
    
    return round(converted_price, 2)