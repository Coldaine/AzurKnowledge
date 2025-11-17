import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Group ships by name to find duplicates
ships_by_name = {}
for ship_id, ship_data in ships.items():
    name = ship_data.get('name', 'Unknown')
    if name not in ships_by_name:
        ships_by_name[name] = []
    ships_by_name[name].append({
        'id': ship_id,
        'star': ship_data.get('star', 0),
        'rarity': ship_data.get('rarity', 0)
    })

# Find ships with multiple entries
print("=== Ships with Multiple Entries ===")
multi_entry_count = 0
for name, entries in ships_by_name.items():
    if len(entries) > 1:
        multi_entry_count += 1
        if multi_entry_count <= 5:  # Show first 5 examples
            print(f"\n{name}: {len(entries)} entries")
            for entry in entries[:4]:  # Show first 4 IDs
                print(f"  ID: {entry['id']}, Star: {entry['star']}, Rarity: {entry['rarity']}")

print(f"\n=== Summary ===")
print(f"Total ship entries: {len(ships)}")
print(f"Unique ship names: {len(ships_by_name)}")
print(f"Ships with multiple entries: {multi_entry_count}")

# Check ID pattern - last 2 digits often indicate retrofit/kai states
print("\n=== ID Pattern Analysis ===")
id_endings = {}
for ship_id in ships.keys():
    ending = ship_id[-2:]  # Last 2 digits
    if ending not in id_endings:
        id_endings[ending] = 0
    id_endings[ending] += 1

print("Most common ID endings (likely indicating ship states):")
for ending, count in sorted(id_endings.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  ...{ending}: {count} ships")
