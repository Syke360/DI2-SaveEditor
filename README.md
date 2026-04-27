# Dead Island 2 Save Editor (Linux/Proton)

A professional PyQt6 GUI wrapper for the `di2save` CLI tool. Designed for Nobara, Steam Deck, and general Linux/Proton users.

Prerequisites
This tool is a wrapper. You MUST have the following installed:
1. **di2save CLI**: [Download here](https://www.steffenl.com/) (Ensure the binary is in your PATH).
2. **yq**: Required for parsing save data (`sudo dnf install yq` or `sudo apt install yq`).
3. **Python 3.10+** and **PyQt6**.

Features
- **Auto-Discovery**: Scans Steam/Proton prefixes and external mount points for DI2 saves.
- **Inventory Management**: Right-click weapons to Repair, Upgrade to Legendary, or Delete.
- **The Armory**: Forge new weapons (Katanas, Rifles, etc.) and inject them directly.
- **Safety First**: Automatic `.bak` creation before every single edit.
- **Quick Cheats**: Instant Max XP, Unlock Blueprints, and Unlock Curveballs.

Installation
```bash
git clone [https://github.com/Syke360/DI2-SaveEditor.git](https://github.com/Syke360/DI2-SaveEditor.git)
cd DI2-Save-Editor
pip install -r requirements.txt
python di2_gui.py
