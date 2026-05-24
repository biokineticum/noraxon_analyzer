import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, savgol_filter

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QComboBox, QLineEdit, QFormLayout, 
                               QCheckBox, QDialog, QMessageBox)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

def apply_filter(data, time_col, filter_type, param1, param2=None):
    """
    Applies the selected filter to a 1D numpy array `data`.
    time_col is a 1D numpy array of time values (in seconds) to compute fs.
    """
    if filter_type == "None" or len(data) < 10:
        return data
        
    # Calculate sampling frequency fs
    dt = np.mean(np.diff(time_col))
    if dt <= 0:
        return data # Invalid time column
    fs = 1.0 / dt

    try:
        if "Butterworth" in filter_type:
            order = int(param2)
            nyq = 0.5 * fs
            
            if filter_type == "Butterworth Lowpass":
                cutoff = float(param1)
                normal_cutoff = cutoff / nyq
                b, a = butter(order, normal_cutoff, btype='low', analog=False)
                return filtfilt(b, a, data)
                
            elif filter_type == "Butterworth Highpass":
                cutoff = float(param1)
                normal_cutoff = cutoff / nyq
                b, a = butter(order, normal_cutoff, btype='high', analog=False)
                return filtfilt(b, a, data)
                
            elif filter_type == "Butterworth Bandpass":
                # param1 is expected to be "low,high" e.g. "10,50"
                low_cut, high_cut = map(float, param1.split(','))
                low = low_cut / nyq
                high = high_cut / nyq
                b, a = butter(order, [low, high], btype='band', analog=False)
                return filtfilt(b, a, data)
                
        elif filter_type == "Savitzky-Golay":
            window = int(param1)
            polyorder = int(param2)
            if window % 2 == 0:
                window += 1 # Window must be odd
            if window > len(data):
                window = len(data) - 1 if (len(data) - 1) % 2 != 0 else len(data) - 2
            if window <= polyorder:
                return data
            return savgol_filter(data, window_length=window, polyorder=polyorder)
            
        elif filter_type == "Moving Average":
            window = int(param1)
            if window < 2:
                return data
            return pd.Series(data).rolling(window=window, center=True, min_periods=1).mean().values
            
    except Exception as e:
        print(f"Filter error: {e}")
        return data # Return original on failure
        
    return data

class FilterPreviewDialog(QDialog):
    def __init__(self, original_data, filtered_data, time_data, signal_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Filter Preview: {signal_name}")
        self.resize(800, 500)
        
        layout = QVBoxLayout(self)
        
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        ax = self.figure.add_subplot(111)
        ax.plot(time_data, original_data, label='Original', color='lightgray', alpha=0.8, linewidth=1.5)
        ax.plot(time_data, filtered_data, label='Filtered', color='#E74C3C', linewidth=1.5)
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        ax.set_title(f"Original vs Filtered: {signal_name}")
        ax.legend()
        ax.grid(True, alpha=0.3)
        self.figure.tight_layout()

class FilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.get_data_callback = None # Should return (df, time_col_name, selected_signals_list)
        self.init_ui()
        
    def init_ui(self):
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.chk_enable = QCheckBox("Enable Filtering")
        self.chk_enable.setChecked(False)
        self.chk_enable.stateChanged.connect(self.toggle_inputs)
        layout.addRow(self.chk_enable)
        
        self.combo_type = QComboBox()
        self.combo_type.addItems([
            "Butterworth Lowpass", 
            "Butterworth Highpass", 
            "Butterworth Bandpass", 
            "Savitzky-Golay", 
            "Moving Average"
        ])
        self.combo_type.currentIndexChanged.connect(self.update_labels)
        layout.addRow("Filter Type:", self.combo_type)
        
        self.lbl_param1 = QLabel("Cutoff Freq (Hz):")
        self.inp_param1 = QLineEdit("50.0")
        layout.addRow(self.lbl_param1, self.inp_param1)
        
        self.lbl_param2 = QLabel("Order:")
        self.inp_param2 = QLineEdit("4")
        layout.addRow(self.lbl_param2, self.inp_param2)
        
        self.combo_signal_preview = QComboBox()
        layout.addRow("Signal to Preview:", self.combo_signal_preview)
        
        self.btn_preview = QPushButton("Preview Filter")
        self.btn_preview.clicked.connect(self.show_preview)
        layout.addRow("", self.btn_preview)
        
        self.toggle_inputs()
        
    def toggle_inputs(self):
        enabled = self.chk_enable.isChecked()
        self.combo_type.setEnabled(enabled)
        self.inp_param1.setEnabled(enabled)
        self.inp_param2.setEnabled(enabled)
        self.combo_signal_preview.setEnabled(enabled)
        self.btn_preview.setEnabled(enabled)
        
    def update_labels(self):
        ftype = self.combo_type.currentText()
        if ftype in ["Butterworth Lowpass", "Butterworth Highpass"]:
            self.lbl_param1.setText("Cutoff Freq (Hz):")
            self.inp_param1.setPlaceholderText("e.g. 50")
            self.lbl_param2.setText("Order:")
            self.lbl_param2.show()
            self.inp_param2.show()
        elif ftype == "Butterworth Bandpass":
            self.lbl_param1.setText("Low,High Cutoff (Hz):")
            self.inp_param1.setPlaceholderText("e.g. 10,50")
            self.lbl_param2.setText("Order:")
            self.lbl_param2.show()
            self.inp_param2.show()
        elif ftype == "Savitzky-Golay":
            self.lbl_param1.setText("Window Size (samples):")
            self.inp_param1.setPlaceholderText("e.g. 51")
            self.lbl_param2.setText("Polynomial Order:")
            self.lbl_param2.show()
            self.inp_param2.show()
            self.inp_param2.setText("3")
        elif ftype == "Moving Average":
            self.lbl_param1.setText("Window Size (samples):")
            self.inp_param1.setPlaceholderText("e.g. 10")
            self.lbl_param2.hide()
            self.inp_param2.hide()
            
    def update_preview_signals(self, signals):
        self.combo_signal_preview.clear()
        self.combo_signal_preview.addItems(signals)
        
    def get_filter_settings(self):
        if not self.chk_enable.isChecked():
            return {"type": "None"}
        return {
            "type": self.combo_type.currentText(),
            "param1": self.inp_param1.text(),
            "param2": self.inp_param2.text() if not self.inp_param2.isHidden() else None
        }
        
    def show_preview(self):
        if not self.get_data_callback:
            QMessageBox.warning(self, "Error", "Preview callback not set.")
            return
            
        df, time_col_name, selected_signals = self.get_data_callback()
        if df is None or time_col_name not in df.columns:
            QMessageBox.warning(self, "Error", "Please select valid time and signal columns first.")
            return
            
        signal_to_preview = self.combo_signal_preview.currentText()
        if not signal_to_preview or signal_to_preview not in df.columns:
            QMessageBox.warning(self, "Error", f"Signal '{signal_to_preview}' not found in data.")
            return
            
        settings = self.get_filter_settings()
        if settings["type"] == "None":
            return
            
        time_data = df[time_col_name].values
        original_data = df[signal_to_preview].values
        
        filtered_data = apply_filter(original_data, time_data, settings["type"], settings["param1"], settings["param2"])
        
        dialog = FilterPreviewDialog(original_data, filtered_data, time_data, signal_to_preview, self)
        dialog.exec()
