# Author: Erik van Gorsel
# Optimization: Mendix 10 Managed Dependencies (vendorlib)
#
# Architectural Shift: 
# Transition to Managed Java Dependencies in 'vendorlib' required 
# automated cross-referencing to prevent 'userlib' redundancy.

import os
import sys
import re
from collections import defaultdict

# Add 'core' to path to find cleanup_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
import utils

# Vendorlib scanning moved to core/cleanup_utils.py

def run_cleanup():
    # Resolve paths using standardized resolver
    project_root, userlib_path = utils.resolve_paths(__file__)

    if not os.path.exists(userlib_path):
        utils.log_error("userlib folder not found.")
        return

    all_files = [f for f in os.listdir(userlib_path) if os.path.isfile(os.path.join(userlib_path, f))]
    all_files = [f for f in all_files if not f.startswith('userlib_backup_') and not f.endswith('.zip')]
    jars = [f for f in all_files if f.endswith('.jar')]
    
    if not jars:
        utils.log_info("No JAR files found in userlib.")
        return

    to_move = set()

    # 1. Vendorlib Cross-Check
    utils.log_info("Checking for managed dependencies in vendorlib...")
    vendor_jars = utils.get_vendorlib_jars(project_root)
    vendor_normalized = {utils.normalize_lib_name(utils.get_jar_details(v)[0]): v for v in vendor_jars}
    
    for jar in jars:
        base_name, ver = utils.get_jar_details(jar)
        norm_name = utils.normalize_lib_name(base_name)
        if norm_name in vendor_normalized:
            utils.log_warning(f"Found in vendorlib: {jar} (Managed as {vendor_normalized[norm_name]})")
            to_move.add(jar)

    # 2. Filename-based grouping
    library_groups = defaultdict(list)
    for jar in jars:
        if jar in to_move: continue
        base_name, ver = utils.get_jar_details(jar)
        normalized_name = utils.normalize_lib_name(base_name)
        library_groups[normalized_name].append({'file': jar, 'version': ver})

    for norm_name, files in library_groups.items():
        if len(files) > 1:
            files.sort(key=lambda x: utils.parse_version(x['version']))
            for old in files[:-1]:
                to_move.add(old['file'])

    # 3. Deep scan with .exe tool
    utils.log_subheader("Running deep scan (signature-based analysis)")
    exe_findings = utils.get_exe_tool_findings(userlib_path)
    for f in exe_findings:
        if f in jars:
            to_move.add(f)

    # 4. Filter associated metadata and protected libs
    final_list = list(to_move)
    for jar in final_list:
        pattern = re.escape(jar) + r'.*'
        for f in all_files:
            if f != jar and re.match(pattern, f):
                to_move.add(f)

    protected_detected = to_move - final_removal_set
    if protected_detected:
        print("\nProtected libraries (critical / required):")
        for prot in sorted(list(protected_detected)):
            print(f"  - {prot}")

    utils.handle_backup_and_cleanup(final_removal_set, userlib_path, total_scanned=len(all_files), engine_name="Mendix 10 Engine")

if __name__ == "__main__":
    run_cleanup()
