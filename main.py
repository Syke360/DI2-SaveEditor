import sys
import os
import subprocess
import json
import glob
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, 
                             QMenu, QComboBox, QSpinBox, QHBoxLayout)
from PyQt6.QtCore import Qt

class DI2Editor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DI2 Save Specialist - GitHub Edition")
        self.setMinimumSize(1000, 700)
        
        self.save_path = self.find_save_path()
        self.init_ui()

    def init_ui(self):
        # Professional "Terminal" Styling for Linux Enthusiasts
        self.setStyleSheet("""
            QMainWindow { background-color: #0d0d0d; }
            QWidget { background-color: #0d0d0d; color: #00ff41; font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; }
            QPushButton { background-color: #1a1a1a; border: 1px solid #00ff41; padding: 10px; border-radius: 2px; color: #00ff41; }
            QPushButton:hover { background-color: #004400; }
            QTableWidget { background-color: #050505; gridline-color: #004400; border: 1px solid #00ff41; selection-background-color: #003300; }
            QHeaderView::section { background-color: #1a1a1a; padding: 8px; border: 1px solid #00ff41; color: #00ff41; font-weight: bold; }
            QTabWidget::pane { border: 1px solid #00ff41; top: -1px; }
            QTabBar::tab { background: #050505; padding: 10px 25px; border: 1px solid #00ff41; border-bottom: none; margin-right: 2px; }
            QTabBar::tab:selected { background: #1a1a1a; border-top: 4px solid #00ff41; }
            QComboBox, QSpinBox { background: #050505; border: 1px solid #00ff41; padding: 5px; color: #00ff41; }
        """)

        main_layout = QVBoxLayout()
        tabs = QTabWidget()

        # --- TAB 1: DASHBOARD ---
        dash_tab = QWidget()
        dash_layout = QVBoxLayout()
        
        self.status_label = QLabel(f"<b>[SYSTEM STATUS]:</b> {self.save_path if self.save_path else 'WAITING FOR TARGET LINK...'}")
        self.status_label.setWordWrap(True)
        dash_layout.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        browse_btn = QPushButton("📂 LINK SAVE FILE")
        browse_btn.clicked.connect(self.manual_browse)
        refresh_btn = QPushButton("🔄 INITIALIZE SCAN")
        refresh_btn.clicked.connect(self.refresh_inventory)
        btn_row.addWidget(browse_btn)
        btn_row.addWidget(refresh_btn)
        dash_layout.addLayout(btn_row)

        dash_layout.addWidget(QLabel("<br><b>KERNEL LEVEL OVERRIDES:</b>"))
        dash_layout.addWidget(self.create_action_btn("🚀 APPLY MAX XP", "max-xp"))
        dash_layout.addWidget(self.create_action_btn("📜 SYNC ALL BLUEPRINTS", "unlock-blueprints"))
        dash_layout.addWidget(self.create_action_btn("🥎 UNLOCK ALL CURVEBALLS", "unlock-curveballs"))
        
        cash_btn = QPushButton("💰 INJECT $500,000")
        cash_btn.clicked.connect(lambda: self.run_cli_action("player inventory add --name DA_InventoryTypes_Special_CashItem --count 500000"))
        dash_layout.addWidget(cash_btn)

        dash_layout.addStretch()
        
        # Attribution footer
        credits = QLabel("Powered by DI2SE CLI (Steffen André Langnes) | GUI Development by Packet & Dave")
        credits.setStyleSheet("color: #004400; font-size: 10px;")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dash_layout.addWidget(credits)
        
        dash_tab.setLayout(dash_layout)

        # --- TAB 2: INVENTORY ---
        inv_tab = QWidget()
        inv_layout = QVBoxLayout()
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ENTRY ID", "ARCHETYPE", "LVL", "RARITY"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_table_context_menu)
        inv_layout.addWidget(self.table)
        inv_tab.setLayout(inv_layout)

        # --- TAB 3: ARMORY ---
        armory_tab = QWidget()
        armory_layout = QVBoxLayout()
        armory_layout.addWidget(QLabel("<b>SELECT WEAPON CHASSIS:</b>"))
        self.weapon_sel = QComboBox()
        self.weapon_sel.setEditable(True)
        self.weapon_sel.addItems(["DA_MeleeWeaponArchetype_Katana", "DA_MeleeWeaponArchetype_Machete", "DA_MeleeWeaponArchetype_Claymore", "DA_RangedWeaponArchetype_HuntingRifle", "DA_RangedWeaponArchetype_SportingRifle"])
        armory_layout.addWidget(self.weapon_sel)

        armory_layout.addWidget(QLabel("<br><b>QUALITY GRADE:</b>"))
        self.rarity_sel = QComboBox()
        self.rarity_sel.addItems(["legendary", "superior", "rare", "uncommon"])
        armory_layout.addWidget(self.rarity_sel)

        forge_btn = QPushButton("⚔️ FORGE AND INJECT")
        forge_btn.clicked.connect(self.forge_weapon)
        armory_layout.addWidget(forge_btn)
        armory_layout.addStretch()
        armory_tab.setLayout(armory_layout)

        tabs.addTab(dash_tab, "DASHBOARD")
        tabs.addTab(inv_tab, "INVENTORY")
        tabs.addTab(armory_tab, "ARMORY")
        main_layout.addWidget(tabs)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_action_btn(self, text, cmd):
        btn = QPushButton(text)
        btn.clicked.connect(lambda: self.run_cli_action(cmd))
        return btn

    def find_save_path(self):
        # Dynamic search for common Linux/Steam mount points
        user_home = os.path.expanduser("~")
        search_patterns = [
            f"{user_home}/.local/share/Steam/steamapps/compatdata/934700/pfx/drive_c/users/steamuser/AppData/Local/DeadIslandSteam/Saved/SaveGames/",
            f"{user_home}/.steam/steam/steamapps/compatdata/934700/pfx/drive_c/users/steamuser/AppData/Local/DeadIslandSteam/Saved/SaveGames/",
            "/run/media/*/*/SteamLibrary/steamapps/compatdata/934700/pfx/drive_c/users/steamuser/AppData/Local/DeadIslandSteam/Saved/SaveGames/"
        ]
        
        for pattern in search_patterns:
            matches = glob.glob(pattern)
            for path in matches:
                if os.path.exists(path):
                    files = [f for f in os.listdir(path) if f.endswith(".sav") and ".bak" not in f]
                    if files:
                        files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)
                        return os.path.join(path, files[0])
        return ""

    def manual_browse(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select Dead Island 2 Save", "", "Save Files (*.sav)")
        if f:
            self.save_path = f
            self.status_label.setText(f"<b>[TARGET LINKED]:</b> {self.save_path}")
            self.refresh_inventory()

    def refresh_inventory(self):
        if not self.save_path: return
        cmd = f"di2save player inventory ls --file '{self.save_path}' | yq -o=json"
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                weapons = data.get("Weapons", [])
                self.table.setRowCount(0)
                for w in weapons:
                    row = self.table.rowCount()
                    self.table.insertRow(row)
                    full_id = w['EntryID']
                    short = w['Archetype'].split('.')[-1]
                    ctx = w.get('ProceduralGenerationContext', {})
                    lvl = ctx.get('RequiredLevel', '?')
                    rar = ctx.get('RequiredRarity', 'N/A').split('::')[-1]
                    id_i = QTableWidgetItem(full_id[:12] + "...")
                    id_i.setData(Qt.ItemDataRole.UserRole, full_id)
                    self.table.setItem(row, 0, id_i)
                    self.table.setItem(row, 1, QTableWidgetItem(short))
                    self.table.setItem(row, 2, QTableWidgetItem(str(lvl)))
                    self.table.setItem(row, 3, QTableWidgetItem(rar))
        except Exception as e: print(f"Refresh Err: {e}")

    def forge_weapon(self):
        if not self.save_path: return
        self.run_cli_action(f"player inventory add --name {self.weapon_sel.currentText()} --rarity {self.rarity_sel.currentText()}")

    def show_table_context_menu(self, pos):
        item = self.table.itemAt(pos)
        if not item: return
        row = self.table.row(item)
        eid = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        m = QMenu()
        rep = m.addAction("🔧 Quick Repair")
        leg = m.addAction("⭐ Boost to Legendary")
        rem = m.addAction("🗑️ Purge Item Data")
        act = m.exec(self.table.mapToGlobal(pos))
        if act == rep: self.run_cli_action(f"player inventory edit --item {eid} --durability 9999")
        elif act == leg: self.run_cli_action(f"player inventory edit --item {eid} --rarity legendary --level 30")
        elif act == rem: self.run_cli_action(f"player inventory rm {eid}")

    def run_cli_action(self, action):
        if not self.save_path: return
        
        # Security: Create a rolling backup
        subprocess.run(["cp", self.save_path, f"{self.save_path}.bak"])
        
        # Check if the command is a 'Quick' apply or a standard 'Inventory' edit
        # Added 'curveballs' to the quick-check list
        if any(x in action for x in ["max-xp", "unlock-blueprints", "unlock-curveballs"]):
            full_cmd = ["di2save", "quick", "apply", action, "--file", self.save_path]
        else:
            # Standard subcommands (inventory, stash, edit, rm)
            full_cmd = ["di2save"] + action.split() + ["--file", self.save_path]
            
        res = subprocess.run(full_cmd, capture_output=True, text=True)
        if res.returncode == 0:
            QMessageBox.information(self, "Success", f"DATA SYNC COMPLETE:\n{action}")
            self.refresh_inventory()
        else: 
            QMessageBox.critical(self, "FAULT", res.stderr)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = DI2Editor()
    ex.show()
    sys.exit(app.exec())