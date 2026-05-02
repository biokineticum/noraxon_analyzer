# PhysioSim - Biomechanical Analysis App

A desktop application for advanced biomechanical data analysis using force plates and inertial sensors (EMG/Accel). It enables cutting raw data into individual events (impacts/movements), analyzing resultant force, acceleration, and performing automatic numerical integration to velocity with comprehensive summary reports.

## Installation Guide (For Users Without Python Installed)

If you do not have Python or any programming libraries installed on your computer, follow these steps to run the application.

### Step 1: Install Python
1. Go to the official Python website: [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest installer for Windows.
3. Run the downloaded file. **CRITICAL:** On the first installer screen, make sure to check the box **"Add Python to PATH"** at the very bottom of the window.
4. Click "Install Now" and wait for the installation to finish.

### Step 2: Download Application Code
1. Locate the green **"Code"** button at the top of this GitHub repository page.
2. Select **"Download ZIP"**.
3. Extract the downloaded folder (e.g., to your Desktop or Documents).

### Step 3: Install Required Libraries
1. Open the built-in Windows program named **Command Prompt** (type `cmd` in the Start menu) or **PowerShell**.
2. In the terminal window, type the command to navigate to the folder where you extracted the code, for example:
   ```bash
   cd "C:\Users\YourName\Desktop\aplikacja uderzenia"
   ```
   *(Replace the path above with the exact location of your extracted folder).*
3. Run the following command to install all necessary libraries (such as PySide6, matplotlib, pandas):
   ```bash
   pip install -r requirements.txt
   ```
4. Wait for the system to download and install all files.

### Step 4: Run the Application
Once the installation is complete, type the start command in the same terminal window:
```bash
python main.py
```
The application should launch! From now on, whenever you want to use it, you only need to execute **Step 4** (remembering to first navigate to the folder using `cd`).

## Features
- **Module 1 (Force Plate - Event Extraction):** Identifies force peaks from the platform to automatically cut time windows (events). Converts raw `mG` data from sensors to standard `m/s²`.
- **Module 2 (Force Plate - Velocity Analysis):** Loads extracted impact windows and mathematically calculates velocity for individual axes and resultant velocity, indicating exact parameters (force, acceleration, velocity) at the microsecond of impact.
- **Module 3 (Air Analysis - Inertial):** An integrated extraction-analysis module based entirely on sensor acceleration (useful where the impact movement is performed without a physical barrier).
