import os

replacements = {
    # main.py
    '"1. Cięcie Eventów (Tarcza)"': '"1. Event Extraction (Force Plate)"',
    '"2. Analiza Prędkości (Tarcza)"': '"2. Velocity Analysis (Force Plate)"',
    '"3. Analiza (Powietrze)"': '"3. Air Analysis (Inertial)"',

    # module_extractor.py & common
    '"1. Wybierz plik z danymi"': '"1. Select Data File"',
    '"Brak pliku"': '"No file selected"',
    '"Pomiń n pierwszych wierszy przy wczytywaniu (domyślnie 3 dla plików Noraxon/Ultium)"': '"Skip first n rows (default 3 for Noraxon/Ultium)"',
    '"2. Mapowanie Kolumn"': '"2. Column Mapping"',
    '"Konwertuj Accel z mG na m/s²"': '"Convert Accel from mG to m/s²"',
    '"--- Brak ---"': '"--- None ---"',
    '"3. Parametry detekcji (Tarcza)"': '"3. Detection Parameters (Force Plate)"',
    '"4. Obliczenia i Zapis"': '"4. Calculation & Export"',
    '"Identyfikuj uderzenia (Calculate & Plot)"': '"Identify Impacts (Calculate & Plot)"',
    '"Tnij na Eventy i Zapisz"': '"Cut Events & Save"',
    '"Wybierz plik z danymi"': '"Select Data File"',
    '"Błąd"': '"Error"',
    '"Nie udało się wczytać pliku: {str(e)}"': '"Failed to load file: {str(e)}"',
    '"Sukces"': '"Success"',
    'f"Pomyślnie wczytano plik. Znaleziono {len(self.data)} wierszy."': 'f"Successfully loaded file. Found {len(self.data)} rows."',
    '"Uwaga"': '"Warning"',
    '"Musisz wybrać kolumnę czasu oraz przynajmniej kolumny siły X, Y, Z."': '"You must select the Time column and at least Force X, Y, Z columns."',
    '"Analiza zakończona"': '"Analysis Complete"',
    'f"Znaleziono {len(top_peaks)} peaków.\\nZostały zaznaczone na wykresie."': 'f"Found {len(top_peaks)} peaks.\\nThey have been marked on the plot."',
    '"Wystąpił błąd podczas analizy:\\n{str(e)}"': '"An error occurred during analysis:\\n{str(e)}"',
    'f"Pomyślnie wycięto i zapisano {len(saved_files)} zdarzeń w folderze docelowym:\\n" + "\\n".join(saved_files)': 'f"Successfully cut and saved {len(saved_files)} events in the target folder:\\n" + "\\n".join(saved_files)',
    '"Nie udało się zapisać eventów:\\n{str(e)}"': '"Failed to save events:\\n{str(e)}"',
    "f'Absolute Top Force Peaks ({len(top_peaks)} znaleziono)'": "f'Absolute Top Force Peaks ({len(top_peaks)} found)'",

    # module_target.py
    '"1. Wczytaj wycięty Event"': '"1. Load Extracted Event"',
    '"2. Mapowanie Kolumn (jeśli puste)"': '"2. Column Mapping (if empty)"',
    '"3. Obliczenia Prędkości"': '"3. Velocity Calculations"',
    '"Analizuj Prędkość i Generuj Raport"': '"Analyze Velocity & Generate Report"',
    '"Raport Zdarzenia"': '"Event Report"',
    '"Wczytaj plik i kliknij Analizuj."': '"Load file and click Analyze."',
    '"Wybierz plik z eventem"': '"Select event file"',
    '"Dane wczytane. Gotowy do analizy."': '"Data loaded. Ready for analysis."',
    '"Musisz wybrać kolumnę czasu oraz kolumny przyspieszenia X, Y, Z."': '"You must select the Time column and Acceleration X, Y, Z columns."',
    '"=== MAX PRĘDKOŚCI ==="': '"=== MAXIMUM VELOCITIES ==="',
    '"MAX Wypadkowa:': '"MAX Resultant:',
    '"=== W MOMENCIE MAX FORCE ==="': '"=== AT MAX FORCE INSTANT ==="',
    '"Czas uderzenia:': '"Impact Time:',
    '"Max Siła (Resultant):': '"Max Force (Resultant):',
    '"Przyspieszenie X:': '"Acceleration X:',
    '"Przyspieszenie Y:': '"Acceleration Y:',
    '"Przyspieszenie Z:': '"Acceleration Z:',
    '"Przyspieszenie Wypadkowe:': '"Resultant Acceleration:',
    '"Prędkość X:': '"Velocity X:',
    '"Prędkość Y:': '"Velocity Y:',
    '"Prędkość Z:': '"Velocity Z:',
    '"Prędkość Wypadkowa:': '"Resultant Velocity:',
    "'Brak kolumny resultant_force'": "'Missing resultant_force column'",

    # module_air.py
    '"1. Wczytaj surowe dane (Powietrze)"': '"1. Load Raw Data (Air)"',
    '"Pomiń n pierwszych wierszy"': '"Skip first n rows"',
    '"Konwertuj z mG na m/s²"': '"Convert from mG to m/s²"',
    '"3. Detekcja (Przyspieszenie)"': '"3. Detection (Acceleration)"',
    '"4. Cięcie i Analiza"': '"4. Cut & Analyze"',
    '"Identyfikuj i Tnij na Eventy"': '"Identify & Cut Events"',
    '"Wykryte eventy (kliknij aby analizować):"': '"Detected events (click to analyze):"',
    'f"Wczytano {len(self.data)} wierszy."': 'f"Loaded {len(self.data)} rows."',
    '"Brak peaków"': '"No peaks"',
    '"Nie znaleziono zdarzeń powyżej zadanego progu."': '"No events found above the given threshold."',
    'f"Zapisano {len(self.saved_events_paths)} eventów. Kliknij w event na liście, aby zobaczyć analizę prędkości."': 'f"Saved {len(self.saved_events_paths)} events. Click an event in the list to view its velocity analysis."',
    'f"=== RAPORT ZDARZENIA {row+1} ==="': 'f"=== EVENT {row+1} REPORT ==="',
    '"Nie udało się przeanalizować eventu:\\n{str(e)}"': '"Failed to analyze event:\\n{str(e)}"',
    "f'Top Accel Peaks ({len(top_peaks)} znaleziono)'": "f'Top Accel Peaks ({len(top_peaks)} found)'"
}

files_to_translate = ["main.py", "module_extractor.py", "module_target.py", "module_air.py"]

for filename in files_to_translate:
    path = os.path.join(r"c:\Users\Lenovo\Documents\aplikacja uderzenia", filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
print("Translation complete.")
