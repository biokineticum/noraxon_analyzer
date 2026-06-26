import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget
from PySide6.QtGui import QIcon

from module_extractor import ModuleExtractor
from module_target import ModuleTarget
from module_air import ModuleAir
from module_bulk import ModuleBulk

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biomechanical Analysis - PhysioSim")
        self.resize(1200, 800)

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab 1: Data Preprocessing & Event Extraction (Tarcza)
        self.tab_extractor = ModuleExtractor()
        self.tabs.addTab(self.tab_extractor, "1. Event Extraction (Force Plate)")

        # Tab 2: Target Velocity Analysis (Tarcza)
        self.tab_target = ModuleTarget()
        self.tabs.addTab(self.tab_target, "2. Velocity Analysis (Force Plate)")

        # Tab 3: Air Analysis (Powietrze)
        self.tab_air = ModuleAir()
        self.tabs.addTab(self.tab_air, "3. Air Analysis (Inertial)")

        # Tab 4: Bulk Analysis (Force + Accel)
        self.tab_bulk = ModuleBulk()
        self.tabs.addTab(self.tab_bulk, "4. Bulk Analysis (Force + Accel)")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set app style for a modern look if possible
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

