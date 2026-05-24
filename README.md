# PhysioSim - Biomechanical Analysis App

*(Scroll down for English version / Wersja polska poniżej)*

---

## 🇵🇱 Wersja Polska

Aplikacja desktopowa do zaawansowanej analizy danych biomechanicznych z platform tensometrycznych oraz czujników inercyjnych (EMG/Accel). Pozwala na cięcie surowych danych na pojedyncze zdarzenia (uderzenia/ruchy), analizę siły wypadkowej, przyspieszenia oraz automatyczne całkowanie numeryczne do prędkości z generowaniem podsumowań.

### Dokumentacja dodatkowa
- [Instrukcja filtrowania sygnałów biomechanicznych (Zalecenia m.in. Noraxon)](file:///c:/Users/Lenovo/Documents/aplikacja%20uderzenia/Instrukcja_filtrowania.md)

### Instrukcja Instalacji (Dla osób bez zainstalowanego Pythona)

Jeśli nie masz na komputerze zainstalowanego Pythona ani żadnych bibliotek programistycznych, postępuj zgodnie z poniższymi krokami, aby uruchomić aplikację.

#### Krok 1: Instalacja Pythona
1. Wejdź na oficjalną stronę Pythona: [python.org/downloads](https://www.python.org/downloads/)
2. Pobierz najnowszą wersję instalatora dla systemu Windows.
3. Uruchom pobrany plik. **BARDZO WAŻNE:** Na pierwszym ekranie instalatora upewnij się, że zaznaczyłeś pole wyboru (checkbox) **"Add Python to PATH"** na samym dole okienka.
4. Kliknij "Install Now" i poczekaj na zakończenie instalacji.

#### Krok 2: Pobranie kodu aplikacji
1. Zlokalizuj zielony przycisk **"Code"** na górze strony tego repozytorium GitHub.
2. Wybierz opcję **"Download ZIP"**.
3. Wypakuj pobrany folder (np. na Pulpit).

#### Krok 3: Instalacja wymaganych bibliotek
1. Otwórz wbudowany w system Windows program o nazwie **Wiersz polecenia** (wpisz `cmd` w menu Start) lub **PowerShell**.
2. W oknie terminala wpisz komendę przejścia do folderu, w którym wypakowałeś kod, na przykład:
   ```bash
   cd "C:\Users\TwojaNazwa\Desktop\aplikacja uderzenia"
   ```
3. Uruchom poniższą komendę, aby zainstalować wszystkie potrzebne biblioteki:
   ```bash
   pip install -r requirements.txt
   ```
4. Poczekaj na zakończenie instalacji.

#### Krok 4: Uruchomienie aplikacji
Gdy instalacja dobiegnie końca, w tym samym oknie terminala wpisz komendę startową:
```bash
python main.py
```
Od teraz wystarczy zawsze wywoływać tę jedną komendę!

---

## 🇬🇧 English Version

A desktop application for advanced biomechanical data analysis using force plates and inertial sensors (EMG/Accel). It enables cutting raw data into individual events (impacts/movements), analyzing resultant force, acceleration, and performing automatic numerical integration to velocity with comprehensive summary reports.

### Additional Documentation
- [Biomechanical Signal Filtering Guide (Polish)](file:///c:/Users/Lenovo/Documents/aplikacja%20uderzenia/Instrukcja_filtrowania.md)

### Installation Guide (For Users Without Python Installed)

If you do not have Python or any programming libraries installed on your computer, follow these steps to run the application.

#### Step 1: Install Python
1. Go to the official Python website: [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest installer for Windows.
3. Run the downloaded file. **CRITICAL:** On the first installer screen, make sure to check the box **"Add Python to PATH"** at the very bottom of the window.
4. Click "Install Now" and wait for the installation to finish.

#### Step 2: Download Application Code
1. Locate the green **"Code"** button at the top of this GitHub repository page.
2. Select **"Download ZIP"**.
3. Extract the downloaded folder (e.g., to your Desktop).

#### Step 3: Install Required Libraries
1. Open the built-in Windows program named **Command Prompt** (type `cmd` in the Start menu) or **PowerShell**.
2. In the terminal window, type the command to navigate to the folder where you extracted the code, for example:
   ```bash
   cd "C:\Users\YourName\Desktop\aplikacja uderzenia"
   ```
3. Run the following command to install all necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Wait for the system to download and install all files.

#### Step 4: Run the Application
Once the installation is complete, type the start command in the same terminal window:
```bash
python main.py
```
From now on, whenever you want to use it, you only need to execute this command!
