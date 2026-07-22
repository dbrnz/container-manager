#===============================================================================

from dataclasses import dataclass
from enum import Enum
import webbrowser

#===============================================================================

import ttkbootstrap as ttk
import ttkbootstrap.constants as constants

#===============================================================================

from ..container import Container
from ..settings import Settings

from .settings import SettingsDialog
from .styles import initialise_styles

#===============================================================================

@dataclass
class RunningState:
    description: str
    style: str
    change_state: str

class RUNNING_STATE(Enum):
    STOPPED = 0
    RUNNING = 1




RUNNING_STATES: dict[RUNNING_STATE, RunningState] = {
    RUNNING_STATE.STOPPED: RunningState('Container stopped', constants.DANGER, 'start'),
    RUNNING_STATE.RUNNING: RunningState('Container running', constants.SUCCESS, 'stop')
}

#===============================================================================

class ContainerSettings:
    def __init__(self, parent, settings: Settings):
        self.__settings = settings
        config = ttk.Labelframe(parent, text="Settings", padding=12)
        config.pack(fill=constants.X, padx=10, pady=10)
        ttk.Label(
            config,
            text='Root directory:'
        ).grid(row=0, column=0, sticky=constants.W, padx=4, pady=4)
        self.__root_dir_label = ttk.Label(
            config,
            text=settings.root_directory,
            wraplength=200
        ).grid(row=0, column=1, columnspan=2, sticky=constants.EW, padx=4, pady=4)
        ttk.Label(
            config,
            text='Container port:'
        ).grid(row=1, column=0, sticky=constants.W, padx=4, pady=4)
        self.__port_label = ttk.Label(
            config,
            text=str(settings.port)
        ).grid(row=1, column=1, sticky=constants.EW, padx=4, pady=4)
        ttk.Button(
            config,
            text='Configure',
            command=self.__change_settings
        ).grid(row=2, column=2, sticky=constants.W, pady=4)
        config.columnconfigure(1, weight=1)

    def __change_settings(self):
        dialog = SettingsDialog(self.__settings)
        dialog.show()
        if (settings := dialog.result) is not None:
            ## If settings have changed need [Reload] container popup...
            self.__settings.root_directory = settings['root_directory']
            self.__root_dir_label.configure(text=self.__settings.root_directory)
            self.__settings.port = settings['port']
            self.__port_label.configure(text=self.__settings.port)
        print(settings, self.__settings)

#===============================================================================

class ContainerStatus:
    def __init__(self, parent, settings: Settings, container):
        self.__settings = settings
        self.__container = container
        state = RUNNING_STATE.RUNNING if self.__container.active else RUNNING_STATE.STOPPED
        running_state = RUNNING_STATES[state]
        status = ttk.Labelframe(parent, text="Status", padding=12)
        status.pack(fill=constants.X, padx=10, pady=10)
        self.__status_icon = ttk.Label(
            status,
            icon='circle-fill',
            bootstyle=running_state.style
        ).grid(row=0, column=0, sticky=constants.W, padx=4, pady=4)
        self.__status_label = ttk.Label(
            status,
            text=running_state.description
        ).grid(row=0, column=1, sticky=constants.EW, padx=4, pady=4)
        self.__status_change_button = ttk.Button(
            status, text=running_state.change_state.title(),
            command=lambda: self.__container_event(running_state.change_state)
        ).grid(row=0, column=2, sticky=constants.W, pady=4)
        status.columnconfigure(1, weight=1)

    def __container_event(self, change_state):
        if change_state == 'start':
            # inactivate button
            self.__container.start(self.__settings)
            ## do this asynchronously
            ## set state to starting and poll for active

        elif change_state == 'stop':
            self.__container.stop()
            ## do this asynchronously
            ## set state to stopping and poll for not active
        self.__set_run_state()

    def __set_run_state(self):
        state = RUNNING_STATE.RUNNING if self.__container.active else RUNNING_STATE.STOPPED
        running_state = RUNNING_STATES[state]
        ttk.apply_bootstyle(self.__status_icon, running_state.style)
        self.__status_label.configure(text=running_state.description)
        self.__status_change_button.configure(
            text=running_state.change_state.title(),
            command=lambda: self.__container_event(running_state.change_state)
        )

#===============================================================================

class DashboardLink:
    def __init__(self, parent, settings: Settings, active: bool=False):
        self.__settings = settings
        self.__button = ttk.Button(
            parent,
            text="Open Dashboard",
            bootstyle="primary link",
            command=self.__open_dashboard
        ).pack(pady=4, fill=constants.X, expand=True)
        self.activate(active)

    def activate(self, active: bool=True):
        self.__button.state(['!disabled' if active else 'disabled'])                 # greyed out, not clickable

    def __open_dashboard(self):
        dashboard_url = f'http://localhost:{self.__settings.port}'
        print('Open dashboard:', dashboard_url)
        webbrowser.open_new_tab(dashboard_url)

#===============================================================================

class ModellingStatusWindow(ttk.Frame):
    def __init__(self, app, settings: Settings):
        initialise_styles(app)
        super().__init__(app, padding=16)
        self.pack(fill=constants.BOTH, expand=constants.YES)
        self.__app = app
        self.__settings = settings
        self.__container = Container()

        header = ttk.Frame(self, padding=10)
        header.pack(fill=constants.X)
        ttk.Label(header, text="Modular Modelling", font="-size 18 -weight bold").pack()

        self.__container_status = ContainerStatus(self, self.__settings, self.__container)
        self.__container_settings = ContainerSettings(self, self.__settings)
        self.__dashboard_link = DashboardLink(self, self.__settings)

        footer = ttk.Frame(self, padding=10)
        footer.pack(fill=constants.X)
        ttk.Button(footer, text='OK', bootstyle='success', command=self.__exit).pack()

    def __exit(self):
        print('exiting...')
        self.__container.exit()
        self.__app.destroy()

#===============================================================================
