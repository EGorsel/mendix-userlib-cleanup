# 🚀 Mendix Universal Userlib Cleanup Suite

A version-aware automation suite to solve "JAR Hell" in Mendix projects (v7–v11). It identifies redundant libraries, creates backups, and ensures stability.

### Why this Project?
This tool was developed to provide Mendix developers with a universal, version-aware cleanup solution that adapts to different platform architectures. It is built upon the powerful [mendix-userlib-cleaner](https://github.com/cinaq/mendix-userlib-cleaner) engine by **CINAQ Technology**, extending its capabilities with automated version detection and specialized logic for Mendix 7 through 11.

<div align="right"><b>Created by: Erik van Gorsel</b></div>

---

## 🌟 Key Features
- **Auto-Detection**: Reads `.mpr` to apply the correct logic for your Mendix version.
- **Universal**: Specialized support for Mendix 7, 8, 9, 10, and 11.
- **Safety First**: Moves files to timestamped ZIP backups with a one-click revert.
- **Vendorlib Aware**: Handles the Mendix 10/11 `vendorlib` structure correctly.
- **Zero Dependency**: Standalone `.exe` available (no Python required).
- **CI/CD Ready**: Integrated `--check` mode for GitHub Actions/Pipelines.

---

## 📥 Quick Start

1. **Setup**: Copy the cleanup tool folder (or the standalone `.exe`) directly into your **Mendix Project Root** (where your `.mpr` file is located).
2. **Run**:
   - Open your project folder in File Explorer.
   - Type `cmd` in the address bar and press **Enter**.
   - Run the command:

          mx--cleanuserlib

---

## 🔄 Revert Changes
Use the commands below in the same directory as the cleanup tool in order to revert changes.
- **Revert latest Backup**:

        mx--cleanuserlib --revert
- **Revert specific Backup**: 

        mx--cleanuserlib [zip_filename] --revert

---

## ⚙️ How it Works (Under the Hood)
1. **Context Resolution**: Locates your Mendix project root by searching for the `.mpr` file.
2. **Version Detection**: Extracts the exact Mendix Studio Pro version from your project metadata.
3. **Smart Routing**: Selects the specialized cleanup script (Mx7–Mx11) based on the detected version.
4. **Vendorlib Audit (Mx10+)**: Cross-references the `vendorlib` folder to identify JARs that are now managed by Mendix.
5. **Deep Scanning**: Runs a signature-based engine (`.exe`) to find identical libraries even if filenames differ.
6. **Safety Filtering**: Protects critical system libraries and required files from accidental removal.
7. **ZIP Archiving**: Moves redundant files into a timestamped ZIP backup for easy restoration.

---

## 🛠️ Advanced Usage

### Standalone Executable (No Python)
If you don't want to install Python, download the latest standalone ZIP from our [Releases](https://github.com/EGorsel/mendix-userlib-cleanup/releases). It includes everything you need to run the tool instantly.

*Note: Developers can generate their own standalone build by running `scripts\local_build.bat`.*

### CI/CD Integration
Prevent "JAR Hell" from ever reaching your main branch by adding a cleanup check to your workflow:

```bash
mx--cleanuserlib --check
```
*Returns exit code 1 if redundant files are detected.*

---

## 📂 Architecture
| Script | Platform Shift & Logic Evolution |
| :--- | :--- |
| `src/core/manager.py` | **The Orchestrator**: Handles version detection, routing, and safety health-checks. |
| `src/engines/clean_userlib_mx11.py` | **Mendix 11**: Optimized for Java 21 and advanced `vendorlib` dependency resolution. |
| `src/engines/clean_userlib_mx10.py` | **Mendix 10**: Cross-references "unmanaged" `userlib` against the new "managed" `vendorlib` architecture. |
| `src/engines/clean_userlib_mx9.py` | **Mendix 9**: Implements advanced name normalization and legacy deep-scan support. |
| `src/engines/clean_userlib_mx8.py` | **Mendix 8**: Tailored for Java 11 transition and initial `.requiredlib` metadata parsing. |
| `src/engines/clean_userlib_mx7.py` | **Mendix 7**: Baseline logic designed for legacy Java 8 and old module packaging formats. |

---

## 🐛 Report a Bug
Found an issue? Help us improve by following our [Bug Reporting Guide](docs/BugReport.md). Clear reports with version details help us resolve issues faster.

---

## 🤝 Contributing
We welcome the community to help make this tool better for everyone! Whether you want to fix a bug, suggest a feature, or improve documentation, please see our [Contribution Guide](docs/Contribute.md) to get started.

---

## 🤝 Credits
Built upon the [mendix-userlib-cleaner](https://github.com/cinaq/mendix-userlib-cleaner) engine by **CINAQ Technology**.
