# Author: Erik van Gorsel
# Mendix Universal Userlib Cleanup
#
# Supported Mendix Studio Pro LTS Versions:
# 10.24 LTS: 10.24.13, 10.24.12, 10.24.11, 10.24.10, 10.24.9, 10.24.8, 10.24.6, 
#            10.24.5, 10.24.4, 10.24.3, 10.24.2, 10.24.1, 10.24.0
#  9.24 LTS: 9.24.40, 9.24.39, 9.24.38, 9.24.37, 9.24.36, 9.24.35, 9.24.34
#  8.18 LTS: 8.18.35, 8.18.34
#  7.23 LTS: All 7.23.x versions
import os
import re
import sys
import sqlite3
import json

# --- Path Resolution & Module Loading ---
# Detect if running as a PyInstaller frozen EXE
if hasattr(sys, '_MEIPASS'):
    RESOURCE_DIR = sys._MEIPASS
    ENGINES_PATH = os.path.join(RESOURCE_DIR, "src", "engines")
    CORE_PATH = os.path.join(RESOURCE_DIR, "src", "core")
else:
    # Running from source (internal/src/core/manager.py)
    CORE_PATH = os.path.dirname(os.path.abspath(__file__))
    # Go up 2 levels from internal/src/core/ to get to internal/
    RESOURCE_DIR = os.path.abspath(os.path.join(CORE_PATH, "..", ".."))
    ENGINES_PATH = os.path.join(RESOURCE_DIR, "src", "engines")

# Ensure critical directories are in sys.path for direct imports
for path in [ENGINES_PATH, CORE_PATH]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# Import Utilities and Engines
import utils
import clean_userlib_mx11
import clean_userlib_mx10
import clean_userlib_mx9
import clean_userlib_mx8
import clean_userlib_mx7

def get_mendix_version(project_root):
    """
    Extracts Mendix version using prioritized sources:
    1. .mpr metadata (Primary)
    2. settings.json (Fallback)
    """
    # Source 1: .mpr (SQLite)
    mpr_files = [f for f in os.listdir(project_root) if f.endswith('.mpr') and not f.endswith('.bak')]
    if mpr_files:
        mpr_path = os.path.join(project_root, mpr_files[0])
        try:
            conn = sqlite3.connect(f"file:{mpr_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM _MetaData LIMIT 1")
            row = cursor.fetchone()
            if row:
                v = row[0] if re.match(r'^\d+\.', str(row[0])) else row[1]
                conn.close()
                return str(v)
            conn.close()
        except:
            pass

    # Source 2: settings.json
    settings_path = os.path.join(project_root, 'settings.json')
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                data = json.load(f)
                return data.get('MendixVersion') or data.get('modelerVersion')
        except:
            pass
            
    return None

def normalize_version(v):
    """Strips suffixes like LTS, MTS and trims whitespace."""
    if not v: return None
    # Remove common suffixes and build numbers
    v = re.sub(r'[\s\-]+(LTS|MTS|MTSLatest|Patch).*$', '', str(v), flags=re.IGNORECASE)
    # Ensure it only contains digits and dots for semantic parsing
    match = re.search(r'(\d+\.\d+(\.\d+)?)', v)
    return match.group(1) if match else v.strip()

def parse_mx_versions(file_path):
    """
    Intelligently parses MxVersions.txt.
    Supports ranges ('Range: X.X.X to Y.Y.Y') and list formats.
    """
    explicit_versions = set()
    ranges = []
    
    if not os.path.exists(file_path):
        return explicit_versions, ranges
        
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Broad regex for Range detection: Range: START to END
                range_match = re.search(r'Range:\s*([\d\.\-]+)\s+to\s+([\d\.\-]+)', line, re.IGNORECASE)
                if range_match:
                    try:
                        start = utils.parse_version(normalize_version(range_match.group(1)))
                        end = utils.parse_version(normalize_version(range_match.group(2)))
                        ranges.append((start, end))
                    except Exception as e:
                        print(f"Note: Skipping invalid range format: {line}")
                    continue

                # Fallback: Extract anything that looks like a version number
                version_matches = re.finditer(r'(\d+\.\d+\.\d+)', line)
                for match in version_matches:
                    explicit_versions.add(match.group(1))
                    
    except Exception as e:
        print(f"Note: Error parsing MxVersions.txt: {e}")
        
    return explicit_versions, ranges

def is_valid_version(v, explicit_set, ranges):
    """Validates if a version exists in the reference list or falls within a range."""
    norm_v = normalize_version(v)
    if not norm_v: return False
    
    # 1. Check explicit list
    if norm_v in explicit_set:
        return True
        
    # 2. Check ranges
    try:
        parsed_v = utils.parse_version(norm_v)
        for start, end in ranges:
            if start <= parsed_v <= end:
                return True
    except:
        pass
        
    return False

# find_project_root moved to core/utils.py

def main():
    # Detect Path Context using standardized resolver
    # Note: utils.resolve_paths handles finding the .mpr
    project_root, userlib_path = utils.resolve_paths(__file__)
    
    if not project_root:
        utils.log_error("Could not find a Mendix project (.mpr file) in this directory or any parent directories.")
        print("Please run this tool from your Mendix project root folder.")
        sys.exit(1)
        
    userlib_path = os.path.join(project_root, 'userlib')
    
    # Custom Revert String: zipname --revert or --revert
    if len(sys.argv) >= 3 and sys.argv[2].lower() == "--revert":
        zip_to_revert = sys.argv[1]
        utils.log_header("Mendix Userlib Cleanup (Special Revert)")
        utils.revert_files(userlib_path, specific_zip=zip_to_revert)
        sys.exit(0)

    # Global Revert Check (Prioritized)
    if '--revert' in sys.argv:
        utils.log_header("Mendix Userlib Cleanup (Revert Mode)")
        utils.revert_files(userlib_path)
        sys.exit(0)
    
    utils.log_header("Mendix Userlib Cleanup")
    print() # Match user's requested spacing
    
    # 1. Detect Version
    utils.log_info("Detecting used Mendix Studio Pro version...")
    version_str = get_mendix_version(project_root)
    
    # Load reference data from the bundled config
    config_dir = os.path.join(RESOURCE_DIR, "config")
    explicit_set, ranges = parse_mx_versions(os.path.join(config_dir, "MxVersions.txt"))
    
    if version_str:
        utils.log_success(f"Detected Mendix Version: {version_str}")
        print() # Match user's requested spacing
        utils.log_info(f"Matching found Mendix version {version_str} with best suitable cleanup engine....")
    else:
        utils.log_warning("Could not determine project version automatically.")
        version_str = input(f"{utils.COLOR_BOLD}Please enter the Mendix Studio Pro version used for this project (e.g., 9.14.2):{utils.COLOR_RESET} ").strip()

    # Final Validation & Normalization
    version_str = normalize_version(version_str)
    
    # LTS Routing Logic
    LTS_MAPPING = {
        # 11 Series
        "11.0.0": clean_userlib_mx11.run_cleanup,
        # 10.24 LTS Series
        "10.24.13": clean_userlib_mx10.run_cleanup,
        "10.24.12": clean_userlib_mx10.run_cleanup,
        "10.24.11": clean_userlib_mx10.run_cleanup,
        "10.24.10": clean_userlib_mx10.run_cleanup,
        "10.24.9": clean_userlib_mx10.run_cleanup,
        "10.24.8": clean_userlib_mx10.run_cleanup,
        "10.24.6": clean_userlib_mx10.run_cleanup,
        "10.24.5": clean_userlib_mx10.run_cleanup,
        "10.24.4": clean_userlib_mx10.run_cleanup,
        "10.24.3": clean_userlib_mx10.run_cleanup,
        "10.24.2": clean_userlib_mx10.run_cleanup,
        "10.24.1": clean_userlib_mx10.run_cleanup,
        "10.24.0": clean_userlib_mx10.run_cleanup,
        # 9.24 LTS Series
        "9.24.40": clean_userlib_mx9.run_cleanup,
        "9.24.39": clean_userlib_mx9.run_cleanup,
        "9.24.38": clean_userlib_mx9.run_cleanup,
        "9.24.37": clean_userlib_mx9.run_cleanup,
        "9.24.36": clean_userlib_mx9.run_cleanup,
        "9.24.35": clean_userlib_mx9.run_cleanup,
        "9.24.34": clean_userlib_mx9.run_cleanup,
        # 8.18 LTS Series
        "8.18.35": clean_userlib_mx8.run_cleanup,
        "8.18.34": clean_userlib_mx8.run_cleanup
    }
    
    # Try exact match first, then prefix match
    target_func = LTS_MAPPING.get(version_str)
    
    if not target_func:
        for lts_ver, func in LTS_MAPPING.items():
            if version_str.startswith(lts_ver):
                target_func = func
                break
    
    if not target_func:
        try:
            major = int(version_str.split('.')[0])
            # Auto-assign for versions 7-11
            if major == 7:
                target_func = clean_userlib_mx7.run_cleanup
            elif major == 8:
                target_func = clean_userlib_mx8.run_cleanup
            elif major == 9:
                target_func = clean_userlib_mx9.run_cleanup
            elif major == 10:
                target_func = clean_userlib_mx10.run_cleanup
            elif major == 11:
                target_func = clean_userlib_mx11.run_cleanup
            elif major > 11:
                target_func = clean_userlib_mx11.run_cleanup
            elif major < 7:
                target_func = clean_userlib_mx7.run_cleanup
        except:
            pass
    
    if target_func:
        utils.log_success(f"Linked to cleanup engine: {target_func.__module__}")
        print() # Match user's requested spacing
    else:
        utils.log_error(f"No suitable cleanup script could be assigned for version {version_str}")
        sys.exit(1)
    
    # Execute Targeted Engine directly
    try:
        target_func()
    except KeyboardInterrupt:
        utils.log_info("Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        utils.log_error(f"Engine failure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
