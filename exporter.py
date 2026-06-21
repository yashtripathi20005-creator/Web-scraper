"""
Data export utilities
"""
import json
import csv
import os
from typing import Dict, List
from datetime import datetime
import pandas as pd

from config import Config


class DataExporter:
    """Handle data export in various formats"""
    
    def __init__(self):
        self.config = Config()
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.config.OUTPUT_DIR):
            os.makedirs(self.config.OUTPUT_DIR)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for filename"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def export_json(self, data: Dict[str, List[Dict]], filename: str = None) -> str:
        """
        Export data to JSON format
        
        Args:
            data: Dictionary of source data
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = self._get_timestamp()
            filename = f"headlines_{timestamp}.json"
        
        filepath = os.path.join(self.config.OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON data exported to: {filepath}")
        return filepath
    
    def export_csv(self, data: Dict[str, List[Dict]], filename: str = None) -> str:
        """
        Export data to CSV format
        
        Args:
            data: Dictionary of source data
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not filename:
            timestamp = self._get_timestamp()
            filename = f"headlines_{timestamp}.csv"
        
        filepath = os.path.join(self.config.OUTPUT_DIR, filename)
        
        # Flatten the data for CSV
        rows = []
        for source, headlines in data.items():
            for item in headlines:
                rows.append({
                    'source': source,
                    'headline': item.get('headline', ''),
                    'link': item.get('link', ''),
                    'timestamp': item.get('timestamp', '')
                })
        
        if rows:
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"✅ CSV data exported to: {filepath}")
        else:
            print("⚠️ No data to export to CSV")
        
        return filepath
    
    def export_all(self, data: Dict[str, List[Dict]]) -> Dict[str, str]:
        """
        Export data in all configured formats
        
        Args:
            data: Dictionary of source data
            
        Returns:
            Dictionary with format names as keys and file paths as values
        """
        results = {}
        
        if self.config.OUTPUT_FORMAT in ['json', 'both']:
            results['json'] = self.export_json(data)
        
        if self.config.OUTPUT_FORMAT in ['csv', 'both']:
            results['csv'] = self.export_csv(data)
        
        return results
    
    def print_summary(self, data: Dict[str, List[Dict]]):
        """
        Print a summary of scraped data to console
        
        Args:
            data: Dictionary of source data
        """
        print("\n" + "="*60)
        print("📰 HEADLINE SCRAPER SUMMARY")
        print("="*60)
        
        total_headlines = 0
        
        for source, headlines in data.items():
            count = len(headlines)
            total_headlines += count
            print(f"\n📌 {source.upper()}: {count} headlines")
            
            # Print first 3 headlines as preview
            for i, item in enumerate(headlines[:3], 1):
                print(f"   {i}. {item.get('headline', 'N/A')}")
                print(f"      🔗 {item.get('link', 'N/A')}")
            
            if count > 3:
                print(f"   ... and {count - 3} more")
        
        print("\n" + "="*60)
        print(f"📊 Total headlines extracted: {total_headlines}")
        print("="*60 + "\n")
