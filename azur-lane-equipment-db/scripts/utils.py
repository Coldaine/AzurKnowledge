import json
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, cast

def load_json(filepath):
    """Load JSON file, return empty list if not exists"""
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filepath):
    """Save data to JSON with pretty formatting"""
    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_progress(item_name: str, status: str) -> None:
    """Update progress tracking"""
    progress_file = 'progress.json'
    raw = load_json(progress_file)
    # Ensure we have a dict structure regardless of what's on disk
    progress: Dict[str, Any]
    if not isinstance(raw, dict) or not raw:
        progress = {}
    else:
        progress = cast(Dict[str, Any], raw)

    # Ensure required keys exist with sane defaults
    for key, default in (
        ("basic", []),
        ("completed", []),
        ("partial", []),
        ("failed", []),
        ("retry_queue", []),
        ("last_updated", ""),
    ):
        if key not in progress:
            progress[key] = default
    
    # Remove from other lists if exists
    for list_name in ['basic', 'completed', 'partial', 'failed']:
        current_list = progress.get(list_name, [])
        if isinstance(current_list, list) and item_name in current_list:
            current_list.remove(item_name)
        progress[list_name] = current_list
    
    # Add to appropriate list
    if status in ['basic', 'completed', 'partial', 'failed']:
        target_list = progress.get(status, [])
        if not isinstance(target_list, list):
            target_list = []
        target_list.append(item_name)
        progress[status] = target_list
    
    progress['last_updated'] = datetime.now().isoformat()
    save_json(progress, progress_file)

def commit_changes(item_names, status):
    """Create git commit with item names"""
    # Stage tracked data and progress files
    subprocess.run(['git', 'add', 'data/equipment', 'progress.json'], check=False)

    # Create commit message (limit item list for brevity)
    items = ', '.join(item_names[:3])
    if len(item_names) > 3:
        items += f' (+{len(item_names)-3} more)'
    message = f"Update: {items} - {status}"

    # Commit only if there are staged changes
    has_changes = subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode != 0
    if has_changes:
        subprocess.run(['git', 'commit', '-m', message], check=False)
    else:
        print('No staged changes to commit.')