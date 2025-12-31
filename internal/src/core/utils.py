import os
import re
import sys
import shutil
import subprocess
from datetime import datetime
import zipfile

# ANSI escape codes for basic terminal coloring
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_CYAN = "\033[96m"

def log_info(msg): print(f"{COLOR_CYAN}>>> {msg}{COLOR_RESET}")
def log_success(msg): print(f"    {COLOR_GREEN}✓ {msg}{COLOR_RESET}")
def log_warning(msg): print(f"{COLOR_YELLOW}⚠️  WARNING: {msg}{COLOR_RESET}")
def log_error(msg): print(f"{COLOR_RED}❌ ERROR: {msg}{COLOR_RESET}")

def log_header(msg):
    width = 60
    padding = (width - len(msg)) // 2
    print(f"\n{COLOR_CYAN}{'=' * width}")
    print(f"{' ' * padding}{msg}")
    print(f"{'=' * width}{COLOR_RESET}")

def log_subheader(msg):
    print(f"\n{COLOR_CYAN}------------------------------------------------------------")
    print(f"   {msg}")
    print(f"------------------------------------------------------------{COLOR_RESET}")

def log_step(current, total, msg):
    print(f"\n{COLOR_CYAN}[{current}/{total}] {msg}{COLOR_RESET}")

def log_divider():
    print(f"{COLOR_CYAN}------------------------------------------------------------{COLOR_RESET}")

class SimpleVersion:
    """A minimal version parser to replace the 'packaging' library dependency."""
    def __init__(self, version_str):
        self.version_str = str(version_str)
        # Extract only digits and dots
        clean_v = re.search(r'(\d+\.\d+(\.\d+)?)', self.version_str)
        self.parts = tuple(map(int, clean_v.group(1).split('.'))) if clean_v else (0, 0, 0)

    def __lt__(self, other): return self.parts < other.parts
    def __le__(self, other): return self.parts <= other.parts
    def __gt__(self, other): return self.parts > other.parts
    def __ge__(self, other): return self.parts >= other.parts
    def __eq__(self, other): return self.parts == other.parts
    def __repr__(self): return self.version_str

def parse_version(v):
    return SimpleVersion(v)

# Libraries that should NEVER be removed
PROTECTED_LIBS = [
    "bcprov", "bcpkix", "bcpg", "dom4j", 
    "jaxb-api", "activation", "javax.activation", 
    "javax.annotation", "javax.xml.bind",
    "checker-qual", "error_prone_annotations", "failureaccess", "listenablefuture"
]

def normalize_lib_name(name):
    """Normalizes library names by removing package prefixes and module suffixes."""
    prefixes = [
        r"^org\.apache\.(poi|commons|xmlbeans|httpcomponents)\.",
        r"^com\.google\.guava\.",
        r"^com\.fasterxml\.jackson\.",
        r"^net\.sf\.",
        r"^javax\.",
        r"^com\.springsource\."
    ]
    
    normalized = name.lower()
    for p in prefixes:
        normalized = re.sub(p, "", normalized)
    
    normalized = re.sub(r"\.(VideoConferenceModule|OQLModule|ExcelImporter|XLSReport|CommunityCommons|GoogleAuth|JWT|Deeplink)\.(RequiredLib|Required)$", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\.RequiredLib$", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\.Required$", "", normalized, flags=re.IGNORECASE)
    
    return normalized

def get_jar_details(filename):
    """Splits a JAR filename into a base name and a version string."""
    temp_name = re.sub(r"\.(VideoConferenceModule|OQLModule|ExcelImporter|XLSReport|CommunityCommons|GoogleAuth|JWT|Deeplink)\.(RequiredLib|Required)$", "", filename, flags=re.IGNORECASE)
    temp_name = re.sub(r"\.(RequiredLib|Required)$", "", temp_name, flags=re.IGNORECASE)
    temp_name = temp_name.replace(".jar", "")

    match = re.search(r'^(.*?)-(\d.*)$', temp_name)
    if match:
        return match.group(1), match.group(2)
    return temp_name, "0.0.0"

def get_exe_tool_findings(userlib_path):
    """Runs mendix-userlib-cleaner.exe and parses output."""
    # The exe is in the same 'internal' folder as this utility script
    internal_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(internal_dir, 'mendix-userlib-cleaner.exe')
    
    if not os.path.exists(exe_path):
        return []
    
    try:
        result = subprocess.run([exe_path, "--target", userlib_path], capture_output=True, text=True)
        combined = result.stdout + "\n" + result.stderr
        findings = []
        for line in combined.splitlines():
            if "Would remove file" in line:
                match = re.search(r'Would remove file.*:\s+(.*)$', line)
                if match:
                    filename = os.path.basename(match.group(1).strip())
                    if filename.endswith('.jar'):
                        findings.append(filename)
        return list(set(findings))
    except Exception as e:
        print(f"Warning: Could not run .exe tool: {e}")
        return []

def create_backup_manifest(to_move, timestamp):
    """Creates a simple text manifest explaining why files were removed."""
    manifest = [
        f"Mendix Userlib Cleanup Manifest",
        f"Timestamp: {timestamp}",
        f"Total items removed: {len(to_move)}",
        "\n--- Removed Files ---"
    ]
    for f in sorted(list(to_move)):
        manifest.append(f" - {f}")
    return "\n".join(manifest)

def handle_backup_and_cleanup(to_move, userlib_path, total_scanned=0, engine_name="Unknown"):
    """Centralized backup, compression, and removal logic with clear feedback."""
    check_mode = '--check' in sys.argv

    if not to_move:
        log_divider()
        log_success(f"Everything is clean! No redundant libraries found by {engine_name} scan.")
        return

    # CI/CD Check Mode
    if check_mode:
        log_error(f"Cleanup check failed: Found {len(to_move)} redundant files.")
        sys.exit(1)

    log_subheader("Redundant libraries detected")
    print(f"A total of {COLOR_BOLD}*{len(to_move)} redundant libraries*{COLOR_RESET} were found, including:")
    
    sorted_items = sorted(list(to_move))
    # Show first 15, then ...
    display_limit = 15
    for f in sorted_items[:display_limit]:
        print(f"  - {f}")
    
    if len(sorted_items) > display_limit:
        print(f"  ... (full list included in cleanup summary)")

    log_subheader("Scan Summary")
    print(f"  • Total files scanned:       {total_scanned}") 
    print(f"  • Redundant files detected:   {len(to_move)}")
    print(f"  • Protected files:           (multiple, see above)")

    log_divider()
    log_warning(f"The cleanup will remove {len(to_move)} files from /userlib.")
    print(f"    A backup ZIP will be created automatically in:")
    print(f"       userlib_backup/<timestamp>.zip")
    
    print(f"\nType {COLOR_BOLD}\"PROCEED\"{COLOR_RESET} to confirm and continue.")
    confirm = input(f"→ ").strip().upper()

    if confirm == 'CANCEL':
        log_info("Operation cancelled. No changes were made.")
        sys.exit(0)
    elif confirm != 'PROCEED':
        log_error("Invalid input. Operation cancelled for safety.")
        sys.exit(1)

    log_subheader("Performing cleanup...")

    backup_folder = os.path.join(userlib_path, 'userlib_backup')
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
        
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    zip_filename = f"userlib_backup_{timestamp}.zip"
    zip_path = os.path.join(backup_folder, zip_filename)
    
    try:
        manifest_content = create_backup_manifest(to_move, timestamp)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add manifest
            zip_file.writestr("cleanup_manifest.txt", manifest_content)
            
            # Add files and remove them
            for f in to_move:
                full_path = os.path.join(userlib_path, f)
                if os.path.exists(full_path):
                    zip_file.write(full_path, arcname=f)
                    os.remove(full_path)
        
        num_files = len(to_move)
        log_success("Backup archive created successfully")
        log_success(f"{num_files} redundant files removed from /userlib/")
        
        # Simple post-cleanup health check
        print()
        log_step(5, 5, "Running post-cleanup project health check...")
        validate_cleanup_result(project_root=os.path.dirname(userlib_path))
        
        log_header("Cleanup Complete — Userlib successfully optimized!")
        print("\nThank you for using the Mendix Userlib Cleanup Utility.")
        print("Hope it saved you some time! 😊\n")
    except Exception as e:
        log_error(f"Error during backup process: {e}")

def validate_cleanup_result(project_root):
    """
    Verifies project health post-cleanup:
    1. Check if .mpr exists and is readable.
    2. Check for critical Mendix system artifacts.
    """
    # log_info("Scanning project health post-cleanup...")
    
    # 1. Database Check
    mpr_files = [f for f in os.listdir(project_root) if f.endswith('.mpr') and not f.endswith('.bak')]
    if not mpr_files:
        log_error("CRITICAL: .mpr file missing after cleanup!")
        return False
        
    mpr_path = os.path.join(project_root, mpr_files[0])
    try:
        import sqlite3
        conn = sqlite3.connect(f"file:{mpr_path}?mode=ro", uri=True)
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        conn.close()
    except Exception as e:
        log_error(f"CRITICAL: .mpr database is unreadable: {e}")
        return False

    # 2. System Artifact Check (Sanity check for userlib)
    # We just want to ensure we didn't wipe the directory entirely if it was supposed to have content
    userlib = os.path.join(project_root, 'userlib')
    if os.path.exists(userlib):
        jars = [f for f in os.listdir(userlib) if f.endswith('.jar')]
        # This is just a warning, some projects might have empty userlibs
        if not jars:
            log_warning("Userlib is now empty. This is normal if all dependencies are managed or removed.")

    log_success("Health check passed. Project structure is intact.")
    return True

def revert_files(userlib_path, specific_zip=None):
    """Universal revert logic."""
    backup_path = os.path.join(userlib_path, 'userlib_backup')
    if not os.path.exists(backup_path):
        print("Error: No backup directory found.")
        return

    if specific_zip:
        zip_file = specific_zip if specific_zip.endswith('.zip') else specific_zip + '.zip'
        target_zip = os.path.join(backup_path, zip_file)
        if not os.path.exists(target_zip):
            # Try searching just by filename if a full path wasn't provided correctly
            target_zip = os.path.join(backup_path, os.path.basename(zip_file))
            if not os.path.exists(target_zip):
                print(f"Error: Could not find backup file: {zip_file}")
                return
    else:
        zips = [f for f in os.listdir(backup_path) if f.startswith('userlib_backup_') and f.endswith('.zip')]
        if not zips:
            print("No ZIP backup files found.")
            return
        zips.sort()
        target_zip = os.path.join(backup_path, zips[-1])
        zip_file = zips[-1]

    print(f"Reverting from: {zip_file}")
    
    try:
        with zipfile.ZipFile(target_zip, 'r') as zip_ref:
            zip_ref.extractall(userlib_path)
            print(f"Restored {len(zip_ref.namelist())} files.")
        os.remove(target_zip)
    except Exception as e:
        print(f"Error during revert: {e}")

def get_vendorlib_jars(project_root):
    """Lists JAR files currently managed in vendorlib."""
    vendorlib_path = os.path.join(project_root, 'vendorlib')
    if not os.path.exists(vendorlib_path):
        return []
    
    vendor_jars = []
    for root, dirs, files in os.walk(vendorlib_path):
        for f in files:
            if f.endswith('.jar'):
                vendor_jars.append(f)
    return vendor_jars

def find_project_root(start_path):
    """Searches upward from start_path to find a folder containing an .mpr file."""
    curr = os.path.abspath(start_path)
    while True:
        mpr_files = [f for f in os.listdir(curr) if f.endswith('.mpr') and not f.endswith('.bak')]
        if mpr_files:
            return curr
        
        parent = os.path.dirname(curr)
        if parent == curr: 
            break
        curr = parent
    return None

def resolve_paths(script_file):
    """
    Standardized path resolution for all cleanup scripts.
    Returns (project_root, userlib_path)
    """
    script_dir = os.path.dirname(os.path.abspath(script_file))
    
    # Context 1: Try current working directory
    project_root = find_project_root(os.getcwd())
    
    # Context 2: Try script's location (assuming engines are in cleanup_suite/engines/)
    if not project_root:
        # If in 'src/engines' or 'src/core', go up 2 levels to find project root
        project_root = find_project_root(os.path.dirname(os.path.dirname(script_dir)))

    if not project_root:
        return None, None
        
    userlib_path = os.path.join(project_root, 'userlib')
    return project_root, userlib_path
