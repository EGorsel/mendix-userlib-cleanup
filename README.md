# 🚀 Mendix Universal Userlib Cleanup Suite


### Why this Project?
This tool provides Mendix developers with a universal, version-aware suite to solve "JAR Hell" in Mendix projects (v7–v11). The project is built upon the powerful [mendix-userlib-cleaner](https://github.com/cinaq/mendix-userlib-cleaner) engine by **CINAQ Technology** and extends the core capabilities of the engine with:

- **Automated Version Detection**: Intelligence to read `.mpr` metadata and apply the correct logic for Mendix 7 through 11 automatically.
- **Universal Support**: Specialized engines tailored for the evolving architectures of Mendix 7, 8, 9, 10, and 11.
- **Vendorlib Awareness**: Advanced logic to correctly handle the Mendix 10/11 `vendorlib` architecture and managed dependencies.
- **Zero-Dependency Standalone Mode**: Standalone execution (.exe) — no Python installation required for end-users ([Security Note](#-security--trust)).
- **DevOps & CI/CD Ready**: Integrated `--check` mode for automated quality gates and pipeline validation.
- **Enhanced Safety**: Moves files to timestamped ZIP backups with a reliable one-click revert mechanism.

<div align="right"><b>Created by: Erik van Gorsel</b></div>

---

## 📖 1. How to Use

### 📥 1.1. Quick Start
1. **Setup**: Download the standalone `.exe` and place it in your **Mendix Project Root** (the folder containing your `.mpr` file).
2. **Run**:
   - Open your project folder in File Explorer.
   - Type `cmd` in the address bar and press **Enter**.
   - Execute the tool:
     ```cmd
     mx--cleanuserlib
     ```

---

### 🔄 1.2. Revert Changes
To restore deleted files, run these commands in your project root:
- **Revert Latest Backup**:
  ```cmd
  mx--cleanuserlib --revert
  ```
- **Revert Specific Backup**: 
  ```cmd
  mx--cleanuserlib [zip_filename] --revert
  ```

---

### 🛠️ 1.3. Advanced Usage (CI/CD)
Prevent "JAR Hell" from ever reaching your main branch by adding a check to your Mendix CI/CD pipeline. 

```bash
mx--cleanuserlib --check
```
*Returns **Exit Code 1** if redundant files are detected.*

> [!NOTE]
> See [Mendix CI/CD Capabilities](https://docs.mendix.com/developerportal/deploy/ci-cd-capabilities/) for official guidance on integrating custom tools.



---


## 🛡️ 2. Security & Trust
As this is a custom-built tool, some browsers (like Microsoft Edge) or Windows SmartScreen may show a warning when downloading or running the `.exe` for the first time (e.g., *"not commonly downloaded"*).

**To proceed safely:**
1. **Edge**: Click the three dots (...) next to the download > select **Keep** > click **Show more** > select **Keep anyway**.
2. **Windows**: If a blue "Windows protected your PC" popup appears, click **More info** > select **Run anyway**.

> [!TIP]
> This tool is open-source. For maximum transparency, you can review the source code in the `internal/src` directory or build the binary yourself using the provided `internal/scripts/local_build.bat`.

---

## ⚙️ 3. How the project Works
1. **Context Resolution**: Locates your Mendix project root by searching for the `.mpr` file.
2. **Version Detection**: Extracts the exact Mendix Studio Pro version from project metadata.
3. **Smart Routing**: Routes to the specialized cleanup engine (Mx7–Mx11) for that version.
4. **Vendorlib Audit (Mx10+)**: Cross-references the `vendorlib` folder to identify JARs managed by Mendix.
5. **Deep Scanning**: Runs a signature-based engine to find identical libraries even if filenames differ.
6. **Safety Filtering**: Protects critical system libraries and required files.
7. **ZIP Archiving**: Moves redundant files to a timestamped ZIP for easy restoration.

---

## 📂 4. Architecture
| Script | Responsibility |
| :--- | :--- |
| `internal/src/core/manager.py` | **The Orchestrator**: Handles version detection, routing, and safety checks. |
| `internal/src/engines/clean_userlib_mx11.py` | **Mendix 11**: Optimized for Java 21 and `vendorlib` resolution. |
| `internal/src/engines/clean_userlib_mx10.py` | **Mendix 10**: Cross-references `userlib` against the `vendorlib` architecture. |
| `internal/src/engines/clean_userlib_mx9.py` | **Mendix 9**: Implements advanced name normalization and deep-scan support. |
| `internal/src/engines/clean_userlib_mx8.py` | **Mendix 8**: Tailored for Java 11 transition and `.requiredlib` parsing. |
| `internal/src/engines/clean_userlib_mx7.py` | **Mendix 7**: Baseline logic for legacy Java 8 and old module formats. |

---

## 🛡️ 5. License
Distrubuted under the MIT License. See [LICENSE](LICENSE) for more information.

---

## 🐛 6. Community & Support
- **Bugs**: Found an issue? See our [Security & Bug Reporting Guide](SECURITY.md).
- **Contributing**: We welcome community help! Check the [Contribution Guide](CONTRIBUTING.md).
- **Credits**: Built upon the [mendix-userlib-cleaner](https://github.com/cinaq/mendix-userlib-cleaner) engine by **CINAQ Technology**.
