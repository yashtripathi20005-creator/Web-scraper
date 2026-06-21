"""
Main entry point for the web scraper
"""
import sys
import argparse
from scraper import WebScraper
from exporter import DataExporter
from config import Config


def main():
    """Main function to run the web scraper"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Web Scraper for News Headlines')
    parser.add_argument(
        '--source',
        type=str,
        help='Specific source to scrape (bbc, cnn, reuters, aljazeera)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'csv', 'both'],
        help='Output format (default: from config)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output directory (default: from config)'
    )
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🚀 STARTING WEB SCRAPER")
    print("="*60)
    
    # Initialize scraper and exporter
    scraper = WebScraper()
    exporter = DataExporter()
    
    # Override config if arguments provided
    if args.format:
        Config.OUTPUT_FORMAT = args.format
    if args.output:
        Config.OUTPUT_DIR = args.output
        exporter._ensure_output_dir()
    
    # Scrape data
    if args.source:
        # Scrape single source
        if args.source not in Config.SOURCES:
            print(f"❌ Error: Source '{args.source}' not found.")
            print(f"Available sources: {', '.join(Config.SOURCES.keys())}")
            sys.exit(1)
        
        print(f"🎯 Scraping single source: {args.source}")
        data = {}
        headlines = scraper.scrape_source(args.source, Config.SOURCES[args.source])
        data[args.source] = headlines
    else:
        # Scrape all sources
        print("🌐 Scraping all sources...")
        data = scraper.scrape_all_sources()
    
    # Export data
    if any(data.values()):
        exporter.print_summary(data)
        exporter.export_all(data)
        print("✅ Scraping completed successfully!")
    else:
        print("❌ No data was scraped. Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
