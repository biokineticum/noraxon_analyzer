import os
import pandas as pd
import numpy as np

from filter_utils import FilterWidget, apply_filter, calculate_contact_time

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QComboBox, QLineEdit, 
                               QGroupBox, QFormLayout, QMessageBox, QCheckBox, QListWidget)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

G_TO_MPS2 = 9.80665
MILLI_G_TO_MPS2 = G_TO_MPS2 / 1000

def compute_velocity(accel, time):
    dt = np.diff(time)
    vel = np.zeros(len(accel))
    vel[1:] = np.cumsum( (accel[:-1] + accel[1:]) / 2 * dt )
    return vel

class ModuleAir(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.top_peak_indices = []
        self.file_path = ""
        self.saved_events_paths = []
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel - Controls
        control_panel = QWidget()
        control_panel.setFixedWidth(350)
        control_layout = QVBoxLayout(control_panel)
        
        # 1. Load File
        group_load = QGroupBox("1. Load Raw Data (Air)")
        load_layout = QVBoxLayout()
        self.btn_load = QPushButton("Load File (.xlsx, .csv)")
        self.btn_load.clicked.connect(self.load_file)
        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setWordWrap(True)
        
        self.cb_skiprows = QLineEdit("3")
        self.cb_skiprows.setToolTip("Skip first n rows")
        
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
        
        map_layout.addRow("Time:", self.combo_time)
        map_layout.addRow("Accel X:", self.combo_ax)
        map_layout.addRow("Accel Y:", self.combo_ay)
        map_layout.addRow("Accel Z:", self.combo_az)
        
        self.chk_convert_mg = QCheckBox("Convert from mG to m/s²")
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
        group_params = QGroupBox("3. Detection (Acceleration)")
        params_layout = QFormLayout()
        
        # Air usually has high acceleration. Provide a generic default.
        self.inp_accel_thresh = QLineEdit("30.0") 
        self.inp_window = QLineEdit("0.6")
        self.inp_min_sep = QLineEdit("0.5")
        self.inp_num_peaks = QLineEdit("5")
        
        params_layout.addRow("Accel Threshold (m/s²):", self.inp_accel_thresh)
        params_layout.addRow("Window Size (s):", self.inp_window)
        params_layout.addRow("Min Separation (s):", self.inp_min_sep)
        params_layout.addRow("Num Peaks:", self.inp_num_peaks)
        
        group_params.setLayout(params_layout)
        control_layout.addWidget(group_params)
        
        # 4. Actions
        group_actions = QGroupBox("4. Cut & Analyze")
        actions_layout = QVBoxLayout()
        
        self.btn_calc = QPushButton("Identify & Cut Events")
        self.btn_calc.clicked.connect(self.calculate_and_cut)
        self.btn_calc.setEnabled(False)
        self.btn_calc.setStyleSheet("background-color: #E67E22; color: white; font-weight: bold;")
        
        actions_layout.addWidget(self.btn_calc)
        
        self.list_events = QListWidget()
        self.list_events.itemClicked.connect(self.on_event_clicked)
        actions_layout.addWidget(QLabel("Detected events (click to analyze):"))
        actions_layout.addWidget(self.list_events)
        
        group_actions.setLayout(actions_layout)
        control_layout.addWidget(group_actions)
        
        # Summary text
        self.lbl_summary = QLabel("")
        self.lbl_summary.setTextInteractionFlags(Qt.TextSelectableByMouse)
        control_layout.addWidget(self.lbl_summary)
        
        control_layout.addStretch()
        
        # Right Panel - Plots
        plot_panel = QWidget()
        plot_layout = QVBoxLayout(plot_panel)
        
        self.figure = Figure(figsize=(8, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(plot_panel, stretch=1)

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
            
        columns = list(self.data.columns)
        combos = [self.combo_time, self.combo_ax, self.combo_ay, self.combo_az]
                  
        for combo in combos:
            combo.clear()
            combo.addItems(["--- None ---"] + columns)
            
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
                
        self.filter_widget.update_preview_signals(columns)
                
        self.btn_calc.setEnabled(True)
        self.list_events.clear()
        self.saved_events_paths = []
        QMessageBox.information(self, "Success", f"Loaded {len(self.data)} rows.")

    def get_preview_data(self):
        if self.data is None:
            return None, None, []
        time_col = self.combo_time.currentText()
        if time_col == "--- None ---":
            return None, None, []
        return self.data.copy(), time_col, list(self.data.columns)

    def calculate_and_cut(self):
        if self.data is None:
            return
            
        time_col = self.combo_time.currentText()
        ax_col = self.combo_ax.currentText()
        ay_col = self.combo_ay.currentText()
        az_col = self.combo_az.currentText()
        
        if time_col == "--- None ---" or ax_col == "--- None ---" or ay_col == "--- None ---" or az_col == "--- None ---":
            QMessageBox.warning(self, "Warning", "You must select the Time column and Acceleration X, Y, Z columns.")
            return
                    try:
            accel_thresh = float(self.inp_accel_thresh.text())
            window_size = float(self.inp_window.text())
            min_sep = float(self.inp_min_sep.text())
            num_peaks = int(self.inp_num_peaks.text())
            
            df = self.data.copy()
            columns = list(df.columns)
            
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
                
            df['Time'] = df[time_col]
            
            # Apply Filter
            f_set = self.filter_widget.get_filter_settings()
            if f_set["type"] != "None":
                t_arr = df['Time'].values
                if ax_col != "--- None ---" and ay_col != "--- None ---" and az_col != "--- None ---":
                    df['ax'] = apply_filter(df['ax'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    df['ay'] = apply_filter(df['ay'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    df['az'] = apply_filter(df['az'].values, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                
            df['resultant_acceleration'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
            
            # Auto-detect force columns if present
            fx_col = next((c for c in columns if 'force' in c.lower() and 'fx' in c.lower()), None)
            fy_col = next((c for c in columns if 'force' in c.lower() and 'fy' in c.lower()), None)
            fz_col = next((c for c in columns if 'force' in c.lower() and 'fz' in c.lower()), None)
            
            has_force_raw = (fx_col is not None) and (fy_col is not None) and (fz_col is not None)
            if has_force_raw:
                fx_vals = df[fx_col].values
                fy_vals = df[fy_col].values
                fz_vals = df[fz_col].values
                
                if f_set["type"] != "None":
                    t_arr = df['Time'].values
                    fx_vals = apply_filter(fx_vals, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    fy_vals = apply_filter(fy_vals, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    fz_vals = apply_filter(fz_vals, t_arr, f_set["type"], f_set["param1"], f_set["param2"])
                    
                df['resultant_force'] = np.sqrt(fx_vals**2 + fy_vals**2 + fz_vals**2)
            
            # Find peaks based on ACCELERATION
            valid_data = df[df['resultant_acceleration'] >= accel_thresh]
            sorted_data = valid_data.sort_values(by='resultant_acceleration', ascending=False)
            
            top_peaks = []
            for index, row in sorted_data.iterrows():
                if len(top_peaks) >= num_peaks:
                    break
                time_diffs = [abs(row['Time'] - df['Time'].loc[prev_index]) for prev_index in top_peaks]
                if all(diff >= min_sep for diff in time_diffs):
                    top_peaks.append(index)
                    
            if not top_peaks:
                QMessageBox.warning(self, "No peaks", "No events found above the given threshold.")
                return
                
            self.top_peak_indices = top_peaks
            self.processed_df = df
            self.window_size = window_size
            
            # Cut and Save
            base_dir = os.path.dirname(self.file_path)
            base_name = os.path.splitext(os.path.basename(self.file_path))[0]
            
            self.list_events.clear()
            self.saved_events_paths = []
            
            for i, peak_index in enumerate(self.top_peak_indices):
                peak_time = self.processed_df['Time'].loc[peak_index]
                start_time = peak_time - self.window_size / 2
                end_time = peak_time + self.window_size / 2
                
                event_data = self.processed_df[(self.processed_df['Time'] >= start_time) & (self.processed_df['Time'] <= end_time)].copy()
                
                # If force is available, calculate contact time and store it
                if 'resultant_force' in self.processed_df.columns:
                    contact_time_val = np.nan
                    try:
                        peak_pos = self.processed_df.index.get_loc(peak_index)
                        contact_info = calculate_contact_time(
                            self.processed_df['Time'].values,
                            self.processed_df['resultant_force'].values,
                            peak_pos,
                            threshold=50.0
                        )
                        if contact_info:
                            contact_time_val = contact_info[4]
                    except Exception as e:
                        print(f"Error calculating contact time: {e}")
                    event_data['contact_time_sec'] = contact_time_val
                
                event_file_name = os.path.join(base_dir, f'{base_name}_air_event_{i + 1}.xlsx')
                event_data.to_excel(event_file_name, index=False)
                
                self.saved_events_paths.append(event_file_name)
                self.list_events.addItem(os.path.basename(event_file_name))
                
            # Initial plot of the full signal and peaks
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(df['Time'], df['resultant_acceleration'], label='Resultant Accel', linewidth=0.7, color='#2E86AB')
            
            for idx, peak_idx in enumerate(self.top_peak_indices, 1):
                peak_time = df['Time'].loc[peak_idx]
                ax.plot(peak_time, df['resultant_acceleration'].loc[peak_idx], 'X', markersize=14, 
                         label=f'Peak {idx}', markeredgecolor='black', markeredgewidth=0.8)
                ax.axvspan(peak_time - window_size/2, peak_time + window_size/2, color='red', alpha=0.15)
                
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Resultant Accel (m/s²)')
            ax.set_title(f'Top Accel Peaks ({len(top_peaks)} found)')
            ax.legend(loc='upper right')
            ax.grid(True, alpha=0.3)
            self.figure.tight_layout()
            self.canvas.draw()
            
            QMessageBox.information(self, "Success", f"Saved {len(self.saved_events_paths)} events. Click an event in the list to view its velocity analysis.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Wystąpił błąd:\n{str(e)}")

    def on_event_clicked(self, item):
        row = self.list_events.row(item)
        file_path = self.saved_events_paths[row]
        
        try:
            df = pd.read_excel(file_path)
            
            # Extract data
            time_vals = df['Time'].values
            ax_vals = df['ax'].values
            ay_vals = df['ay'].values
            az_vals = df['az'].values
            
            # Compute velocities
            df['vel_x'] = compute_velocity(ax_vals, time_vals)
            df['vel_y'] = compute_velocity(ay_vals, time_vals)
            df['vel_z'] = compute_velocity(az_vals, time_vals)
            df['vel_resultant'] = np.sqrt(df['vel_x']**2 + df['vel_y']**2 + df['vel_z']**2)
            
            has_force = 'resultant_force' in df.columns
            contact_time_val = None
            start_time = None
            end_time = None
            peak_time = None
            peak_force = None
            
            if has_force:
                max_force_idx = df['resultant_force'].idxmax()
                peak_time = df['Time'].loc[max_force_idx]
                peak_force = df['resultant_force'].loc[max_force_idx]
                
                if 'contact_time_sec' in df.columns:
                    non_nan = df['contact_time_sec'].dropna()
                    if not non_nan.empty:
                        contact_time_val = non_nan.iloc[0]
                        
                try:
                    peak_pos = df.index.get_loc(max_force_idx)
                    contact_info = calculate_contact_time(df['Time'].values, df['resultant_force'].values, peak_pos, threshold=50.0)
                    if contact_info:
                        _, _, start_time, end_time, calculated_ct = contact_info
                        if contact_time_val is None or np.isnan(contact_time_val):
                            contact_time_val = calculated_ct
                except Exception as e:
                    print(f"Error calculating contact time: {e}")

            # Summary report
            max_vx = df['vel_x'].max()
            max_vy = df['vel_y'].max()
            max_vz = df['vel_z'].max()
            max_res = df['vel_resultant'].max()
            
            summary_text = (
                f"=== RAPORT ZDARZENIA {row+1} ===\n"
                f"Max vel_x: {max_vx:.2f} m/s\n"
                f"Max vel_y: {max_vy:.2f} m/s\n"
                f"Max vel_z: {max_vz:.2f} m/s\n"
                f"MAX RESULTANT: {max_res:.2f} m/s\n"
            )
            if contact_time_val is not None and not np.isnan(contact_time_val):
                summary_text += f"Czas kontaktu z tarczą: {contact_time_val:.3f} s\n"
                
            self.lbl_summary.setText(summary_text)
            
            # Plot
            self.figure.clear()
            num_plots = 5 if has_force else 4
            axes = self.figure.subplots(num_plots, 1, sharex=True)
            
            curr_idx = 0
            if has_force:
                axes[curr_idx].plot(df['Time'], df['resultant_force'], color='#E74C3C', linewidth=1.5)
                axes[curr_idx].set_ylabel('Force (N)')
                axes[curr_idx].axvline(peak_time, color='gray', linestyle='--', alpha=0.7)
                axes[curr_idx].plot(peak_time, peak_force, marker='o', markersize=10, markerfacecolor='gold', markeredgecolor='black')
                axes[curr_idx].text(peak_time + 0.01, peak_force, f'Max Force\n{peak_force:.0f} N', color='#E74C3C', fontweight='bold', va='top')
                
                # Show threshold and contact line on plot
                axes[curr_idx].axhline(50, color='gray', linestyle='--', alpha=0.5)
                if start_time is not None and end_time is not None and contact_time_val is not None:
                    axes[curr_idx].plot([start_time, end_time], [50, 50], color='green', linewidth=2.5, marker='|')
                    axes[curr_idx].axvline(start_time, color='green', linestyle=':', alpha=0.6)
                    axes[curr_idx].axvline(end_time, color='green', linestyle=':', alpha=0.6)
                    axes[curr_idx].text((start_time + end_time)/2, 60, f"Kontakt: {contact_time_val:.3f}s", color='green', fontweight='bold', ha='center', va='bottom')
                axes[curr_idx].grid(True, alpha=0.3)
                axes[curr_idx].set_title(f'Event {row+1} - Force & Velocity Components', fontweight='bold')
                curr_idx += 1
                
            axes[curr_idx].plot(df['Time'], df['vel_x'], color='#E74C3C', linewidth=1.3)
            axes[curr_idx].set_ylabel('Vel X (m/s)')
            axes[curr_idx].grid(True, alpha=0.3)
            if not has_force:
                axes[curr_idx].set_title(f'Velocity Components - Event {row+1}')
            curr_idx += 1
            
            axes[curr_idx].plot(df['Time'], df['vel_y'], color='#3498DB', linewidth=1.3)
            axes[curr_idx].set_ylabel('Vel Y (m/s)')
            axes[curr_idx].grid(True, alpha=0.3)
            curr_idx += 1
            
            axes[curr_idx].plot(df['Time'], df['vel_z'], color='#2ECC71', linewidth=1.3)
            axes[curr_idx].set_ylabel('Vel Z (m/s)')
            axes[curr_idx].grid(True, alpha=0.3)
            curr_idx += 1
            
            axes[curr_idx].plot(df['Time'], df['vel_resultant'], color='#9B59B6', linewidth=1.6)
            axes[curr_idx].fill_between(df['Time'], df['vel_resultant'], alpha=0.15, color='#9B59B6')
            axes[curr_idx].set_ylabel('Resultant (m/s)')
            axes[curr_idx].set_xlabel('Time (s)')
            axes[curr_idx].grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to analyze event:\n{str(e)}")
