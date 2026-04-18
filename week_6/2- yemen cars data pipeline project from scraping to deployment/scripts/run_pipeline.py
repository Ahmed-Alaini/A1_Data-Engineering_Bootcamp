import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from pipeline.extract.scrapper import scrape_yemen_cars
from pipeline.transform.processing import main as transform_data
from pipeline.load.loading import create_table, load_csv

def main():
    print(" Starting Data Engineering Pipeline...")
    
    print("\n--- Step 1: Extract (Scraping Data from OpenSooq) ---")
    try:
        scrape_yemen_cars()
    except Exception as e:
        print(f"Error during Data Extraction: {e}")
        return
        
    print("\n--- Step 2: Transform (Cleaning and Processing Data) ---")
    try:
        transform_data()
    except Exception as e:
        print(f"Error during Data Transformation: {e}")
        return
        
    print("\n--- Step 3: Load (Saving to PostgreSQL Database) ---")
    try:
        cars_csv = project_root / "data" / "processed" / "yemen_cars_cleaned.csv"
        create_table()
        load_csv(cars_csv)
    except Exception as e:
        print(f" Error during Data Loading: {e}")
        return
        
    print("\n Pipeline execution completed successfully!")

if __name__ == "__main__":
    main()
