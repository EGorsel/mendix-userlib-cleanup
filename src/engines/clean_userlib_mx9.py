# Author: Erik van Gorsel
# Optimization: Mendix 9 Advanced Normalization
#
# Architectural Shift: 
# Increased module complexity in Mx9 required advanced normalization 
# and deep metadata scanning for safe duplicate identification.

import os
import sys
import re
from collections import defaultdict

# Add 'core' to path to find cleanup_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
import utils

def clean_mx9_userlib():
    # Resolve paths using standardized resolver
    project_root, userlib_path = utils.resolve_paths(__file__)

    if not os.path.exists(userlib_path):
        utils.log_error("userlib folder not found.")
        return

    all_files = [f for f in os.listdir(userlib_path) if os.path.isfile(os.path.join(userlib_path, f))]
    all_files = [f for f in all_files if not f.startswith('userlib_backup_') and not f.endswith('.zip')]
    jars = [f for f in all_files if f.endswith('.jar')]
    
    if not jars:
        utils.log_info("Everything is clean! No JAR files found in userlib.")
        return

    to_move = set()

    # 1. Filename-based grouping with normalization
    library_groups = defaultdict(list)
    for jar in jars:
        base_name, ver = utils.get_jar_details(jar)
        normalized_name = utils.normalize_lib_name(base_name)
        library_groups[normalized_name].append({'file': jar, 'version': ver})

    for norm_name, files in library_groups.items():
        if len(files) > 1:
            files.sort(key=lambda x: utils.parse_version(x['version']))
            for old in files[:-1]:
                to_move.add(old['file'])

    # 2. Deep scan with .exe tool
    utils.log_info("Running deep scan with signature-based engine...")
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

    final_removal_set = {f for f in to_move if not any(lib in f.lower() for lib in utils.PROTECTED_LIBS)}
    for prot in (to_move - final_removal_set):
        utils.log_info(f"Protecting critical library: {prot}")

    utils.log_info(f"Reviewed {len(all_files)} files in userlib.")
    utils.handle_backup_and_cleanup(final_removal_set, userlib_path, engine_name="Mendix 9 Engine")

if __name__ == "__main__":
    clean_mx9_userlib()
