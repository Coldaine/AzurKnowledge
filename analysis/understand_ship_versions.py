import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Let's look at one ship's multiple versions
example_ship = "Laffey"
print(f"=== Example: {example_ship} Versions ===")
laffey_versions = []
for ship_id, ship_data in ships.items():
    if ship_data.get('name') == example_ship:
        laffey_versions.append({
            'id': ship_id,
            'star': ship_data.get('star', 0),
            'rarity': ship_data.get('rarity', 0),
            'attrs': ship_data.get('attrs', []),
            'base_list': ship_data.get('base_list', [])
        })

# Sort by ID to see progression
laffey_versions.sort(key=lambda x: x['id'])
for v in laffey_versions:
    hp = v['attrs'][0] if v['attrs'] else 0
    firepower = v['attrs'][1] if len(v['attrs']) > 1 else 0
    print(f"ID: {v['id']}, Star: {v['star']}, HP: {hp}, Firepower: {firepower}")

# Check if these are limit breaks
print("\n=== Understanding ID Pattern ===")
print("Last 2 digits likely represent:")
print("  x1: Base form (0 limit break)")
print("  x2: 1 star limit break")
print("  x3: 2 star limit break")
print("  x4: 3 star limit break (Max)")
print("  x9: Retrofit version")

# Count actual unique ships (base forms only - ending in x1)
base_ships = {}
for ship_id, ship_data in ships.items():
    if ship_id.endswith('1') and not ship_id.endswith('01'):  # x1 but not 01
        name = ship_data.get('name', 'Unknown')
        base_ships[name] = ship_id

print(f"\n=== Actual Ship Count ===")
print(f"Total database entries: {len(ships)}")
print(f"Unique ship names: {len(set(ship_data.get('name') for ship_data in ships.values()))}")
print(f"Base forms (x1 ending): {len(base_ships)}")

# Check retrofit ships (ending in x9)
retrofit_count = sum(1 for sid in ships if sid.endswith('9'))
print(f"Retrofit versions (x9 ending): {retrofit_count}")
