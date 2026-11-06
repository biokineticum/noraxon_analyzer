# noraxon_analyzer (PhysioSim)

**Desktop biomechanical strike analysis** for **Noraxon Ultium** (and optional **AMTI** force plate) data — slice multi-strike recordings, compute velocity beyond a standard MR 3.18 export, write results to Excel.

For physiotherapists, martial-arts coaches and sports scientists working with force plates and IMU/EMG strike datasets.

## Features (tabs in `main.py`)

1. **Event Extraction (Force Plate)** — slice raw recordings into single strikes  
2. **Velocity Analysis (Force Plate)** — integrate / analyse target strikes  
3. **Air Analysis (Inertial)** — inertial-only strike analysis  
4. **Bulk Analysis (Force + Accel)** — combined workflows  

Outputs to `.xlsx` via openpyxl. Extra notes (Polish): [`Instrukcja_filtrowania.md`](Instrukcja_filtrowania.md).

## Requirements

- Python 3.x on Windows (tested workflow)
- Dependencies in `requirements.txt`: PySide6, pandas, numpy, matplotlib, scipy, openpyxl

## Install & quick start

```bash
git clone https://github.com/biokineticum/noraxon_analyzer.git
cd noraxon_analyzer
pip install -r requirements.txt
python main.py
```

### Polish quick notes / Notatki PL

Aplikacja desktopowa do cięcia surowych danych na pojedyncze uderzenia, analizy siły wypadkowej i przyspieszenia oraz całkowania do prędkości z podsumowaniem. Instalacja Pythona: zaznacz **Add Python to PATH**, potem `pip install -r requirements.txt` i `python main.py`.

---

## Author

**Dariusz Mosler** (Biokineticum) — physiotherapy, biomechanics, sports science  
🌐 [biokineticum.com](https://biokineticum.com) · 📰 [Substack](https://biokineticum.substack.com) · 𝕏 [@Biokineticum](https://x.com/Biokineticum)

