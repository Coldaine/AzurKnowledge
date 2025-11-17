import json

# Check equipment data
with open('/home/coldaine/Projects/AzurKnowledge/azur-lane-data/EN/sharecfgdata/equip_data_statistics.json', 'r') as f:
    equipment = json.load(f)

# Analyze equipment patterns
equip_by_nation = {}
for equip_id, equip_data in equipment.items():
    nation = equip_data.get('nationality', 0)
    name = equip_data.get('name', 'Unknown')
    
    if nation not in equip_by_nation:
        equip_by_nation[nation] = {'count': 0, 'examples': []}
    
    equip_by_nation[nation]['count'] += 1
    if len(equip_by_nation[nation]['examples']) < 3:
        equip_by_nation[nation]['examples'].append(f"{name} (ID: {equip_id})")

print("=== Equipment Nationality Distribution ===")
for nation, data in sorted(equip_by_nation.items()):
    print(f"Nation {nation}: {data['count']} equipment")
    if data['examples']:
        print(f"  Examples: {', '.join(data['examples'][:2])}")
