#===============================================================================
# nuitka-project: --enable-plugin=tk-inter
# nuitka-project: --user-package-configuration-file=nuitka-config.yaml
# nuitka-project: --include-package=podman_compose
# nuitka-project: --include-package-data=ttkbootstrap
# nuitka-project-if: os.getenv("DEPLOYMENT") == "yes":
#   nuitka-project: --deployment
#   nuitka-project: --windows-console-mode=disable
#   nuitka-project: --mode=onefile
#===============================================================================

import ttkbootstrap as ttk

#===============================================================================

from container_manager.settings import Settings
from container_manager.ui import ModellingStatusWindow

CONTAINER_NAME = 'xx'
CONTAINER_PORT = 8000

#===============================================================================

def main():
    settings = Settings(None, CONTAINER_PORT)
    app = ttk.App(title="Modular Modelling", theme="bootstrap-light", size=(560, 520))
    ModellingStatusWindow(app, settings)
    app.mainloop()

#===============================================================================

if __name__ == '__main__':
    main()

#===============================================================================
