# Azur Lane Equipment Database - Repository Setup Plan

## Repository Structure

```
azur-lane-equipment-db/
├── data/
│   ├── equipment/
│   │   ├── destroyer_guns.json
│   │   ├── light_cruiser_guns.json
│   │   ├── heavy_cruiser_guns.json
│   │   ├── large_cruiser_guns.json
│   │   ├── battleship_guns.json
│   │   ├── anti_air_guns.json
│   │   ├── ship_torpedoes.json
│   │   ├── submarine_torpedoes.json
│   │   ├── fighters.json
│   │   ├── dive_bombers.json
│   │   ├── torpedo_bombers.json
│   │   ├── seaplanes.json
│   │   ├── auxiliary_equipment.json
│   │   ├── augment_modules.json
│   │   └── anti_submarine_equipment.json
│   ├── schema_example.json
│   └── raw/
│       └── (temporary scraping cache)
├── scripts/
│   ├── scraper.py
│   ├── parser.py
│   ├── run_collection.py
│   └── utils.py
├── logs/
│   └── scraping.log
├── .gitignore
├── README.md
├── requirements.txt
└── progress.json
```

## Step-by-Step Setup

### 1. Initialize Repository
```bash
mkdir azur-lane-equipment-db
cd azur-lane-equipment-db
git init
```

### 2. Create Initial Files

#### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
.env
venv/

# Data files
data/raw/
*.tmp
*.bak

# Logs
logs/*.log.*

# OS
.DS_Store
Thumbs.db
```

#### `requirements.txt`
```
requests==2.31.0
beautifulsoup4==4.12.3
lxml==5.1.0
```

#### `README.md`
```markdown
# Azur Lane Equipment Database

Personal database for Azur Lane equipment and augmentation modules.

## Structure
- `data/equipment/` - JSON files organized by equipment type
- `scripts/` - Data collection scripts
- `logs/` - Scraping logs

## Data Format
Each equipment entry follows the schema defined in `data/schema_example.json`

## Progress
See `progress.json` for collection status
```

### 3. Create Data Schema

#### `data/equipment/destroyer_guns.json` (start with empty array)
```json
[]
```

#### `data/schema_example.json` (for reference)
```json
{
  "_example": {
    "identity": {
      "itemName": "string",
      "itemID": "integer",
      "rarity": "string",
      "type": "string",
      "faction": "string"
    },
    "source": {
      "acquisitionMethod": ["array"],
      "isCraftable": "boolean"
    },
    "stats_numerical": {
      "firepower": "integer",
      "anti_air": "integer",
      "damage": "integer",
      "numberOfShots": "integer",
      "baseReload": "float",
      "range": "integer",
      "ammoType": "string"
    },
    "stats_qualitative_visual": {
      "firingPattern": "string",
      "shellOrdnanceVelocity": "string",
      "visualDataURL": "string"
    },
    "derived_analysis": {
      "primaryRole": ["array"],
      "strengths": ["array"],
      "weaknesses": ["array"],
      "communityTier": "string",
      "notes": "string"
    },
    "metadata": {
      "lastUpdated": "ISO-date",
      "dataCompleteness": "complete|partial|basic",
      "sources": ["array"]
    }
  }
}
```

### 4. Create Basic Scripts

#### `scripts/utils.py`
```python
import json
import os
import subprocess
from datetime import datetime

def load_json(filepath):
    """Load JSON file, return empty list if not exists"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data to JSON with pretty formatting"""
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_progress(item_name, status):
    """Update progress tracking"""
    progress_file = 'progress.json'
    progress = load_json(progress_file)
    if not progress:
        progress = {
            "completed": [],
            "partial": [],
            "failed": [],
            "retry_queue": [],
            "last_updated": ""
        }
    
    # Remove from other lists if exists
    for list_name in ['completed', 'partial', 'failed']:
        if item_name in progress[list_name]:
            progress[list_name].remove(item_name)
    
    # Add to appropriate list
    if status in ['completed', 'partial', 'failed']:
        progress[status].append(item_name)
    
    progress['last_updated'] = datetime.now().isoformat()
    save_json(progress, progress_file)

def commit_changes(item_names, status):
    """Create git commit with item names"""
    # Stage tracked data and progress files
    subprocess.run(['git', 'add', 'data/equipment', 'progress.json'], check=False)

    # Create commit message (limit item list for brevity)
    items = ', '.join(item_names[:3])
    if len(item_names) > 3:
        items += f' (+{len(item_names)-3} more)'
    message = f"Update: {items} - {status}"

    # Commit only if there are staged changes
    has_changes = subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode != 0
    if has_changes:
        subprocess.run(['git', 'commit', '-m', message], check=False)
    else:
        print('No staged changes to commit.')
```

#### `scripts/scraper.py` (Basic template)
```python
import requests
from bs4 import BeautifulSoup
import time
import logging
import os
from datetime import datetime
from utils import load_json, save_json, update_progress, commit_changes

logging.basicConfig(
    filename='logs/scraping.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AzurLaneScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Ensure log directory exists
        os.makedirs('logs', exist_ok=True)
        # Polite defaults
        self.request_timeout = 10
        self.delay_seconds = 1.0
    
    def scrape_item(self, item_name, equipment_type):
        """Main method to scrape a single item"""
        logging.info(f"Starting scrape for: {item_name}")
        
        item_data = {
            # Keep type as canonical slug matching file names (e.g., 'destroyer_guns')
            "identity": {"itemName": item_name, "type": equipment_type},
            "source": {},
            "stats_numerical": {},
            "stats_qualitative_visual": {},
            "derived_analysis": {},
            "metadata": {
                "lastUpdated": datetime.now().isoformat(),
                "dataCompleteness": "basic",
                "sources": []  # prefer URLs when available
            }
        }
        
        # Try multiple sources
        sources = [
            ("wiki", self.scrape_wiki),
            ("community", self.scrape_community_guides),
        ]
        
        for source_name, scrape_func in sources:
            try:
                data = scrape_func(item_name)
                if data:
                    # Merge dict sections
                    for key, value in data.items():
                        if key in item_data and isinstance(item_data[key], dict) and isinstance(value, dict):
                            item_data[key].update(value)
                    # Track source URL if provided
                    src_url = data.get("_source_url")
                    if src_url:
                        item_data["metadata"]["sources"].append(src_url)
                    else:
                        item_data["metadata"]["sources"].append(source_name)
                    logging.info(f"Successfully scraped {source_name} for {item_name}")
            except Exception as e:
                logging.error(f"Failed to scrape {source_name} for {item_name}: {e}")
                continue
        
        # Determine completeness
        if item_data["stats_numerical"] and item_data["derived_analysis"]:
            item_data["metadata"]["dataCompleteness"] = "complete"
        elif item_data["stats_numerical"]:
            item_data["metadata"]["dataCompleteness"] = "partial"
        
        return item_data
    
    def scrape_wiki(self, item_name):
        """Scrape from wiki sources"""
        # Implementation here (use self.session.get(url, timeout=self.request_timeout))
        # time.sleep(self.delay_seconds)
        return {}
    
    def scrape_community_guides(self, item_name):
        """Scrape from community guides"""
        # Implementation here (use self.session.get(url, timeout=self.request_timeout))
        # time.sleep(self.delay_seconds)
        return {}
    
    def save_item(self, item_data, equipment_type):
        """Save item to appropriate JSON file"""
        filepath = f'data/equipment/{equipment_type}.json'
        
        # Load existing data
        existing_data = load_json(filepath)
        
        # Find and update or append
        item_found = False
        for i, item in enumerate(existing_data):
            if item['identity']['itemName'] == item_data['identity']['itemName']:
                existing_data[i] = item_data
                item_found = True
                break
        
        if not item_found:
            existing_data.append(item_data)
        
        # Save
        save_json(existing_data, filepath)
        
        # Update progress
        status = item_data['metadata']['dataCompleteness']
        update_progress(item_data['identity']['itemName'], status)
        
        return status

# Example usage
if __name__ == "__main__":
    scraper = AzurLaneScraper()
    
    # Example: scrape a single item
    item_data = scraper.scrape_item("Twin 127mm (5\"/38 Mk 38)", "destroyer_guns")
    status = scraper.save_item(item_data, "destroyer_guns")
    
    # Commit after each item
    commit_changes(["Twin 127mm (5\"/38 Mk 38)"], status)
```

### 5. Initialize Progress Tracking

#### `progress.json`
```json
{
  "completed": [],
  "partial": [],
  "failed": [],
  "retry_queue": [],
  "last_updated": ""
}
```

### 6. First Commit
```bash
git add .
git commit -m "Initial repository structure for Azur Lane equipment database"
```

## Usage Workflow

### Starting a Scraping Session
```python
# In scripts/run_collection.py
from scraper import AzurLaneScraper
from utils import commit_changes

# Load list of items to process
items_to_process = [
    ("Twin 127mm (5\"/38 Mk 38)", "destroyer_guns"),
    ("Triple 152mm Main Gun", "light_cruiser_guns"),
    # ... more items
]

scraper = AzurLaneScraper()
batch = []
batch_status = []

for item_name, equipment_type in items_to_process:
    item_data = scraper.scrape_item(item_name, equipment_type)
    status = scraper.save_item(item_data, equipment_type)
    
    batch.append(item_name)
    batch_status.append(status)
    
    # Commit every 5 items
    if len(batch) >= 5:
        commit_changes(batch, "Mixed" if len(set(batch_status)) > 1 else batch_status[0])
        batch = []
        batch_status = []

# Commit remaining items
if batch:
    commit_changes(batch, "Mixed" if len(set(batch_status)) > 1 else batch_status[0])
```

## Source & Scraping Notes

- Respect the Azur Lane Wiki license and robots policy.
- License: CC BY-NC-SA; provide attribution when publishing data.
- robots.txt indicates a 1-second crawl delay; avoid `/w/` except allowed endpoints.
- Use timeouts and a small delay between requests to be polite.

## Key Principles

1. **Simple file structure** - JSON files grouped by equipment type
2. **Frequent commits** - Built into the utility functions
3. **Progress tracking** - Simple JSON file to track status
4. **No database** - Just JSON files in git
5. **Modular scripts** - Separate scraping, parsing, and utilities
6. **Error resilience** - Log errors but continue processing
7. **Polite scraping** - Timeouts + small delays between requests

## Next Steps

1. Run initial setup commands
2. Test with a single item
3. Expand scraper methods for different sources
4. Build item list to process
5. Run collection in batches

This keeps things simple while maintaining data integrity through version control.
