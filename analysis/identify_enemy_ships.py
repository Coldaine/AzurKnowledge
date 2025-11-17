import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Look for enemy patterns
enemy_ships = []
player_ships = []
special_900_ships = []

for ship_id, ship_data in ships.items():
    name = ship_data.get('name', 'Unknown')
    nation = ship_data.get('nationality', 0)
    ship_id_int = int(ship_id)
    
    # Check 900xxx range more carefully
    if 900000 <= ship_id_int < 901000:
        hp = ship_data.get('attrs', [0])[0] if ship_data.get('attrs') else 0
        special_900_ships.append({
            'id': ship_id,
            'name': name,
            'nation': nation,
            'hp': hp,
            'star': ship_data.get('star', 0)
        })

# Sort and analyze 900xxx ships
special_900_ships.sort(key=lambda x: int(x['id']))

print("=== Analyzing 900xxx Range Ships ===")
print("These might be enemy or special event ships:")
print("\nHigh HP ships (potential enemies):")
for ship in special_900_ships:
    if ship['hp'] > 50000:  # Abnormally high HP
        print(f"  ID: {ship['id']}, Name: {ship['name']}, HP: {ship['hp']:,}, Nation: {ship['nation']}")

print("\nLow ID 900xxx ships (first 10):")
for ship in special_900_ships[:10]:
    print(f"  ID: {ship['id']}, Name: {ship['name']}, HP: {ship['hp']}, Nation: {ship['nation']}")

# Check for ships with no limit break versions (only one entry)
single_entry_ships = {}
for ship_id, ship_data in ships.items():
    name = ship_data.get('name', 'Unknown')
    if name not in single_entry_ships:
        single_entry_ships[name] = []
    single_entry_ships[name].append(ship_id)

print("\n=== Ships with Only One Entry (Potential NPCs) ===")
count = 0
for name, ids in single_entry_ships.items():
    if len(ids) == 1:
        ship_data = ships[ids[0]]
        nation = ship_data.get('nationality', 0)
        hp = ship_data.get('attrs', [0])[0] if ship_data.get('attrs') else 0
        if hp > 100000 or nation == 99:  # Very high HP or Siren nation
            count += 1
            print(f"  {name} (ID: {ids[0]}, Nation: {nation}, HP: {hp:,})")

print(f"\nTotal single-entry ships with suspicious stats: {count}")
