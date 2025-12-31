# 🚀 Mendix Universal Userlib Cleanup Suite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Mendix Support](https://img.shields.io/badge/Mendix-7%20--%2011-blue.svg)](https://docs.mendix.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/EGorsel/mendix-userlib-cleanup/graphs/commit-activity)

A version-aware automation suite designed to solve "JAR Hell" in Mendix development. It intelligently identifies redundant libraries, manages specialized backups, and ensures project stability across all LTS versions.

---

### 💡 Why this Project?
Managing Java dependencies (JARs) in Mendix can be challenging, especially as projects evolve through multiple Studio Pro versions. This suite provides a universal, automated solution that adapts to the unique architecture of each Mendix version.

The project is built upon the powerful [mendix-userlib-cleaner](https://github.com/cinaq/mendix-userlib-cleaner) engine by **CINAQ Technology**, extending it with:

- **Automated Version Detection**: Zero-config detection of Mendix 7 through 11.
- **Universal Support**: Logic-driven engines tailored for v7, v8, v9, v10, and v11.
- **Vendorlib Aware**: Intelligently handles Mendix 10/11's managed dependency system.
- **DevOps Ready**: Integrated `--check` mode for automated CI/CD pipeline quality gates.
- **Zero Dependency**: Standalone binary (.exe) — no environment setup needed.
- **Enhanced Safety**: Automatic timestamped ZIP archiving with instant restoration.

<div align="right"><b>Created by: <a href="https://github.com/EGorsel">Erik van Gorsel</a></b></div>

---

## 🗺️ Quick Links
| [📥 Download](https://github.com/EGorsel/mendix-userlib-cleanup/releases) | [📖 Use Guide](#-1-how-to-use) | [🐛 Report Bug](SECURITY.md) | [🤝 Contribute](CONTRIBUTING.md) | [⚖️ License](LICENSE) |
| :--- | :--- | :--- | :--- | :--- |

---

> [!NOTE]
> In case your browser blocks the .exe file, download the 'Source code (zip)' file instead. Unzip the file after downloading and copy the 'mx--cleanuserlib.exe' file from the unzipper folder to the root directory of your Mendix project.

## 📖 1. How to Use

   ### 📥 1.1. Quick Start

   - **Setup**:
      - Download the [latest release](https://github.com/EGorsel/mendix-userlib-cleanup/releases)
      - Place `mx--cleanuserlib.exe` in your **Mendix Project Root** (the folder containing the `.mpr` file).
      
   - **Run**:
      - Open your project folder in File Explorer.
      - Type `cmd` in the address bar and press **Enter**.
      - Execute the command below in your terminal
   
  ```cmd
  mx--cleanuserlib
  ```

   ---

   ### 🔄 1.2. Restoration
   If you need to revert changes, run these in your project root:
   - **Revert Latest**:
   ```cmd
      mx--cleanuserlib
   ```
   
   - **Revert Specific**:
   ```cmd
      mx--cleanuserlib [backup_name.zip] --revert
   ```

   ---

   ### 🛠️ 1.3. CI/CD Integration
   Fail your build pipeline if JAR issues are detected:
   ```bash
   mx--cleanuserlib --check
   ```
   *Returns **Exit Code 1** if redundant files are identified.*

---

## ⚙️ 2. How the project Works
The suite follows a standard audit methodology:
1. **Resolution**: Locates the project context via `.mpr` lookup.
2. **Identification**: Extracts the Studio Pro version from project metadata.
3. **Routing**: Matches the project to its specialized cleanup engine.
4. **Audit (Mx10+)**: Syncs `userlib` against the platform's `vendorlib` registry.
5. **Deep Scan**: Uses signature matching to find duplicates with mismatched names.
6. **Filtering**: Applies safety rules to protect required framework JARs.
7. **Archiving**: Safely isolates files into timestamped ZIP archives.

---

## 🛡️ 3. Security & Trust
As a portable utility, Windows SmartScreen may flag the `.exe` as "uncommon." 

**To proceed:**
- **Edge**: `...` > **Keep** > **Show more** > **Keep anyway**.
- **Windows**: **More info** > **Run anyway**.

> [!NOTE]
> This project is 100% open-source. For maximum transparency, you can review the source code in `internal/src` or build the binary yourself using `internal/scripts/local_build.bat`.

---

## 📂 4. Architecture
| Component | Responsibility |
| :--- | :--- |
| `internal/src/core/manager.py` | **Orchestrator**: handles detection, routing, and safety logic. |
| `internal/src/engines/clean_userlib_mx11.py` | **Mx11 Engine**: optimized for Java 21 and vendorlib registries. |
| `internal/src/engines/clean_userlib_mx10.py` | **Mx10 Engine**: handles managed vs unmanaged dependency audits. |
| `internal/src/engines/clean_userlib_mx9.py` | **Mx9 Engine**: advanced name normalization and deep-scan logic. |
| `internal/src/engines/clean_userlib_mx8.py" | **Mx8 Engine**: handles `.requiredlib` metadata and Java 11 transition. |
| `internal/src/engines/clean_userlib_mx7.py` | **Mx7 Engine**: baseline logic for legacy module packaging. |

---

## 🤝 5. Contributing & Support
This is a **community-driven** project. We welcome contributions of all kinds!

- **Contributing**: Please read our [Contribution Guide](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md).
- **Security**: Report vulnerabilities via our [Security Policy](SECURITY.md).
- **Credits**: Built upon the [mendix-userlib-cleaner](https://github.com/cinaq/mendix-userlib-cleaner) engine by **CINAQ Technology**.

---

<div align="center">
  <sub>Built with ❤️ for the Mendix Community</sub>
</div>
