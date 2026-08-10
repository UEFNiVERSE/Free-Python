# 🐍 UEFNiVERSE - Free-Python Tool Collection
Professional Python tools for UEFN creators. 100% free and open-source.
Community requests are always welcome via the UEFNiVERSE Discord or Issue Requests!

## License Note
This project is licensed under **[Apache 2.0](https://choosealicense.com/licenses/apache-2.0/) + the [Commons Clause](https://commonsclause.com/)**. In plain terms:

- ✅ **Free to use in your UEFN workflow.** Run these tools on any project — published or private, monetized or not — at no cost.
- ✅ **Forking and contributing is welcome.** Fork the repo, modify the code, and open a PR. Community contributions are encouraged.
- ❌ **You cannot sell the library itself.** The Commons Clause means you may not sell a product or service whose value derives *primarily* from this library (for example, reselling these tools as a paid pack or paid support service for them).

In short: build whatever you want *with* these tools — just don't sell *them*. See [LICENSE](LICENSE) for the full terms.

## Overview
Free-Python is the Python-side companion to [Free-Verse](https://github.com/UEFNiVERSE/Free-Verse): reusable, well-documented Python tools that automate and speed up UEFN development workflows. Each tool lives in its own folder with a README covering setup, usage, and examples.

> Have a workflow you wish was automated? [Open a feature request](../../issues/new/choose) or suggest it on Discord!

## Tools

| Tool | What It Does | Author(s) | Release |
|---|---|---|---|
| [Sortilege](Sortilege/) | Sorts your Content Drawer into tidy category folders — dry-run preview by default, full undo | mangoUEFN, PineFruit | v1.0.0 |

Each tool folder has its own README with full setup, configuration, and examples.

## Requirements
- [Python 3.10+](https://www.python.org/downloads/)
- Any tool-specific dependencies are listed in that tool's README (and its `requirements.txt` where applicable)

## Installation
1. Clone the repo (or download just the tool folder(s) you need)
2. Check the tool's README for setup and any dependencies
3. Install dependencies if the tool has them: `pip install -r requirements.txt` (from the tool's folder)
4. Run the tool per its README
   - If you hit any errors and need assistance, reach out to us on Discord!

---

## Contributing
We welcome contributions from the UEFN community!

**👉 Read our [CONTRIBUTING.md](CONTRIBUTING.md) for complete guidelines:**
- How to report bugs
- How to suggest features
- Development prerequisites
- Contribution workflow (fork, branch, PR)
- Coding standards and best practices
- PR review process

**Quick Start:** Fork → Create feature branch → Make changes → Submit PR

---

## Community Tools
Third-party tooling from the wider UEFN community. These projects are **not part of this collection** and are **not covered by this repository's license**. Each one is maintained by its own author, under whatever terms that author sets. They are listed here because they are useful to the same creators these tools are for.

### Verse Field Tool
**By Supreme** ([@supremeuefn](https://github.com/supremeuefn)) · [supremeuefn/uefn-python-tools](https://github.com/supremeuefn/uefn-python-tools)

A standalone in-editor GUI for creating, managing, and MVVM-binding Verse-exposed variables ("Verse fields") on UEFN Widget Blueprints. Run it inside UEFN via **Tools > Execute Python Script**.

- **Create fields** of any supported type (float, int, logic, string, message, color, color_alpha, material, texture, event), organized into categories
- **Bulk-bind** a widget's Verse fields to engine widget properties, to the Verse fields of embedded child-widget instances, or to button events (OnClicked, OnHovered, and similar)
- **Event parameters**, where each binding carries its own value, so a single Verse handler can tell which button called it
- **Manage fields** with crash-safe deletion of freshly-created fields

Creating and binding Verse fields by hand is error-prone and can crash UEFN. This tool wraps the whole create, patch, compile, verify, bind workflow behind a UI. Requires only `unreal`, the Python standard library, and PySide6.

> ⚠️ **Licensing:** `uefn-python-tools` currently ships **no license file**, so it grants no reuse terms. Treat it as all rights reserved: use the tool as published, and speak to Supreme directly before redistributing it or building on its source. Listing it here is a credit and a link, not a sublicense, and it does **not** place his work under this repository's Apache 2.0 + Commons Clause.

Listed with Supreme's permission. Please raise issues and feature requests for this tool on its own repository, not here.

---

## Support

**Maintainer:** PineFruit — per-tool authors are listed in the [Tools](#tools) table
**Organization:** Chartis / UEFNiVERSE
**License:** Open-Source (see LICENSE)

**Contact:**
- Discord: PineFruit, LastMadeUEFN
- Epic: PineFruitDev, LastMadeMe
- Twitter: @PineFruitDev, @LastMadeUefn

**Resources:**
- Each tool has its own detailed README
- Reach out on discord if you need anything: https://discord.gg/UEFNiVERSE
- [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines

---

**License:** [Apache 2.0](https://choosealicense.com/licenses/apache-2.0/) with [Commons Clause](https://commonsclause.com/)
**Powered by:** [Project Moonlight](https://www.projectmoonlight.org/)
