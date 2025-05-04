# Freez & Ufreez

**Freez** is a command-line tool that allows you to **save** and **restore** workspaces by capturing open windows and their positions. **Ufreez** complements Freez by allowing you to **reopen** previously saved workspaces.

## Features

✅ Save all open windows as a workspace  
✅ Select specific windows to save  
✅ Restore saved workspaces with a single command  
✅ List and manage saved workspaces  
✅ Optionally close all windows, reboot, or shut down after saving  

---

## Installation

1. Prerequisites
  - This tool is meant for Ubuntu using Wayland
  - [Window Calls](https://extensions.gnome.org/extension/4724/window-calls/) extension for GNOME
  - Python 3.13
  - git

2. Clone the repository:
   ```sh
   git clone https://github.com/stecik/freez.git freez
   cd freez
   ```
   
3. Install dependencies
   ```sh
   sudo apt install pipx
   pipx install poetry
   poetry install
   ```
4. Run
   ```sh
   python freez.py -h
   python ufreez.py -h
   ```

## Run without python
   ```sh
   pip install pyinstaller
   pyinstaller --onefile freez.py
   pyinstaller --onefile ufreez.py
   cp dist/* /usr/bin
   freez -h
   ufreez -h
   ```
## Tips
- the data.json file is located in /home/$USER/.freez - you can edit the saved workspaces there

# Licence
Feel free to use/edit my software in any way possible for __non-commercial__ purposes.
