import json

with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/ship_data_statistics.json', 'r') as f:
    ships = json.load(f)

# Analyze different patterns for player vs NPC
player_nations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 96, 97, 98, 101, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113]
enemy_indicators = []
player_indicators = []

# Check nationality patterns
nation_99_count = 0
for ship_id, ship_data in ships.items():
    nation = ship_data.get('nationality', 0)
    name = ship_data.get('name', '')
    
    # Nationality 99 appears to be Sirens
    if nation == 99:
        nation_99_count += 1
        enemy_indicators.append(f"Nation 99: {name} (ID: {ship_id})")
    
    # Check for specific enemy-related names
    name_lower = name.lower()
    enemy_keywords = ['compiler', 'observer', 'purifier', 'tester', 'omitter', 'navigator']
    if any(keyword in name_lower for keyword in enemy_keywords):
        enemy_indicators.append(f"Enemy-like name: {name} (ID: {ship_id}, Nation: {nation})")

# Check ID ranges
id_900xxx_ships = []
for ship_id, ship_data in ships.items():
    ship_id_int = int(ship_id)
    if 900000 <= ship_id_int < 901000:
        id_900xxx_ships.append({
            'id': ship_id,
            'name': ship_data.get('name'),
            'nation': ship_data.get('nationality')
        })

print("=== Player vs NPC Analysis ===")
print(f"\nTotal ships: {len(ships)}")
print(f"Nation 99 (Siren) ships: {nation_99_count}")
print(f"\nEnemy indicators found:")
for indicator in enemy_indicators[:10]:  # Show first 10
    print(f"  - {indicator}")

print(f"\n=== Ships in 900xxx ID range (possible special/enemy ships) ===")
for ship in id_900xxx_ships[:10]:
    print(f"  ID: {ship['id']}, Name: {ship['name']}, Nation: {ship['nation']}")

# Check for collab ships (usually 10xxxxx range)
collab_count = sum(1 for sid in ships if int(sid) >= 10000000)
print(f"\nCollaboration ships (ID >= 10000000): {collab_count}")

# Check for META ships (Nation 97)
meta_count = sum(1 for s in ships.values() if s.get('nationality') == 97)
print(f"META ships (Nation 97): {meta_count}")

# Check for Bulins (Nation 98)
bulin_count = sum(1 for s in ships.values() if s.get('nationality') == 98)
print(f"Bulin ships (Nation 98): {bulin_count}")
