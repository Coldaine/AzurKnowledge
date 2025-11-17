import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Count nationalities
nationality_counts = {}
for ship_id, ship_data in ships.items():
    nation = ship_data.get('nationality', 0)
    name = ship_data.get('name', 'Unknown')
    
    if nation not in nationality_counts:
        nationality_counts[nation] = {'count': 0, 'examples': []}
    
    nationality_counts[nation]['count'] += 1
    if len(nationality_counts[nation]['examples']) < 3:
        nationality_counts[nation]['examples'].append(name)

# Print nationality analysis
print("=== Nationality Analysis ===")
for nation, data in sorted(nationality_counts.items()):
    print(f"Nation {nation}: {data['count']} ships")
    print(f"  Examples: {', '.join(data['examples'])}")
