#===============================================================================

from pathlib import Path

#===============================================================================

import ttkbootstrap as ttk

#===============================================================================

from .settings import Settings
from .ui import ModellingStatusWindow

CONTAINER_NAME = 'xx'
CONTAINER_PORT = 8000

#===============================================================================

def main():
    settings = Settings(Path.home(), CONTAINER_PORT)
    app = ttk.App(title="Modelling Modelling", theme="bootstrap-light", size=(560, 520))
    ModellingStatusWindow(app, settings)
    app.mainloop()

#===============================================================================
