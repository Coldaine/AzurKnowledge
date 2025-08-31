from scraper import AzurLaneScraper
from utils import commit_changes

# Load list of items to process
items_to_process = [
    ("Twin 127mm (5\"/38 Mk 38)", "destroyer_guns"),
    ("Triple 152mm Main Gun", "light_cruiser_guns"),
    ("203mm/53 Twin Gun Mount", "heavy_cruiser_guns"),
    ("305mm/50 Twin Gun Mount", "large_cruiser_guns"),
    ("410mm/45 Triple Gun Mount", "battleship_guns"),
    ("Type 96 25mm AA Gun", "anti_air_guns"),
    ("Type 93 Torpedo", "ship_torpedoes"),
    ("Type 95 Torpedo", "submarine_torpedoes"),
    ("A6M Zero Fighter", "fighters"),
    ("D3A1 Val Dive Bomber", "dive_bombers"),
    ("B5N2 Kate Torpedo Bomber", "torpedo_bombers"),
    ("F1M Pete Seaplane", "seaplanes"),
    ("Radar Type 0", "auxiliary_equipment"),
    ("Fire Control System", "augment_modules"),
    ("Depth Charge", "anti_submarine_equipment"),
]

def main():
    scraper = AzurLaneScraper()
    batch = []
    batch_status = []

    for item_name, equipment_type in items_to_process:
        print(f"Processing: {item_name}")
        item_data = scraper.scrape_item(item_name, equipment_type)
        status = scraper.save_item(item_data, equipment_type)
        
        batch.append(item_name)
        batch_status.append(status)
        
        # Commit every 5 items
        if len(batch) >= 5:
            commit_status = "Mixed" if len(set(batch_status)) > 1 else batch_status[0]
            commit_changes(batch, commit_status)
            batch = []
            batch_status = []

    # Commit remaining items
    if batch:
        commit_status = "Mixed" if len(set(batch_status)) > 1 else batch_status[0]
        commit_changes(batch, commit_status)

if __name__ == "__main__":
    main()