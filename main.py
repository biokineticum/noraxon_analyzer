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
    
    app.setStyleSheet("""
        /* Global Styles */
        QMainWindow {
            background-color: #121214;
        }
        QWidget {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-size: 12px;
        }
        
        /* Tabs styling */
        QTabWidget::pane {
            border: 1px solid #1F1F23;
            background-color: #16161a;
            border-radius: 8px;
            padding: 10px;
        }
        QTabBar::tab {
            background-color: #1A1A1E;
            color: #8E8E93;
            border: 1px solid #1F1F23;
            border-bottom: none;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #16161a;
            color: #FFFFFF;
            border: 1px solid #3498DB;
            border-bottom: none;
            font-weight: bold;
        }
        QTabBar::tab:hover:!selected {
            background-color: #232328;
            color: #D1D1D6;
        }
        
        /* Group Box */
        QGroupBox {
            border: 1px solid #2A2A30;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 14px;
            font-weight: bold;
            color: #3498DB;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 4px;
            background-color: #16161a;
        }
        
        /* Buttons */
        QPushButton {
            background-color: #2C3E50;
            border: 1px solid #34495E;
            border-radius: 4px;
            color: #FFFFFF;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #34495E;
            border-color: #3498DB;
        }
        QPushButton:pressed {
            background-color: #1E2B37;
        }
        QPushButton:disabled {
            background-color: #1C1C1E;
            border-color: #242426;
            color: #48484A;
        }
        
        /* Input Fields */
        QLineEdit, QComboBox {
            background-color: #1A1A1E;
            border: 1px solid #2A2A30;
            border-radius: 4px;
            padding: 4px 8px;
            color: #E2E2E6;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #3498DB;
            background-color: #1C1C22;
        }
        QComboBox::drop-down {
            border: none;
            background-color: #232328;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            width: 20px;
        }
        
        /* Labels */
        QLabel {
            color: #E2E2E6;
        }
        
        /* Table Widget */
        QTableWidget {
            background-color: #16161a;
            gridline-color: #232328;
            border: 1px solid #1F1F23;
            border-radius: 6px;
            color: #E2E2E6;
        }
        QTableWidget::item {
            padding: 4px;
        }
        QTableWidget::item:selected {
            background-color: #2B3D52;
            color: #FFFFFF;
        }
        QHeaderView::section {
            background-color: #1A1A1E;
            color: #FFFFFF;
            padding: 6px;
            border: 1px solid #232328;
            font-weight: bold;
        }
        
        /* List Widget */
        QListWidget {
            background-color: #16161a;
            border: 1px solid #1F1F23;
            border-radius: 6px;
            color: #E2E2E6;
            padding: 4px;
        }
        QListWidget::item {
            padding: 4px;
            border-bottom: 1px solid #1F1F23;
        }
        QListWidget::item:selected {
            background-color: #2B3D52;
            color: #FFFFFF;
        }
        
        /* Progress Bar */
        QProgressBar {
            background-color: #1A1A1E;
            border: 1px solid #2A2A30;
            border-radius: 4px;
            text-align: center;
            color: #FFFFFF;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #2ECC71;
            border-radius: 3px;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            border: none;
            background: #16161a;
            width: 10px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #2C2C35;
            min-height: 20px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical:hover {
            background: #3A3A45;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

