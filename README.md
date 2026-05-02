# PhysioSim - Biomechanical Analysis App

Aplikacja desktopowa do zaawansowanej analizy danych biomechanicznych z platform tensometrycznych oraz czujników inercyjnych (EMG/Accel). Pozwala na cięcie surowych danych na pojedyncze zdarzenia (uderzenia/ruchy), analizę siły wypadkowej, przyspieszenia oraz automatyczne całkowanie numeryczne do prędkości z generowaniem podsumowań.

## Instrukcja Instalacji (Dla osób bez zainstalowanego Pythona)

Jeśli nie masz na komputerze zainstalowanego Pythona ani żadnych bibliotek programistycznych, postępuj zgodnie z poniższymi krokami, aby uruchomić aplikację.

### Krok 1: Instalacja Pythona
1. Wejdź na oficjalną stronę Pythona: [python.org/downloads](https://www.python.org/downloads/)
2. Pobierz najnowszą wersję instalatora dla systemu Windows.
3. Uruchom pobrany plik. **BARDZO WAŻNE:** Na pierwszym ekranie instalatora upewnij się, że zaznaczyłeś pole wyboru (checkbox) **"Add Python to PATH"** (Dodaj Pythona do ścieżki środowiskowej) na samym dole okienka.
4. Kliknij "Install Now" i poczekaj na zakończenie instalacji.

### Krok 2: Pobranie kodu aplikacji
1. Zlokalizuj zielony przycisk **"Code"** na górze strony tego repozytorium GitHub.
2. Wybierz opcję **"Download ZIP"**.
3. Wypakuj pobrany folder (np. na Pulpit lub do Moich Dokumentów).

### Krok 3: Instalacja wymaganych bibliotek
1. Otwórz wbudowany w system Windows program o nazwie **Wiersz polecenia** (wpisz `cmd` w menu Start) lub **PowerShell**.
2. W oknie terminala wpisz komendę przejścia do folderu, w którym wypakowałeś kod, na przykład:
   ```bash
   cd "C:\Users\TwojaNazwa\Desktop\aplikacja uderzenia"
   ```
   *(Zastąp powyższą ścieżkę dokładną lokalizacją swojego wypakowanego folderu).*
3. Uruchom poniższą komendę, aby zainstalować wszystkie potrzebne biblioteki (takie jak PySide6, matplotlib, pandas):
   ```bash
   pip install -r requirements.txt
   ```
4. Poczekaj, aż system pobierze i zainstaluje wszystkie pliki.

### Krok 4: Uruchomienie aplikacji
Gdy instalacja dobiegnie końca, w tym samym oknie terminala wpisz komendę startową:
```bash
python main.py
```
Aplikacja powinna się uruchomić! Od teraz za każdym razem, gdy zechcesz jej użyć, wystarczy wykonać ponownie jedynie **Krok 4** (pamiętając o uprzednim przejściu do folderu za pomocą `cd`).

## Funkcjonalności
- **Moduł 1 (Tarcza - Cięcie):** Identyfikacja szczytów siły z platformy w celu automatycznego wycinania okien czasowych (eventów). Przelicza surowe dane `mG` z sensorów na standardowe `m/s²`.
- **Moduł 2 (Tarcza - Analiza):** Wczytywanie wyciętych okien uderzeń i matematyczne wyliczanie prędkości dla poszczególnych osi oraz prędkości wypadkowej ze wskazaniem dokładnych parametrów (siła, przyspieszenie, prędkość) w mikrosekundzie uderzenia.
- **Moduł 3 (Powietrze):** Zintegrowany moduł tnąco-analizujący, bazujący całkowicie na przyspieszeniu czujnika (przydatny tam, gdzie ruch uderzenia wykonano bez fizycznej bariery).
