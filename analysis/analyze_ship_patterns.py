import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Analyze ID patterns
id_patterns = {}
for ship_id, ship_data in ships.items():
    ship_id_int = int(ship_id)
    prefix = ship_id_int // 100000  # Get the first digits
    
    if prefix not in id_patterns:
        id_patterns[prefix] = []
    
    id_patterns[prefix].append({
        'id': ship_id_int,
        'name': ship_data.get('name', 'Unknown'),
        'nationality': ship_data.get('nationality', 0),
        'type': ship_data.get('type', 0),
        'rarity': ship_data.get('rarity', 0)
    })

# Print pattern analysis
for prefix, ships_list in sorted(id_patterns.items()):
    print(f"\n=== ID Prefix: {prefix}xxxxx ===")
    print(f"Count: {len(ships_list)}")
    # Show first 3 examples
    for ship in ships_list[:3]:
        print(f"  ID: {ship['id']}, Name: {ship['name']}, Nation: {ship['nationality']}, Type: {ship['type']}, Rarity: {ship['rarity']}")
