# Author: Erik van Gorsel
# Optimization: Mendix 7 Legacy Java 8 & Old Packaging
#
# Architectural Shift: 
# Legacy Java 8 requirements and older non-standard module packaging 
# necessitated a dedicated baseline for core project stability.

import os
import sys
import re

# Add 'core' to path to find cleanup_utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
import utils

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
        utils.log_info("Everything is clean! No JAR files found in userlib.")
        return

    # Mendix 7 legacy approach: rely on .exe engine as baseline
    utils.log_info("Running deep scan with signature-based engine...")
    to_move = set(utils.get_exe_tool_findings(userlib_path))
    
    # Associate metadata
    final_list = list(to_move)
    for jar in final_list:
        pattern = re.escape(jar) + r'.*'
        for f in all_files:
            if f != jar and re.match(pattern, f):
                to_move.add(f)

    # Protect core libs
    final_removal_set = {f for f in to_move if not any(lib in f.lower() for lib in utils.PROTECTED_LIBS)}
    
    utils.log_info(f"Reviewed {len(all_files)} files in userlib.")
    utils.handle_backup_and_cleanup(final_removal_set, userlib_path, engine_name="Mendix 7 Engine")

if __name__ == "__main__":
    run_cleanup()
