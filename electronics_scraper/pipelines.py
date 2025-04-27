"""
Data processing pipeline for the electronics scraper.
"""
import os
import json
import logging
import pandas as pd
from datetime import datetime

from electronics_scraper.utils.normalizer import normalize_product_name
from electronics_scraper.utils.currency import convert_to_zar
from electronics_scraper.utils.matcher import group_similar_products


class DataProcessingPipeline:
    """Pipeline for processing and analyzing scraped data"""
    
    def __init__(self):
        self.data = []
        self.file_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
    
    def process_item(self, item, spider):
        """Process each scraped item"""
        # Add normalized product name
        item['normalized_name'] = normalize_product_name(item.get('name', ''))
        
        # Convert price to ZAR
        item['price_zar'] = convert_to_zar(item.get('price'), item.get('currency', 'ZAR'))
        
        # Store processed item
        self.data.append(dict(item))
        
        return item
    
    def close_spider(self, spider):
        """Process all data after spider completes"""
        logging.info(f"Spider {spider.name} finished. Processing collected data...")
        
        if not self.data:
            logging.warning(f"No data collected by {spider.name}")
            return
        
        # If this is the first spider to finish, initialize the output files
        self._create_or_update_output_files(spider)
    
    def _create_or_update_output_files(self, spider):
        """Create or update output files with current data"""
        # Convert data to DataFrame for easier processing
        df = pd.DataFrame(self.data)
        
        # Save raw data
        df.to_csv(f'results/raw_data_{self.file_timestamp}.csv', index=False, mode='a')
        
        # Save as JSON too
        with open(f'results/raw_data_{self.file_timestamp}.json', 'w') as f:
            json.dump(self.data, f, indent=2)
        
        # Find arbitrage opportunities
        self._find_opportunities()
        
        # Clear data for next spider
        self.data = []
    
    def _find_opportunities(self):
        """Find and save arbitrage opportunities"""
        # Load all data if exists, otherwise use current data
        try:
            df = pd.read_csv(f'results/raw_data_{self.file_timestamp}.csv')
        except FileNotFoundError:
            df = pd.DataFrame(self.data)
        
        if df.empty:
            logging.warning("No data available for finding opportunities")
            return
        
        # Group similar products
        groups = group_similar_products(df)
        
        # Find arbitrage opportunities
        opportunities = self._find_arbitrage_opportunities(groups)
        
        # Save results
        self._save_results(df, groups, opportunities)
    
    def _find_arbitrage_opportunities(self, groups):
        """Find price differences that create arbitrage opportunities"""
        opportunities = []
        
        for group in groups:
            if len(group) < 2:
                continue
                
            # Convert group to DataFrame for easier analysis
            group_df = pd.DataFrame(group)
            
            # Filter out items with no price
            group_df = group_df[group_df['price_zar'].notna()]
            
            if len(group_df) < 2:
                continue
                
            # Find min and max prices
            min_price_idx = group_df['price_zar'].idxmin()
            max_price_idx = group_df['price_zar'].idxmax()
            
            min_price_item = group_df.iloc[min_price_idx]
            max_price_item = group_df.iloc[max_price_idx]
            
            # Calculate potential profit
            price_diff = max_price_item['price_zar'] - min_price_item['price_zar']
            profit_margin = price_diff / min_price_item['price_zar'] * 100
            
            # If potential profit margin is significant (>10%)
            if profit_margin > 10:
                opportunities.append({
                    'buy_item': min_price_item.to_dict(),
                    'sell_comparison': max_price_item.to_dict(),
                    'price_difference': float(price_diff),
                    'profit_margin_percent': float(profit_margin),
                    'group': [item.to_dict() for item in group]
                })
        
        # Sort by profit margin
        opportunities.sort(key=lambda x: x['profit_margin_percent'], reverse=True)
        
        return opportunities
    
    def _save_results(self, df, groups, opportunities):
        """Save the results to disk"""
        # Save opportunities
        with open(f'results/opportunities_{self.file_timestamp}.json', 'w') as f:
            json.dump(opportunities, f, indent=2)
        
        # Create an HTML report
        self._create_html_report(opportunities)
        
        logging.info(f"Found {len(opportunities)} arbitrage opportunities")
        logging.info(f"Results saved to results/opportunities_{self.file_timestamp}.json")
    
    def _create_html_report(self, opportunities):
        """Create an HTML report of arbitrage opportunities"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Electronics Arbitrage Opportunities</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .opportunity { border: 1px solid #ddd; margin: 20px 0; padding: 15px; border-radius: 5px; }
                .profit { font-size: 1.2em; font-weight: bold; color: green; }
                .item { margin: 10px 0; padding: 10px; background-color: #f9f9f9; }
                .price { font-weight: bold; }
                .group { margin-top: 20px; }
                h1, h2 { color: #333; }
                .buy { background-color: #e6ffe6; }
                .sell { background-color: #ffe6e6; }
            </style>
        </head>
        <body>
            <h1>Electronics Arbitrage Opportunities</h1>
            <p>Report generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
        """
        
        for i, opp in enumerate(opportunities):
            profit = opp['price_difference']
            margin = opp['profit_margin_percent']
            
            html += f"""
            <div class="opportunity">
                <h2>Opportunity #{i+1}</h2>
                <div class="profit">Potential Profit: R{profit:.2f} (Margin: {margin:.1f}%)</div>
                
                <div class="item buy">
                    <h3>BUY FROM: {opp['buy_item']['website']}</h3>
                    <p>{opp['buy_item']['name']}</p>
                    <p class="price">Price: R{opp['buy_item']['price_zar']:.2f}</p>
                    <p>URL: <a href="{opp['buy_item']['url']}" target="_blank">View Item</a></p>
                </div>
                
                <div class="item sell">
                    <h3>COMPARE WITH: {opp['sell_comparison']['website']}</h3>
                    <p>{opp['sell_comparison']['name']}</p>
                    <p class="price">Price: R{opp['sell_comparison']['price_zar']:.2f}</p>
                    <p>URL: <a href="{opp['sell_comparison']['url']}" target="_blank">View Item</a></p>
                </div>
                
                <div class="group">
                    <h3>All Similar Items:</h3>
            """
            
            for item in opp['group']:
                html += f"""
                    <div class="item">
                        <p>{item['name']} - {item['website']}</p>
                        <p class="price">Price: R{item['price_zar']:.2f}</p>
                        <p>URL: <a href="{item['url']}" target="_blank">View Item</a></p>
                    </div>
                """
            
            html += """
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        with open(f'results/opportunities_report_{self.file_timestamp}.html', 'w') as f:
            f.write(html)