#!/usr/bin/env python3
"""
Azur Lane Data Parser and Analyzer
Extracts and organizes numerical data from AzurLaneData repository
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import csv

@dataclass
class Equipment:
    """Equipment data model"""
    id: int
    name: str
    type: int
    type_name: str = ""
    rarity: int = 0
    nationality: int = 0
    tech: int = 0
    damage: List[float] = field(default_factory=list)
    reload: List[float] = field(default_factory=list)
    armor_modifiers: List[float] = field(default_factory=list)
    ammo_type: int = 0
    weapon_ids: List[int] = field(default_factory=list)
    equip_parameters: Dict = field(default_factory=dict)
    property_rate: List[float] = field(default_factory=list)
    value_2: int = 0
    value_3: int = 0
    description: str = ""
    speciality: str = ""
    part_main: List[int] = field(default_factory=list)
    part_sub: List[int] = field(default_factory=list)

@dataclass
class Ship:
    """Ship data model"""
    id: int
    name: str
    english_name: str = ""
    type: int = 0
    type_name: str = ""
    nationality: int = 0
    rarity: int = 0
    star: int = 0
    armor_type: int = 0
    
    # Base stats (index mapping from attrs array)
    hp: int = 0
    firepower: int = 0
    torpedo: int = 0
    antiair: int = 0
    aviation: int = 0
    reload: int = 0
    armor: int = 0
    hit: int = 0
    evasion: int = 0
    speed: int = 0
    luck: int = 0
    antisub: int = 0
    
    # Growth rates
    hp_growth: int = 0
    firepower_growth: int = 0
    torpedo_growth: int = 0
    antiair_growth: int = 0
    aviation_growth: int = 0
    reload_growth: int = 0
    armor_growth: int = 0
    hit_growth: int = 0
    evasion_growth: int = 0
    antisub_growth: int = 0
    
    # Equipment slots
    equipment_proficiency: List[float] = field(default_factory=list)
    base_list: List[int] = field(default_factory=list)
    preload_count: List[int] = field(default_factory=list)

@dataclass
class Weapon:
    """Weapon data model"""
    id: int
    name: str = ""
    damage: int = 0
    reload_max: int = 0
    bullet_id: int = 0
    barrage_id: int = 0
    spawn_bound: str = ""
    fire_fx: str = ""
    type: int = 0
    range: int = 0
    angle: int = 0
    min_range: int = 0
    aim_type: int = 0

class AzurLaneDataParser:
    """Main parser class for Azur Lane data"""
    
    # Equipment type mapping
    EQUIP_TYPES = {
        1: "DD Gun",
        2: "CL Gun", 
        3: "CA Gun",
        4: "BB Gun",
        5: "Torpedo",
        6: "AA Gun",
        7: "Fighter",
        8: "Torpedo Bomber",
        9: "Dive Bomber",
        10: "Auxiliary",
        11: "CB Gun",
        12: "Seaplane",
        13: "Submarine Torpedo",
        14: "Depth Charge",
        15: "Anti-Submarine Aircraft",
        17: "Helicopter",
        18: "Goods"
    }
    
    # Ship type mapping
    SHIP_TYPES = {
        1: "Destroyer",
        2: "Light Cruiser",
        3: "Heavy Cruiser",
        4: "Battlecruiser",
        5: "Battleship",
        6: "Light Carrier",
        7: "Aircraft Carrier",
        8: "Submarine",
        9: "Aviation Cruiser",
        10: "Aviation Battleship",
        11: "Torpedo Cruiser",
        12: "Repair Ship",
        13: "Monitor",
        17: "Submarine Carrier",
        18: "Large Cruiser",
        19: "Munition Ship",
        20: "Missile Destroyer",
        21: "Missile Cruiser",
        22: "Frigate"
    }
    
    # Nationality mapping
    NATIONS = {
        0: "Universal",
        1: "Eagle Union",
        2: "Royal Navy",
        3: "Sakura Empire",
        4: "Iron Blood",
        5: "Dragon Empery",
        6: "Sardegna Empire",
        7: "Northern Parliament",
        8: "Iris Libre",
        9: "Vichya Dominion",
        10: "Iris Orthodoxy",
        11: "Tempesta",
        12: "META",
        13: "Unknown"
    }
    
    # Rarity mapping
    RARITIES = {
        1: "Common",
        2: "Rare", 
        3: "Elite",
        4: "Super Rare",
        5: "Ultra Rare",
        6: "Decisive"
    }
    
    def __init__(self, data_path: str = "azur-lane-data/EN/sharecfgdata"):
        self.data_path = Path(data_path)
        self.equipment = {}
        self.ships = {}
        self.weapons = {}
        self.weapon_names = {}
        self.bullets = {}
        self.barrages = {}
        self.ship_templates = {}
        self.equip_templates = {}
        
    def load_json(self, filename: str) -> Dict:
        """Load JSON file from data directory"""
        filepath = self.data_path / filename
        try:
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: {filename} not found")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {filename}: {e}")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
        return {}
    
    def parse_equipment(self):
        """Parse equipment data from JSON files"""
        print("Parsing equipment data...")
        
        # Load equipment statistics
        equip_stats = self.load_json("equip_data_statistics.json")
        equip_templates = self.load_json("equip_data_template.json")
        
        # Merge template and statistics data
        for equip_id, data in equip_stats.items():
            try:
                equip = Equipment(
                    id=int(equip_id),
                    name=data.get('name', 'Unknown'),
                    type=data.get('type', 0),
                    type_name=self.EQUIP_TYPES.get(data.get('type', 0), 'Unknown'),
                    rarity=data.get('rarity', 1),
                    nationality=data.get('nationality', 0),
                    tech=data.get('tech', 0),
                    weapon_ids=data.get('weapon_id', []),
                    ammo_type=data.get('ammo', 0),
                    value_2=data.get('value_2', 0),
                    value_3=data.get('value_3', 0),
                    description=data.get('descrip', ''),
                    speciality=data.get('speciality', ''),
                    part_main=data.get('part_main', []),
                    part_sub=data.get('part_sub', []),
                    property_rate=data.get('property_rate', []),
                    equip_parameters=data.get('equip_parameters', {})
                )
                
                # Get additional data from template if available
                if equip_id in equip_templates:
                    template = equip_templates[equip_id]
                    equip.damage = template.get('damage', [])
                    equip.reload = template.get('reload', [])
                    equip.armor_modifiers = template.get('armor_modifiers', [])
                
                self.equipment[int(equip_id)] = equip
                
            except Exception as e:
                print(f"Error parsing equipment {equip_id}: {e}")
        
        print(f"Parsed {len(self.equipment)} equipment items")
    
    def parse_ships(self):
        """Parse ship data from JSON files"""
        print("Parsing ship data...")
        
        ship_stats = self.load_json("ship_data_statistics.json")
        ship_templates = self.load_json("ship_data_template.json")
        
        for ship_id, data in ship_stats.items():
            try:
                # Extract base stats from attrs array
                attrs = data.get('attrs', [0] * 12)
                attrs_growth = data.get('attrs_growth', [0] * 12)
                
                ship = Ship(
                    id=int(ship_id),
                    name=data.get('name', 'Unknown'),
                    english_name=data.get('english_name', ''),
                    type=data.get('type', 0),
                    type_name=self.SHIP_TYPES.get(data.get('type', 0), 'Unknown'),
                    nationality=data.get('nationality', 0),
                    rarity=data.get('rarity', 1),
                    star=data.get('star', 1),
                    armor_type=data.get('armor_type', 1),
                    
                    # Base stats
                    hp=attrs[0] if len(attrs) > 0 else 0,
                    firepower=attrs[1] if len(attrs) > 1 else 0,
                    torpedo=attrs[2] if len(attrs) > 2 else 0,
                    antiair=attrs[3] if len(attrs) > 3 else 0,
                    aviation=attrs[4] if len(attrs) > 4 else 0,
                    reload=attrs[5] if len(attrs) > 5 else 0,
                    armor=attrs[6] if len(attrs) > 6 else 0,
                    hit=attrs[7] if len(attrs) > 7 else 0,
                    evasion=attrs[8] if len(attrs) > 8 else 0,
                    speed=attrs[9] if len(attrs) > 9 else 0,
                    luck=attrs[10] if len(attrs) > 10 else 0,
                    antisub=attrs[11] if len(attrs) > 11 else 0,
                    
                    # Growth rates
                    hp_growth=attrs_growth[0] if len(attrs_growth) > 0 else 0,
                    firepower_growth=attrs_growth[1] if len(attrs_growth) > 1 else 0,
                    torpedo_growth=attrs_growth[2] if len(attrs_growth) > 2 else 0,
                    antiair_growth=attrs_growth[3] if len(attrs_growth) > 3 else 0,
                    aviation_growth=attrs_growth[4] if len(attrs_growth) > 4 else 0,
                    reload_growth=attrs_growth[5] if len(attrs_growth) > 5 else 0,
                    armor_growth=attrs_growth[6] if len(attrs_growth) > 6 else 0,
                    hit_growth=attrs_growth[7] if len(attrs_growth) > 7 else 0,
                    evasion_growth=attrs_growth[8] if len(attrs_growth) > 8 else 0,
                    antisub_growth=attrs_growth[11] if len(attrs_growth) > 11 else 0,
                    
                    # Equipment data
                    equipment_proficiency=data.get('equipment_proficiency', []),
                    base_list=data.get('base_list', []),
                    preload_count=data.get('preload_count', [])
                )
                
                self.ships[int(ship_id)] = ship
                
            except Exception as e:
                print(f"Error parsing ship {ship_id}: {e}")
        
        print(f"Parsed {len(self.ships)} ships")
    
    def parse_weapons(self):
        """Parse weapon data"""
        print("Parsing weapon data...")
        
        # Load weapon names
        weapon_names = self.load_json("weapon_name.json")
        self.weapon_names = {int(k): v for k, v in weapon_names.items() if k.isdigit()}
        
        # Try to load weapon_property first (preferred), fallback to bullet_template
        weapon_data = self.load_json("weapon_property.json")
        if not weapon_data:
            print("  weapon_property.json not found, using bullet_template.json")
            weapon_data = self.load_json("bullet_template.json")
        
        for weapon_id, data in weapon_data.items():
            try:
                weapon = Weapon(
                    id=int(weapon_id),
                    name=self.weapon_names.get(int(weapon_id), ''),
                    damage=data.get('damage', 0),
                    reload_max=data.get('reload_max', 0),
                    bullet_id=data.get('bullet_ID', 0),
                    barrage_id=data.get('barrage_ID', 0),
                    spawn_bound=data.get('spawn_bound', ''),
                    fire_fx=data.get('fire_fx', ''),
                    type=data.get('type', 0),
                    range=data.get('range', 0),
                    angle=data.get('angle', 0),
                    min_range=data.get('min_range', 0),
                    aim_type=data.get('aim_type', 0)
                )
                self.weapons[int(weapon_id)] = weapon
                
            except Exception as e:
                print(f"Error parsing weapon {weapon_id}: {e}")
        
        print(f"Parsed {len(self.weapons)} weapons")
    
    def analyze_equipment_stats(self):
        """Analyze and summarize equipment statistics"""
        print("\n" + "="*60)
        print("EQUIPMENT ANALYSIS")
        print("="*60)
        
        # Group by type
        equip_by_type = defaultdict(list)
        for equip in self.equipment.values():
            equip_by_type[equip.type_name].append(equip)
        
        # Sort and display top equipment by type
        for type_name, items in sorted(equip_by_type.items()):
            print(f"\n{type_name} ({len(items)} items)")
            print("-" * 40)
            
            # Sort by rarity and tech level
            sorted_items = sorted(items, key=lambda x: (x.rarity, x.tech), reverse=True)[:5]
            
            for item in sorted_items:
                rarity_name = self.RARITIES.get(item.rarity, 'Unknown')
                nation_name = self.NATIONS.get(item.nationality, 'Unknown')
                print(f"  [{rarity_name}] {item.name}")
                print(f"    Nation: {nation_name}, Tech: T{item.tech}")
                if item.weapon_ids:
                    weapon_id = item.weapon_ids[0] if item.weapon_ids else 0
                    if weapon_id in self.weapons:
                        weapon = self.weapons[weapon_id]
                        print(f"    Damage: {weapon.damage}, Range: {weapon.range}")
    
    def analyze_ship_stats(self):
        """Analyze and summarize ship statistics"""
        print("\n" + "="*60)
        print("SHIP ANALYSIS")
        print("="*60)
        
        # Group by type
        ships_by_type = defaultdict(list)
        for ship in self.ships.values():
            ships_by_type[ship.type_name].append(ship)
        
        # Display statistics by ship type
        for type_name, ships in sorted(ships_by_type.items()):
            print(f"\n{type_name} ({len(ships)} ships)")
            print("-" * 40)
            
            # Calculate average stats
            if ships:
                avg_hp = sum(s.hp for s in ships) / len(ships)
                avg_fp = sum(s.firepower for s in ships) / len(ships)
                avg_torp = sum(s.torpedo for s in ships) / len(ships)
                avg_aa = sum(s.antiair for s in ships) / len(ships)
                
                print(f"  Average Stats:")
                print(f"    HP: {avg_hp:.0f}")
                print(f"    Firepower: {avg_fp:.0f}")
                print(f"    Torpedo: {avg_torp:.0f}")
                print(f"    Anti-Air: {avg_aa:.0f}")
                
                # Top ships by rarity
                top_ships = sorted(ships, key=lambda x: (x.rarity, x.hp), reverse=True)[:3]
                print(f"  Top Ships:")
                for ship in top_ships:
                    rarity_name = self.RARITIES.get(ship.rarity, 'Unknown')
                    nation_name = self.NATIONS.get(ship.nationality, 'Unknown')
                    print(f"    [{rarity_name}] {ship.name} ({nation_name})")
                    print(f"      HP:{ship.hp} FP:{ship.firepower} TRP:{ship.torpedo} AA:{ship.antiair}")
    
    def sanitize_csv_field(self, value: str) -> str:
        """Sanitize CSV field to prevent injection attacks"""
        if isinstance(value, str) and value:
            if value[0] in ('=', '+', '-', '@', '\t', '\r'):
                return "'" + value
        return str(value)
    
    def export_to_csv(self, output_dir: str = "azur_lane_parsed_data"):
        """Export parsed data to CSV files"""
        print(f"\nExporting data to {output_dir}/...")
        try:
            os.makedirs(output_dir, exist_ok=True)
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return
        
        # Export equipment data
        equip_file = os.path.join(output_dir, "equipment.csv")
        with open(equip_file, 'w', newline='', encoding='utf-8') as f:
            if self.equipment:
                fieldnames = ['id', 'name', 'type_name', 'rarity', 'nationality', 'tech', 
                             'weapon_ids', 'description', 'speciality']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for equip in sorted(self.equipment.values(), key=lambda x: (x.type, x.rarity, x.tech)):
                    row = {
                        'id': equip.id,
                        'name': self.sanitize_csv_field(equip.name),
                        'type_name': equip.type_name,
                        'rarity': self.RARITIES.get(equip.rarity, 'Unknown'),
                        'nationality': self.NATIONS.get(equip.nationality, 'Unknown'),
                        'tech': equip.tech,
                        'weapon_ids': ','.join(map(str, equip.weapon_ids)),
                        'description': self.sanitize_csv_field(equip.description),
                        'speciality': self.sanitize_csv_field(equip.speciality)
                    }
                    writer.writerow(row)
        print(f"  Exported {len(self.equipment)} equipment items to equipment.csv")
        
        # Export ship data
        ship_file = os.path.join(output_dir, "ships.csv")
        with open(ship_file, 'w', newline='', encoding='utf-8') as f:
            if self.ships:
                fieldnames = ['id', 'name', 'english_name', 'type_name', 'rarity', 'nationality',
                             'hp', 'firepower', 'torpedo', 'antiair', 'aviation', 'reload',
                             'armor', 'hit', 'evasion', 'speed', 'luck', 'antisub']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for ship in sorted(self.ships.values(), key=lambda x: (x.type, x.rarity, x.id)):
                    row = {
                        'id': ship.id,
                        'name': self.sanitize_csv_field(ship.name),
                        'english_name': self.sanitize_csv_field(ship.english_name),
                        'type_name': ship.type_name,
                        'rarity': self.RARITIES.get(ship.rarity, 'Unknown'),
                        'nationality': self.NATIONS.get(ship.nationality, 'Unknown'),
                        'hp': ship.hp,
                        'firepower': ship.firepower,
                        'torpedo': ship.torpedo,
                        'antiair': ship.antiair,
                        'aviation': ship.aviation,
                        'reload': ship.reload,
                        'armor': ship.armor,
                        'hit': ship.hit,
                        'evasion': ship.evasion,
                        'speed': ship.speed,
                        'luck': ship.luck,
                        'antisub': ship.antisub
                    }
                    writer.writerow(row)
        print(f"  Exported {len(self.ships)} ships to ships.csv")
        
        # Export weapon data
        weapon_file = os.path.join(output_dir, "weapons.csv")
        with open(weapon_file, 'w', newline='', encoding='utf-8') as f:
            if self.weapons:
                fieldnames = ['id', 'name', 'damage', 'reload_max', 'range', 'angle', 'type']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for weapon in sorted(self.weapons.values(), key=lambda x: x.id):
                    row = {
                        'id': weapon.id,
                        'name': self.sanitize_csv_field(weapon.name or f"Weapon_{weapon.id}"),
                        'damage': weapon.damage,
                        'reload_max': weapon.reload_max,
                        'range': weapon.range,
                        'angle': weapon.angle,
                        'type': weapon.type
                    }
                    writer.writerow(row)
        print(f"  Exported {len(self.weapons)} weapons to weapons.csv")
    
    def export_to_json(self, output_dir: str = "azur_lane_parsed_data"):
        """Export parsed data to organized JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export equipment by type
        equip_by_type = defaultdict(list)
        for equip in self.equipment.values():
            equip_dict = asdict(equip)
            equip_dict['rarity_name'] = self.RARITIES.get(equip.rarity, 'Unknown')
            equip_dict['nation_name'] = self.NATIONS.get(equip.nationality, 'Unknown')
            equip_by_type[equip.type_name].append(equip_dict)
        
        equip_json_file = os.path.join(output_dir, "equipment_by_type.json")
        with open(equip_json_file, 'w', encoding='utf-8') as f:
            json.dump(equip_by_type, f, indent=2, ensure_ascii=False)
        print(f"  Exported equipment to equipment_by_type.json")
        
        # Export ships by type
        ships_by_type = defaultdict(list)
        for ship in self.ships.values():
            ship_dict = asdict(ship)
            ship_dict['rarity_name'] = self.RARITIES.get(ship.rarity, 'Unknown')
            ship_dict['nation_name'] = self.NATIONS.get(ship.nationality, 'Unknown')
            ships_by_type[ship.type_name].append(ship_dict)
        
        ships_json_file = os.path.join(output_dir, "ships_by_type.json")
        with open(ships_json_file, 'w', encoding='utf-8') as f:
            json.dump(ships_by_type, f, indent=2, ensure_ascii=False)
        print(f"  Exported ships to ships_by_type.json")
        
        # Export summary statistics
        summary = {
            'total_equipment': len(self.equipment),
            'total_ships': len(self.ships),
            'total_weapons': len(self.weapons),
            'equipment_types': list(equip_by_type.keys()),
            'ship_types': list(ships_by_type.keys()),
            'nationalities': list(self.NATIONS.values()),
            'rarities': list(self.RARITIES.values())
        }
        
        summary_file = os.path.join(output_dir, "summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"  Exported summary to summary.json")
    
    def run(self):
        """Main execution method"""
        print("Starting Azur Lane Data Parser...")
        print("="*60)
        
        # Parse all data
        self.parse_weapons()
        self.parse_equipment()
        self.parse_ships()
        
        # Analyze data
        self.analyze_equipment_stats()
        self.analyze_ship_stats()
        
        # Export data
        self.export_to_csv()
        self.export_to_json()
        
        print("\n" + "="*60)
        print("Parsing complete!")
        print(f"Total items parsed:")
        print(f"  - Equipment: {len(self.equipment)}")
        print(f"  - Ships: {len(self.ships)}")
        print(f"  - Weapons: {len(self.weapons)}")
        print("="*60)


if __name__ == "__main__":
    parser = AzurLaneDataParser()
    parser.run()