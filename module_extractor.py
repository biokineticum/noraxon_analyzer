import os
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

from filter_utils import FilterWidget, apply_filter, calculate_contact_time

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QComboBox, QLineEdit, 
                               QGroupBox, QFormLayout, QMessageBox, QCheckBox, QSlider)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

G_TO_MPS2 = 9.80665
MILLI_G_TO_MPS2 = G_TO_MPS2 / 1000

class ModuleExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.top_peak_indices = []
        self.file_path = ""
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel - Controls
        control_panel = QWidget()
        control_panel.setFixedWidth(350)
        control_layout = QVBoxLayout(control_panel)
        
        # 1. Load File
        group_load = QGroupBox("1. Select Data File")
        load_layout = QVBoxLayout()
        self.btn_load = QPushButton("Load File (.xlsx, .csv)")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setWordWrap(True)
        
        self.cb_skiprows = QLineEdit("3")
        self.cb_skiprows.setToolTip("Skip first n rows (default 3 for Noraxon/Ultium)")
        load_layout.addWidget(self.btn_load)
        load_layout.addWidget(self.lbl_file)
        
        skip_layout = QHBoxLayout()
        skip_layout.addWidget(QLabel("Skip rows:"))
        skip_layout.addWidget(self.cb_skiprows)
        load_layout.addLayout(skip_layout)
        
        group_load.setLayout(load_layout)
        control_layout.addWidget(group_load)
        
        # 2. Column Mapping
        group_map = QGroupBox("2. Column Mapping")
        map_layout = QFormLayout()
        
        self.combo_time = QComboBox()
        self.combo_ax = QComboBox()
        self.combo_ay = QComboBox()
        self.combo_az = QComboBox()
        self.combo_fx = QComboBox()
        self.combo_fy = QComboBox()
        self.combo_fz = QComboBox()
        
        map_layout.addRow("Time:", self.combo_time)
        map_layout.addRow("Accel X:", self.combo_ax)
        map_layout.addRow("Accel Y:", self.combo_ay)
        map_layout.addRow("Accel Z:", self.combo_az)
        map_layout.addRow("Force X:", self.combo_fx)
        map_layout.addRow("Force Y:", self.combo_fy)
        map_layout.addRow("Force Z:", self.combo_fz)
        
        self.chk_convert_mg = QCheckBox("Convert Accel from mG to m/s²")
        self.chk_convert_mg.setChecked(True)
        map_layout.addRow(self.chk_convert_mg)
        
        group_map.setLayout(map_layout)
        control_layout.addWidget(group_map)
        
        # 2.5 Data Filtering
        group_filter = QGroupBox("2.5 Data Filtering")
        filter_layout = QVBoxLayout()
        self.filter_widget = FilterWidget()
        self.filter_widget.get_data_callback = self.get_preview_data
        filter_layout.addWidget(self.filter_widget)
        group_filter.setLayout(filter_layout)
        control_layout.addWidget(group_filter)
        
        # 3. Parameters
        group_params = QGroupBox("3. Detection Parameters (Force Plate)")
        params_layout = QFormLayout()
        
        self.inp_force_thresh = QLineEdit("400")
        self.inp_window = QLineEdit("0.6")
        self.inp_min_sep = QLineEdit("0.5")
        self.inp_num_peaks = QLineEdit("5")
        
        params_layout.addRow("Impact Force Thresh (N):", self.inp_force_thresh)
        params_layout.addRow("Window Size (s):", self.inp_window)
        params_layout.addRow("Min Separation (s):", self.inp_min_sep)
        params_layout.addRow("Num Peaks:", self.inp_num_peaks)
        
        slider_layout = QHBoxLayout()
        self.lbl_contact_thresh = QLabel("50")
        self.slider_contact_thresh = QSlider(Qt.Horizontal)
        self.slider_contact_thresh.setRange(0, 100)
        self.slider_contact_thresh.setValue(50)
        self.slider_contact_thresh.valueChanged.connect(self.update_thresh_label)
        slider_layout.addWidget(self.slider_contact_thresh)
        slider_layout.addWidget(self.lbl_contact_thresh)
        params_layout.addRow("Contact Time Thresh (N):", slider_layout)
        
        group_params.setLayout(params_layout)
        control_layout.addWidget(group_params)
        
        # 4. Actions
        group_actions = QGroupBox("4. Calculation & Export")
        actions_layout = QVBoxLayout()
        
        self.btn_calc = QPushButton("Identify Impacts (Calculate & Plot)")
        self.btn_calc.clicked.connect(self.calculate_and_plot)
        self.btn_calc.setEnabled(False)
        
        self.btn_save = QPushButton("Cut Events & Save")
        self.btn_save.clicked.connect(self.save_events)
        self.btn_save.setEnabled(False)
        self.btn_save.setStyleSheet("background-color: #2ECC71; color: white; font-weight: bold;")
        
        actions_layout.addWidget(self.btn_calc)
        actions_layout.addWidget(self.btn_save)
        
        group_actions.setLayout(actions_layout)
        control_layout.addWidget(group_actions)
        
        control_layout.addStretch()
        
        # Right Panel - Plots
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)
        
        self.figure = Figure(figsize=(8, 5))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(plot_panel, stretch=1)

    def update_thresh_label(self, value):
        self.lbl_contact_thresh.setText(str(value))

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return
            
        self.file_path = file_path
        self.lbl_file.setText(os.path.basename(file_path))
        
        skiprows = 0
        try:
            skiprows = int(self.cb_skiprows.text())
        except:
            pass
            
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path, skiprows=skiprows)
            else:
                self.data = pd.read_excel(file_path, skiprows=skiprows)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
            return
            
        # Update combo boxes
        columns = list(self.data.columns)
        combos = [self.combo_time, self.combo_ax, self.combo_ay, self.combo_az, 
                  self.combo_fx, self.combo_fy, self.combo_fz]
                  
        for combo in combos:
            combo.clear()
            combo.addItems(["--- None ---"] + columns)
            
        self.filter_widget.update_preview_signals(columns)
            
        # Auto-guess columns based on common names
        for i, col in enumerate(columns):
            col_lower = col.lower()
            if 'time' in col_lower:
                self.combo_time.setCurrentIndex(i + 1)
            elif 'accel' in col_lower and 'x' in col_lower:
                self.combo_ax.setCurrentIndex(i + 1)
            elif 'accel' in col_lower and 'y' in col_lower:
                self.combo_ay.setCurrentIndex(i + 1)
            elif 'accel' in col_lower and 'z' in col_lower:
                self.combo_az.setCurrentIndex(i + 1)
            elif 'force' in col_lower and 'fx' in col_lower:
                self.combo_fx.setCurrentIndex(i + 1)
            elif 'force' in col_lower and 'fy' in col_lower:
                self.combo_fy.setCurrentIndex(i + 1)
            elif 'force' in col_lower and 'fz' in col_lower:
                self.combo_fz.setCurrentIndex(i + 1)
                
        self.btn_calc.setEnabled(True)
        QMessageBox.information(self, "Success", f"Successfully loaded file. Found {len(self.data)} rows.")

    def get_preview_data(self):
        if self.data is None:
            return None, None, []
        time_col = self.combo_time.currentText()
        if time_col == "--- None ---":
            return None, None, []
        return self.data.copy(), time_col, list(self.data.columns)

    def calculate_and_plot(self):
        if self.data is None:
            return
            
        time_col = self.combo_time.currentText()
        ax_col = self.combo_ax.currentText()
        ay_col = self.combo_ay.currentText()
        az_col = self.combo_az.currentText()
        fx_col = self.combo_fx.currentText()
        fy_col = self.combo_fy.currentText()
        fz_col = self.combo_fz.currentText()
        
        if time_col == "--- None ---" or fx_col == "--- None ---" or fy_col == "--- None ---" or fz_col == "--- None ---":
            QMessageBox.warning(self, "Warning", "You must select the Time column and at least Force X, Y, Z columns.")
            return
            
        try:
            # Parse parameters
            force_thresh = float(self.inp_force_thresh.text())
            window_size = float(self.inp_window.text())
            min_sep = float(self.inp_min_sep.text())
            num_peaks = int(self.inp_num_peaks.text())
            
            # Setup working dataframe
            df = self.data.copy()
            
            # Force mapping
            df['fx'] = df[fx_col]
            df['fy'] = df[fy_col]
            df['fz'] = df[fz_col]
            df['resultant_force'] = np.sqrt(df['fx']**2 + df['fy']**2 + df['fz']**2)
            
            # Accel mapping if provided
            if ax_col != "--- None ---" and ay_col != "--- None ---" and az_col != "--- None ---":
                if self.chk_convert_mg.isChecked():
                    # Przekonwertuj wszystkie kolumny mG w całym dataframe
                    for col in df.columns:
                        if 'mG' in str(col):
                            new_col_name = str(col).replace('mG', 'mps2')
                            try:
                                df[new_col_name] = df[col] * MILLI_G_TO_MPS2
                            except:
                                pass
                                
                    df['ax'] = df[ax_col] * MILLI_G_TO_MPS2
                    df['ay'] = df[ay_col] * MILLI_G_TO_MPS2
                    df['az'] = df[az_col] * MILLI_G_TO_MPS2
                else:
                    df['ax'] = df[ax_col]
                    df['ay'] = df[ay_col]
                    df['az'] = df[az_col]
                df['resultant_acceleration'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
            else:
                df['resultant_acceleration'] = 0.0 # Placeholder
                
            df['Time'] = df[time_col]
            
            # Apply Filter
            f_set = self.filter_widget.get_filter_settings()
            if f_set["type"] != "None":
                t_arr = df['Time'].values
                
                # Filter force
                df['fx'] = apply_filter(df['fx'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                df['fy'] = apply_filter(df['fy'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                df['fz'] = apply_filter(df['fz'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                df['resultant_force'] = np.sqrt(df['fx']**2 + df['fy']**2 + df['fz']**2)
                
                # Filter accel if present
                if ax_col != "--- None ---" and ay_col != "--- None ---" and az_col != "--- None ---":
                    df['ax'] = apply_filter(df['ax'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    df['ay'] = apply_filter(df['ay'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    df['az'] = apply_filter(df['az'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    df['resultant_acceleration'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
            
            # Find peaks (logic from notebook)
            valid_data = df[df['resultant_force'] >= force_thresh]
            sorted_data = valid_data.sort_values(by='resultant_force', ascending=False)
            
            top_peaks = []
            for index, row in sorted_data.iterrows():
                if len(top_peaks) >= num_peaks:
                    break
                time_diffs = [abs(row['Time'] - df['Time'].loc[prev_index]) for prev_index in top_peaks]
                if all(diff >= min_sep for diff in time_diffs):
                    top_peaks.append(index)
                    
            self.top_peak_indices = top_peaks
            self.processed_df = df
            self.window_size = window_size
                        # Plot
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            
            ax.plot(df['Time'], df['resultant_force'], label='Resultant Force', linewidth=0.7, color='#2E86AB')
            thresh_val = float(self.slider_contact_thresh.value())
            ax.axhline(thresh_val, color='gray', linestyle='--', alpha=0.5, label=f'Threshold {thresh_val} N')
            
            for idx, peak_idx in enumerate(self.top_peak_indices, 1):
                peak_time = df['Time'].loc[peak_idx]
                ax.plot(peak_time, df['resultant_force'].loc[peak_idx], 'X', markersize=14, 
                         label=f'Peak {idx}', markeredgecolor='black', markeredgewidth=0.8)
                ax.axvspan(peak_time - window_size/2, peak_time + window_size/2, color='red', alpha=0.15)
                
                # Contact time calculation and display
                try:
                    peak_pos = df.index.get_loc(peak_idx)
                    contact_info = calculate_contact_time(df['Time'].values, df['resultant_force'].values, peak_pos, threshold=thresh_val)
                    if contact_info:
                        start_idx, end_idx, start_time, end_time, contact_time = contact_info
                        # Plot horizontal green line at thresh_val N
                        ax.plot([start_time, end_time], [thresh_val, thresh_val], color='green', linewidth=2.5, marker='|')
                        # Vertical dotted lines
                        ax.axvline(start_time, color='green', linestyle=':', alpha=0.6)
                        ax.axvline(end_time, color='green', linestyle=':', alpha=0.6)
                        # Text annotation above the line
                        ax.text((start_time + end_time)/2, 60, f"{contact_time:.3f}s", color='green', fontweight='bold', ha='center', va='bottom')
                except Exception as e:
                    print(f"Error drawing contact time for peak {idx}: {e}")
                
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Resultant Force (N)')
            ax.set_title(f'Absolute Top Force Peaks ({len(top_peaks)} found)')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            self.figure.tight_layout()
            self.canvas.draw()
            
            self.btn_save.setEnabled(len(top_peaks) > 0)
            
            msg = f"Found {len(top_peaks)} peaks.\nThey have been marked on the plot."
            if len(self.top_peak_indices) > 0:
                msg += "\n\nContact Times (Czas kontaktu):\n"
                for idx, peak_idx in enumerate(self.top_peak_indices, 1):
                    try:
                        peak_pos = df.index.get_loc(peak_idx)
                        contact_info = calculate_contact_time(df['Time'].values, df['resultant_force'].values, peak_pos, threshold=float(self.slider_contact_thresh.value()))
                        if contact_info:
                            msg += f"Peak {idx}: {contact_info[4]:.3f} s\n"
                    except:
                        pass
                        
            QMessageBox.information(self, "Analysis Complete", msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred during analysis:\n{str(e)}")
 
    def save_events(self):
        if not hasattr(self, 'processed_df') or not self.top_peak_indices:
            return
            
        try:
            base_dir = os.path.dirname(self.file_path)
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            
            saved_files = []
            for i, peak_index in enumerate(self.top_peak_indices):
                peak_time = self.processed_df['Time'].loc[peak_index]
                start_time = peak_time - self.window_size / 2
                end_time = peak_time + self.window_size / 2
                
                # Extract event (including all original columns plus the new mapped ones)
                event_data = self.processed_df[(self.processed_df['Time'] >= start_time) & (self.processed_df['Time'] <= end_time)].copy()
                
                # Calculate contact time on full data
                contact_time_val = np.nan
                try:
                    peak_pos = self.processed_df.index.get_loc(peak_index)
                    contact_info = calculate_contact_time(
                        self.processed_df['Time'].values, 
                        self.processed_df['resultant_force'].values, 
                        peak_pos,
                        threshold=float(self.slider_contact_thresh.value())
                    )
                    if contact_info:
                        contact_time_val = contact_info[4]
                except Exception as e:
                    print(f"Error calculating contact time in save: {e}")
                
                event_data['contact_time_sec'] = contact_time_val
                
                event_file_name = os.path.join(base_dir, f'{base_name}_event_{i + 1}.xlsx')
                event_data.to_excel(event_file_name, index=False)
                saved_files.append(os.path.basename(event_file_name))
                
            msg = f"Successfully cut and saved {len(saved_files)} events in the target folder:\n" + "\n".join(saved_files)
            QMessageBox.information(self, "Success", msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save events:\n{str(e)}")
