import os

# DATA_DIR = "/home/marek/Programming/projects/freez/data"
DATA_DIR = f"/home/{os.getlogin()}/.freez/"
DATA_FILE = "data.json"
# OVERRIDE - do you want to override the saved workspace in case od name collision? False will prompt for confirmation
OVERWRITE = True  # Default=True
# TIMEOUT - how long to wait for window to open, so it can be resized and moved
TIMEOUT = 20  # Default=20
# CLOSE_TERMINAL - closes all terminal windows
CLOSE_TERMINAL = False  # Default=False
# NEW_TERM_IN_TAB - opens new terminal in tab instead of new window
NEW_TERM_IN_TAB = True  # Default=True
