import os
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

from filter_utils import calculate_contact_time

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QFileDialog, QLineEdit, QGroupBox, 
                               QFormLayout, QMessageBox, QCheckBox, QTableWidget, 
                               QTableWidgetItem, QProgressBar, QListWidget, QSplitter, QSlider)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor

G_TO_MPS2 = 9.80665
MILLI_G_TO_MPS2 = G_TO_MPS2 / 1000

# Mappings of column names from Dane dollio.xlsx
COLUMNS_FORMAT = [
    'zawodnik', 'plec', 'wiek', 'masa', 'wysokość ciała', 'rodzaj uderzenia', 'nr uderzenia',
    '1Velocity X m/s', '1Velocity Y m/s', '1Velocity Z m/s', '1Resultant Velocity m/s',
    '1Acceleration X m/s2', '1Acceleration Y m/s2', '1Acceleration Z m/s2', '1Resultant Acceleration',
    '1Max Force (Resultant)', '1Max vel_x m/s', '1Max vel_y m/s', '1Max vel_z m/s', '1MAX Resultant m/s',
    '2Velocity X m/s', '2Velocity Y m/s', '2Velocity Z m/s', '2Resultant Velocity m/s',
    '2Acceleration X m/s2', '2Acceleration Y m/s2', '2Acceleration Z m/s2', '2Resultant Acceleration',
    '2Max Force (Resultant)', '2Max vel_x m/s', '2Max vel_y m/s', '2Max vel_z m/s', '2MAX Resultant m/s',
    '3Velocity X m/s', '3Velocity Y m/s', '3Velocity Z m/s', '3Resultant Velocity m/s',
    '3Acceleration X m/s2', '3Acceleration Y m/s2', '3Acceleration Z m/s2', '3Resultant Acceleration',
    '3Max Force (Resultant)', '3Max vel_x m/s', '3Max vel_y m/s', '3Max vel_z m/s', '3MAX Resultant m/s',
    'Czas kontaktu z tarczą (s)'
]

# Columns that can be edited by the user in the table
EDITABLE_COLUMNS = ['zawodnik', 'plec', 'wiek', 'masa', 'wysokość ciała', 'rodzaj uderzenia']

def apply_butter_lowpass(data, fs, cutoff=50.0, order=4):
    if len(data) < 10:
        return data
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def compute_velocity(accel, time):
    dt = np.diff(time)
    vel = np.zeros(len(accel))
    vel[1:] = np.cumsum((accel[:-1] + accel[1:]) / 2 * dt)
    return vel

def guess_athlete_and_kick(filename):
    name_without_ext = os.path.splitext(filename)[0]
    name_lower = name_without_ext.lower()
    
    # Guess side (L/P)
    side = "Dollio_L"
    if "prawa" in name_lower or "prawy" in name_lower or "_p" in name_lower or "right" in name_lower:
        side = "Dollio_P"
    elif "lewa" in name_lower or "lewy" in name_lower or "_l" in name_lower or "left" in name_lower:
        side = "Dollio_L"
        
    # Guess athlete name based on typical names in Polish or English
    known_players = {
        "zdzislaw": "Zdzisław Synoradzki",
        "zdzisław": "Zdzisław Synoradzki",
        "rafal": "Rafał Magryś",
        "rafał": "Rafał Magryś",
        "przemyslaw": "Przemysław Mruk",
        "przemysław": "Przemysław Mruk",
        "andrzej": "Andrzej Chomiuk",
        "antonina": "Antonina Dudek"
    }
    
    athlete = "Nieznany"
    for key, fullname in known_players.items():
        if key in name_lower:
            athlete = fullname
            break
            
    if athlete == "Nieznany":
        # Clean up common words to guess name
        words = name_without_ext.split()
        clean_words = []
        for w in words:
            wl = w.lower()
            if wl in ["lewa", "prawa", "tarcza", "tarczy", "uderzenie", "kopnięcie", "kopniecie", "air", "inertial", "event", "sport", "sync", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
                continue
            if any(c.isdigit() for c in w) or '-' in w or '.' in w or '_' in w:
                continue
            clean_words.append(w)
        if clean_words:
            athlete = " ".join(clean_words).title()
        else:
            athlete = name_without_ext.title()
            
    return athlete, side

def detect_sensor_prefixes(columns):
    """
    Scans list of columns to find all prefixes for accelerometer channels.
    E.g. finding 'Ultium EMG.Accel 1', 'Ultium EMG.Accel 4', 'Ultium EMG.Accel 5'
    """
    accel_cols = [col for col in columns if 'accel' in col.lower()]
    prefixes = set()
    for col in accel_cols:
        col_lower = col.lower()
        for suffix in [' x', ' y', ' z', 'x,', 'y,', 'z,']:
            if suffix in col_lower:
                idx = col_lower.rfind(suffix)
                prefixes.add(col[:idx].strip())
                break
    return sorted(list(prefixes))

class AnalysisWorker(QThread):
    progress = Signal(int)
    log_message = Signal(str)
    finished = Signal(list, str)
    
    def __init__(self, files, params):
        super().__init__()
        self.files = files
        self.params = params
        
    def run(self):
        results = []
        try:
            num_files = len(self.files)
            for file_idx, file_path in enumerate(self.files):
                self.log_message.emit(f"Przetwarzanie pliku: {os.path.basename(file_path)}...")
                
                # Check for cancel or other thread triggers if needed
                athlete, side = guess_athlete_and_kick(os.path.basename(file_path))
                
                skiprows = self.params['skiprows']
                df_raw = pd.read_excel(file_path, skiprows=skiprows)
                
                # Identify columns
                columns = list(df_raw.columns)
                time_col = next((c for c in columns if 'time' in c.lower()), None)
                fx_col = next((c for c in columns if 'force' in c.lower() and 'fx' in c.lower()), None)
                fy_col = next((c for c in columns if 'force' in c.lower() and 'fy' in c.lower()), None)
                fz_col = next((c for c in columns if 'force' in c.lower() and 'fz' in c.lower()), None)
                
                if not time_col or not fx_col or not fy_col or not fz_col:
                    self.log_message.emit(f"Błąd: Brak kolumny Czasu lub Siły X/Y/Z w pliku {os.path.basename(file_path)}!")
                    continue
                
                # Calculate fs (sampling frequency)
                time_vals = df_raw[time_col].values
                dt = np.mean(np.diff(time_vals))
                fs = 1.0 / dt if dt > 0 else 1000.0
                
                # Filter Force
                fx_raw = df_raw[fx_col].values
                fy_raw = df_raw[fy_col].values
                fz_raw = df_raw[fz_col].values
                
                if self.params['enable_filter']:
                    fx_filt = apply_butter_lowpass(fx_raw, fs, self.params['cutoff'], self.params['order'])
                    fy_filt = apply_butter_lowpass(fy_raw, fs, self.params['cutoff'], self.params['order'])
                    fz_filt = apply_butter_lowpass(fz_raw, fs, self.params['cutoff'], self.params['order'])
                else:
                    fx_filt, fy_filt, fz_filt = fx_raw, fy_raw, fz_raw
                    
                res_force = np.sqrt(fx_filt**2 + fy_filt**2 + fz_filt**2)
                
                # Detect peaks
                force_thresh = self.params['force_thresh']
                min_sep = self.params['min_sep']
                num_peaks = self.params['num_peaks']
                
                valid_indices = np.where(res_force >= force_thresh)[0]
                sorted_indices = sorted(valid_indices, key=lambda idx: res_force[idx], reverse=True)
                
                peaks = []
                for idx in sorted_indices:
                    if len(peaks) >= num_peaks:
                        break
                    if all(abs(time_vals[idx] - time_vals[p]) >= min_sep for p in peaks):
                        peaks.append(idx)
                        
                # Sort peaks chronologically or by force descending?
                # Dane dollio.xlsx sorted descending by peak force. Let's do that!
                peaks = sorted(peaks, key=lambda idx: res_force[idx], reverse=True)
                
                # Detect sensors
                sensors = detect_sensor_prefixes(columns)
                self.log_message.emit(f"Wykryto {len(sensors)} czujników w {os.path.basename(file_path)}: {sensors}")
                
                window_size = self.params['window_size']
                
                for peak_num, peak_idx in enumerate(peaks):
                    peak_time = time_vals[peak_idx]
                    
                    # Slice window
                    start_time = peak_time - window_size / 2
                    end_time = peak_time + window_size / 2
                    window_mask = (time_vals >= start_time) & (time_vals <= end_time)
                    w_time = time_vals[window_mask]
                    w_indices = np.where(window_mask)[0]
                    
                    if len(w_time) < 2:
                        continue
                        
                    peak_rel_idx = np.where(w_indices == peak_idx)[0][0]
                    
                    # Calculate contact time
                    contact_time_val = np.nan
                    try:
                        contact_thresh = self.params.get('contact_thresh', 50.0)
                        contact_info = calculate_contact_time(time_vals, res_force, peak_idx, threshold=contact_thresh)
                        if contact_info:
                            contact_time_val = contact_info[4]
                    except Exception as e:
                        print(f"Error calculating contact time in bulk: {e}")

                    row_dict = {
                        'zawodnik': athlete,
                        'plec': np.nan,
                        'wiek': np.nan,
                        'masa': np.nan,
                        'wysokość ciała': np.nan,
                        'rodzaj uderzenia': side,
                        'nr uderzenia': peak_num + 1,
                        'Czas kontaktu z tarczą (s)': contact_time_val
                    }
                    
                    # Calculate for each sensor (up to 3)
                    for s_idx in range(1, 4):
                        if s_idx - 1 < len(sensors):
                            sensor_prefix = sensors[s_idx - 1]
                            
                            # Find actual column names
                            ax_col = next((c for c in columns if sensor_prefix in c and 'x' in c.lower()), None)
                            ay_col = next((c for c in columns if sensor_prefix in c and 'y' in c.lower()), None)
                            az_col = next((c for c in columns if sensor_prefix in c and 'z' in c.lower()), None)
                            
                            if not ax_col or not ay_col or not az_col:
                                continue
                                
                            ax_vals = df_raw[ax_col].values
                            ay_vals = df_raw[ay_col].values
                            az_vals = df_raw[az_col].values
                            
                            if self.params['convert_mg']:
                                ax_vals = ax_vals * MILLI_G_TO_MPS2
                                ay_vals = ay_vals * MILLI_G_TO_MPS2
                                az_vals = az_vals * MILLI_G_TO_MPS2
                                
                            # Filter acceleration
                            if self.params['enable_filter']:
                                ax_filt = apply_butter_lowpass(ax_vals, fs, self.params['cutoff'], self.params['order'])
                                ay_filt = apply_butter_lowpass(ay_vals, fs, self.params['cutoff'], self.params['order'])
                                az_filt = apply_butter_lowpass(az_vals, fs, self.params['cutoff'], self.params['order'])
                            else:
                                ax_filt, ay_filt, az_filt = ax_vals, ay_vals, az_vals
                                
                            w_ax_filt = ax_filt[window_mask]
                            w_ay_filt = ay_filt[window_mask]
                            w_az_filt = az_filt[window_mask]
                            
                            # Compute velocities
                            w_vx = compute_velocity(w_ax_filt, w_time)
                            w_vy = compute_velocity(w_ay_filt, w_time)
                            w_vz = compute_velocity(w_az_filt, w_time)
                            w_vres = np.sqrt(w_vx**2 + w_vy**2 + w_vz**2)
                            
                            # Acceleration resultant (filtered)
                            res_acc_filt = np.sqrt(ax_filt**2 + ay_filt**2 + az_filt**2)
                            
                            # Populating values
                            row_dict[f'{s_idx}Velocity X m/s'] = round(w_vx[peak_rel_idx], 2)
                            row_dict[f'{s_idx}Velocity Y m/s'] = round(w_vy[peak_rel_idx], 2)
                            row_dict[f'{s_idx}Velocity Z m/s'] = round(w_vz[peak_rel_idx], 2)
                            row_dict[f'{s_idx}Resultant Velocity m/s'] = round(w_vres[peak_rel_idx], 2)
                            
                            # Raw accelerations at peak
                            row_dict[f'{s_idx}Acceleration X m/s2'] = round(ax_vals[peak_idx], 1)
                            row_dict[f'{s_idx}Acceleration Y m/s2'] = round(ay_vals[peak_idx], 1)
                            row_dict[f'{s_idx}Acceleration Z m/s2'] = round(az_vals[peak_idx], 1)
                            
                            # Filtered resultant acceleration
                            row_dict[f'{s_idx}Resultant Acceleration'] = round(res_acc_filt[peak_idx], 1)
                            
                            # Max Force
                            row_dict[f'{s_idx}Max Force (Resultant)'] = int(round(res_force[peak_idx]))
                            
                            # Max velocities in window
                            row_dict[f'{s_idx}Max vel_x m/s'] = round(w_vx.max(), 2)
                            row_dict[f'{s_idx}Max vel_y m/s'] = round(w_vy.max(), 2)
                            row_dict[f'{s_idx}Max vel_z m/s'] = round(w_vz.max(), 2)
                            row_dict[f'{s_idx}MAX Resultant m/s'] = round(w_vres.max(), 2)
                        else:
                            # Fill with NaN/empty for unused sensor slots
                            row_dict[f'{s_idx}Velocity X m/s'] = np.nan
                            row_dict[f'{s_idx}Velocity Y m/s'] = np.nan
                            row_dict[f'{s_idx}Velocity Z m/s'] = np.nan
                            row_dict[f'{s_idx}Resultant Velocity m/s'] = np.nan
                            row_dict[f'{s_idx}Acceleration X m/s2'] = np.nan
                            row_dict[f'{s_idx}Acceleration Y m/s2'] = np.nan
                            row_dict[f'{s_idx}Acceleration Z m/s2'] = np.nan
                            row_dict[f'{s_idx}Resultant Acceleration'] = np.nan
                            row_dict[f'{s_idx}Max Force (Resultant)'] = np.nan
                            row_dict[f'{s_idx}Max vel_x m/s'] = np.nan
                            row_dict[f'{s_idx}Max vel_y m/s'] = np.nan
                            row_dict[f'{s_idx}Max vel_z m/s'] = np.nan
                            row_dict[f'{s_idx}MAX Resultant m/s'] = np.nan
                            
                    results.append(row_dict)
                    
                progress_val = int((file_idx + 1) / num_files * 100)
                self.progress.emit(progress_val)
                
            self.finished.emit(results, "")
        except Exception as e:
            self.finished.emit([], str(e))

class ModuleBulk(QWidget):
    def __init__(self):
        super().__init__()
        self.files = []
        self.results_data = []
        
        self.init_ui()
        
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Left Panel - Controls
        control_panel = QSplitter(Qt.Vertical)
        control_panel.setFixedWidth(360)
        
        # 1. File Selection Group
        group_files = QGroupBox("1. Wybór Plików Wejściowych")
        files_layout = QVBoxLayout()
        
        self.btn_add_files = QPushButton("Dodaj Pliki (.xlsx, .csv)")
        self.btn_add_files.clicked.connect(self.add_files)
        
        self.list_files = QListWidget()
        self.list_files.setSelectionMode(QListWidget.MultiSelection)
        
        self.btn_remove_files = QPushButton("Usuń Zaznaczone Pliki")
        self.btn_remove_files.clicked.connect(self.remove_files)
        files_layout.addWidget(self.btn_add_files)
        files_layout.addWidget(self.list_files)
        files_layout.addWidget(self.btn_remove_files)
        group_files.setLayout(files_layout)
        control_panel.addWidget(group_files)
        
        # 2. Parameters Group
        group_params = QGroupBox("2. Parametry Analizy i Filtracji")
        params_layout = QFormLayout()
        
        self.inp_skiprows = QLineEdit("3")
        self.inp_force_thresh = QLineEdit("400")
        self.inp_window = QLineEdit("0.6")
        self.inp_min_sep = QLineEdit("0.5")
        self.inp_num_peaks = QLineEdit("5")
        
        self.chk_convert_mg = QCheckBox("Konwertuj czujnik z mG na m/s²")
        self.chk_convert_mg.setChecked(True)
        
        self.chk_enable_filter = QCheckBox("Włącz Filtrowanie Sygnałów")
        self.chk_enable_filter.setChecked(True)
        
        self.inp_filter_cutoff = QLineEdit("50.0")
        self.inp_filter_order = QLineEdit("4")
        
        params_layout.addRow("Pomiń wiersze nagłówka:", self.inp_skiprows)
        params_layout.addRow("Próg siły (N):", self.inp_force_thresh)
        params_layout.addRow("Rozmiar okna (s):", self.inp_window)
        params_layout.addRow("Min. separacja (s):", self.inp_min_sep)
        params_layout.addRow("Maks. liczba uderzeń:", self.inp_num_peaks)
        params_layout.addRow(self.chk_convert_mg)
        params_layout.addRow(self.chk_enable_filter)
        params_layout.addRow("Częst. odcięcia (Hz):", self.inp_filter_cutoff)
        params_layout.addRow("Rząd filtru Butterwortha:", self.inp_filter_order)
        
        slider_layout = QHBoxLayout()
        self.lbl_contact_thresh = QLabel("50")
        self.slider_contact_thresh = QSlider(Qt.Horizontal)
        self.slider_contact_thresh.setRange(0, 100)
        self.slider_contact_thresh.setValue(50)
        self.slider_contact_thresh.valueChanged.connect(self.update_thresh_label)
        slider_layout.addWidget(self.slider_contact_thresh)
        slider_layout.addWidget(self.lbl_contact_thresh)
        params_layout.addRow("Próg czasu kontaktu (N):", slider_layout)
        
        group_params.setLayout(params_layout)
        control_panel.addWidget(group_params)
        
        # 3. Actions Group
        group_actions = QGroupBox("3. Operacje")
        actions_layout = QVBoxLayout()
        
        self.btn_run = QPushButton("Uruchom Analizę Zbiorczą")
        self.btn_run.clicked.connect(self.run_bulk_analysis)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setVisible(False)
        
        self.lbl_status = QLabel("Wybierz pliki i kliknij Uruchom.")
        self.lbl_status.setWordWrap(True)
        
        self.btn_export = QPushButton("Eksportuj do Excela (.xlsx)")
        self.btn_export.clicked.connect(self.export_to_excel)
        self.btn_export.setEnabled(False)
        
        actions_layout.addWidget(self.btn_run)
        actions_layout.addWidget(self.progress_bar)
        actions_layout.addWidget(self.lbl_status)
        actions_layout.addWidget(self.btn_export)
        group_actions.setLayout(actions_layout)
        control_panel.addWidget(group_actions)
        
        # Right Panel - Table Results
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        lbl_table = QLabel("Wyniki Analizy Zbiorczej (Pola Zawodnik, Płeć, Wiek, Masa, Wysokość i Rodzaj są edytowalne):")
        lbl_table.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(lbl_table)
        
        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNS_FORMAT))
        self.table.setHorizontalHeaderLabels(COLUMNS_FORMAT)
        self.table.setAlternatingRowColors(True)
        
        # Adjust column sizing
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(110)
        
        right_layout.addWidget(self.table)
        
        main_layout.addWidget(control_panel)
        main_layout.addWidget(right_panel, stretch=1)
        
    def update_thresh_label(self, value):
        self.lbl_contact_thresh.setText(str(value))
        
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Wybierz Pliki Dane", "", "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)")
        if files:
            for f in files:
                if f not in self.files:
                    self.files.append(f)
                    self.list_files.addItem(os.path.basename(f))
                    
    def remove_files(self):
        selected_items = self.list_files.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            row = self.list_files.row(item)
            self.list_files.takeItem(row)
            self.files.pop(row)
            
    def run_bulk_analysis(self):
        if not self.files:
            QMessageBox.warning(self, "Brak Plików", "Wybierz przynajmniej jeden plik do analizy.")
            return
            
        # Parse parameters
        try:
            params = {
                'skiprows': int(self.inp_skiprows.text()),
                'force_thresh': float(self.inp_force_thresh.text()),
                'contact_thresh': float(self.slider_contact_thresh.value()),
                'window_size': float(self.inp_window.text()),
                'min_sep': float(self.inp_min_sep.text()),
                'num_peaks': int(self.inp_num_peaks.text()),
                'convert_mg': self.chk_convert_mg.isChecked(),
                'enable_filter': self.chk_enable_filter.isChecked(),
                'cutoff': float(self.inp_filter_cutoff.text()),
                'order': int(self.inp_filter_order.text())
            }
        except Exception as e:
            QMessageBox.critical(self, "Błąd parametrów", f"Niepoprawne parametry wejściowe:\n{str(e)}")
            return
            
        # Disable buttons
        self.btn_run.setEnabled(False)
        self.btn_add_files.setEnabled(False)
        self.btn_remove_files.setEnabled(False)
        self.btn_export.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start worker thread
        self.worker = AnalysisWorker(self.files, params)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.log_message.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.start()
        
    def on_analysis_finished(self, results, err_msg):
        self.btn_run.setEnabled(True)
        self.btn_add_files.setEnabled(True)
        self.btn_remove_files.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if err_msg:
            self.lbl_status.setText("Wystąpił błąd podczas analizy.")
            QMessageBox.critical(self, "Błąd", f"Analiza nie powiodła się:\n{err_msg}")
            return
            
        self.results_data = results
        self.populate_table()
        
        self.lbl_status.setText(f"Ukończono! Przetworzono {len(self.files)} plików. Łącznie {len(results)} uderzeń.")
        self.btn_export.setEnabled(len(results) > 0)
        
    def populate_table(self):
        self.table.clearContents()
        self.table.setRowCount(len(self.results_data))
        
        for row_idx, data in enumerate(self.results_data):
            for col_idx, col_name in enumerate(COLUMNS_FORMAT):
                val = data.get(col_name, "")
                
                # Format numbers for output in table
                if isinstance(val, float):
                    if np.isnan(val):
                        item_text = ""
                    elif "Force" in col_name or "Max Force" in col_name:
                        item_text = f"{int(round(val))}"
                    elif "Velocity" in col_name or "vel" in col_name:
                        item_text = f"{val:.2f}"
                    elif "Czas kontaktu" in col_name or "Contact Time" in col_name:
                        item_text = f"{val:.3f}"
                    else:
                        item_text = f"{val:.1f}"
                elif isinstance(val, int):
                    item_text = str(val)
                else:
                    item_text = str(val) if val is not None and str(val) != "nan" else ""
                    
                item = QTableWidgetItem(item_text)
                
                # Lock non-editable columns
                if col_name not in EDITABLE_COLUMNS:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    # Gray background for locked metrics columns
                    item.setBackground(QColor("#F2F4F4"))
                else:
                    # Soft blue background for user-editable fields
                    item.setBackground(QColor("#EBF5FB"))
                    
                self.table.setItem(row_idx, col_idx, item)
                
    def export_to_excel(self):
        if not self.results_data:
            return
            
        # Retrieve final user-edited data from the table
        exported_rows = []
        for row_idx in range(self.table.rowCount()):
            row_dict = {}
            for col_idx, col_name in enumerate(COLUMNS_FORMAT):
                item = self.table.item(row_idx, col_idx)
                text = item.text() if item else ""
                
                # Cast to correct type
                if col_name in EDITABLE_COLUMNS:
                    if col_name in ['wiek', 'masa', 'wysokość ciała']:
                        try:
                            row_dict[col_name] = float(text) if text else np.nan
                        except:
                            row_dict[col_name] = np.nan
                    else:
                        row_dict[col_name] = text if text else np.nan
                else:
                    # Keep calculated numeric value
                    orig_val = self.results_data[row_idx].get(col_name, np.nan)
                    row_dict[col_name] = orig_val
            exported_rows.append(row_dict)
            
        df_export = pd.DataFrame(exported_rows, columns=COLUMNS_FORMAT)
        
        # Show save dialog
        save_path, _ = QFileDialog.getSaveFileName(self, "Zapisz dane zbiorcze", "dane zbiorcze.xlsx", "Excel Files (*.xlsx);;All Files (*)")
        if not save_path:
            return
            
        try:
            df_export.to_excel(save_path, index=False)
            QMessageBox.information(self, "Sukces", f"Pomyślnie wyeksportowano tabelę zbiorczą do pliku:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Błąd eksportu", f"Nie udało się zapisać pliku Excel:\n{str(e)}")
