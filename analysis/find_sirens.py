import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Find all nationality 99 ships (likely Sirens/enemies)
siren_ships = []
for ship_id, ship_data in ships.items():
    if ship_data.get('nationality') == 99:
        siren_ships.append({
            'id': ship_id,
            'name': ship_data.get('name', 'Unknown'),
            'type': ship_data.get('type', 0)
        })

print("=== Nationality 99 Ships (Likely Sirens/Enemies) ===")
for ship in siren_ships:
    print(f"ID: {ship['id']}, Name: {ship['name']}, Type: {ship['type']}")

# Also check for ships with suspicious names
print("\n=== Ships with 'Siren' or 'Test' Related Names ===")
for ship_id, ship_data in ships.items():
    name = ship_data.get('name', '').lower()
    if 'siren' in name or 'test' in name or 'compiler' in name or 'observer' in name or 'purifier' in name:
        print(f"ID: {ship_id}, Name: {ship_data.get('name')}, Nation: {ship_data.get('nationality')}")
