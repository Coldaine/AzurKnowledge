# Azur Lane Player vs NPC Data Separation Plan

## Executive Summary
After analyzing the AzurLaneData repository structure and content, I've identified clear patterns to separate player-controlled ships, weapons, and skills from NPC enemies. The database contains 3,664 total entries representing:
- **872 unique ship names** (actual distinct ships)
- **~766 base player ships** (ending in x1)
- Multiple entries per ship for limit break states (x1, x2, x3, x4) and retrofits (x9)
- **900xxx range contains enemy/boss versions** with massively inflated HP (100,000-1,300,000 HP)

## Key Findings

### 1. Database Structure Understanding

#### Ship Entry System
Each player ship has multiple database entries:
- **xxxxx1**: Base form (0 limit break)
- **xxxxx2**: 1-star limit break
- **xxxxx3**: 2-star limit break  
- **xxxxx4**: 3-star limit break (Max)
- **xxxxx9**: Retrofit version (if available)

Example: Laffey has 8 entries:
- 101171-101174: Normal progression
- 900xxx entries: Enemy/boss versions with inflated stats

### 2. Ship Identification Patterns

#### Player Ships
- **Nationalities**: 1-11, 96-98, 101-113
  - Nation 1: Eagle Union (684 ships)
  - Nation 2: Royal Navy (575 ships)  
  - Nation 3: Sakura Empire (692 ships)
  - Nation 4: Iron Blood (429 ships)
  - Nation 5: Dragon Empery (140 ships)
  - Nation 6: Sardegna Empire (147 ships)
  - Nation 7: Northern Parliament (153 ships)
  - Nation 8: Iris Libre (122 ships)
  - Nation 9: Vichya Dominion (103 ships)
  - Nation 11: Netherland (15 ships)
  - Nation 96: Tempesta/Pirates (54 ships)
  - Nation 97: META ships (216 ships)
  - Nation 98: Bulins/Universal (28 ships)
  - Nations 101-113: Collaboration ships (276 total)

#### NPC/Enemy Ships
- **Nationality 99**: Siren faction (1 entry: Compiler)
- **900xxx Range with HP > 100,000**: Enemy/boss versions of player ships
  - Examples: Ayanami (900040) with 142,758 HP vs normal 319-786 HP
  - Boss battleships: 1,200,000+ HP
  - Boss carriers: 1,100,000+ HP
- **Identification**: Same ship name but massively inflated stats

### 2. ID Range Patterns

#### Player Ship ID Ranges:
- 1xxxxx: Universal/Special (628 ships)
- 2xxxxx: Royal Navy (487 ships)
- 3xxxxx: Sakura Empire (627 ships)
- 4xxxxx: Iron Blood (365 ships)
- 5xxxxx: Dragon Empery (107 ships)
- 6xxxxx: Sardegna (136 ships)
- 7xxxxx: Northern Parliament (137 ships)
- 8xxxxx: Iris/Vichya (108 ships)
- 900xxx: Special player ships (537 ships)
- 96xxxxx: Tempesta (44 ships)
- 97xxxxx: META variants (200 ships)
- 10xxxxxx+: Collaboration ships (276 ships)

### 3. Equipment Patterns

#### Player Equipment (99.9% of data)
- **Nationality 0**: Universal equipment (9,041 items - 90.6%)
- **Nationalities 1-11, 96, 104-106**: Faction-specific equipment (927 items)

#### NPC Equipment
- No distinct NPC-only equipment found in the dataset
- Enemy ships likely use player equipment or have stats defined elsewhere

## Separation Strategy

### Phase 1: Immediate Filtering
```python
def is_player_ship(ship_id, ship_data):
    # Exclude nationality 99 (Sirens)
    if ship_data.get('nationality') == 99:
        return False
    
    # Exclude enemy boss versions (900xxx with extreme HP)
    ship_id_int = int(ship_id)
    if 900000 <= ship_id_int < 901000:
        hp = ship_data.get('attrs', [0])[0] if ship_data.get('attrs') else 0
        if hp > 50000:  # Boss versions have 100k-1.3M HP
            return False
    
    return True

def is_player_equipment(equip_data):
    # All equipment in the dataset appears to be player-usable
    return True

def get_base_player_ships(all_ships):
    # Get only base forms (ending in x1) to avoid duplicates
    base_ships = {}
    for ship_id, ship_data in all_ships.items():
        if is_player_ship(ship_id, ship_data):
            # Check if it's a base form
            if ship_id.endswith('1') and not ship_id.endswith('01'):
                base_ships[ship_id] = ship_data
    return base_ships
```

### Phase 2: Data Validation
1. **Ships**: 
   - Filter out nationality 99 (Sirens)
   - Filter out 900xxx range with HP > 50,000 (enemy bosses)
   - Include all limit break states or just base forms depending on use case
2. **Equipment**: Include all (no NPC-specific equipment found)
3. **Weapons**: Include all weapon_property.json entries referenced by player equipment

### Phase 3: Implementation Plan

#### Step 1: Update Parser Script
- Add `is_player` flag to data models
- Implement filtering logic based on nationality
- Create separate output files for player-only data

#### Step 2: Data Extraction
```python
# Filter player ships
player_ships = {
    ship_id: ship_data 
    for ship_id, ship_data in all_ships.items()
    if ship_data.get('nationality') != 99
}

# All equipment is player-usable
player_equipment = all_equipment

# Weapons referenced by player equipment
player_weapon_ids = set()
for equip in player_equipment.values():
    if 'weapon_id' in equip:
        player_weapon_ids.update(equip['weapon_id'])
```

#### Step 3: Output Structure
```
azur_lane_player_data/
├── ships_player_base.csv      # ~766 unique player ships (base forms only)
├── ships_player_all.csv       # ~3,500 player ship entries (all limit breaks)
├── equipment_player.csv       # 9,968 player equipment
├── weapons_player.csv         # Player-referenced weapons
├── ships_by_faction.json      # Organized by nationality
├── equipment_by_type.json     # Organized by equipment type
└── player_summary.json        # Statistics for player content only
```

## Skills Data Strategy

### Current Status
- No skills data found in current `sharecfgdata/` directory
- Likely stored in separate files or different format

### Investigation Plan
1. Search for skill-related JSON files
2. Check for skill references in ship data
3. Look for buff/ability templates
4. Parse skill descriptions from game text files

## Edge Cases & Considerations

### 1. Special Ships
- "Observer zero" (ID: 900136) has nationality 1 but enemy-like name
  - **Decision**: Include as player ship (follows nationality rule)

### 2. Missing Enemy Data
- Only 1-2 enemy ships found in dataset
- Actual enemy formations likely defined elsewhere:
  - chapter_template.json references
  - expedition_data_template.json formations
  - Separate enemy database not included in this repository

### 3. Future-Proofing
- Monitor for new nationalities > 113 (potential enemies)
- Check for new fields like `is_enemy` or `is_npc`
- Watch for ID patterns outside current ranges

## Implementation Priority

### High Priority (Immediate)
1. ✅ Filter ships by nationality (!= 99)
2. ✅ Include all equipment data
3. ✅ Extract player-referenced weapons

### Medium Priority (Next Steps)
1. ⏳ Find and parse skill data
2. ⏳ Map skills to player ships
3. ⏳ Create faction-specific exports

### Low Priority (Future)
1. ⏳ Investigate missing enemy data sources
2. ⏳ Add validation for edge cases
3. ⏳ Create data relationship diagrams

## Conclusion

The AzurLaneData repository contains a complex database structure where:
- **3,664 total entries** represent **~872 unique ships** with multiple states
- **~766 actual playable base ships** when filtering to unique entries
- **900xxx range contains enemy boss versions** with inflated HP (100k-1.3M)

Separation strategy:
- **Ships**: 
  - Exclude nationality 99 (Sirens)
  - Exclude 900xxx entries with HP > 50,000 (boss versions)
  - Choose between base forms only (~766) or all states (~3,500)
- **Equipment**: Include all (100% player-usable)
- **Weapons**: Include all referenced by equipment
- **Skills**: Require further investigation to locate data

This corrected understanding shows the database includes both player ships (with their progression states) and enemy boss versions, not just player content as initially thought.