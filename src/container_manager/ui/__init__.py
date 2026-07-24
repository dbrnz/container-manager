#===============================================================================

from dataclasses import dataclass
from enum import Enum
import logging
import queue
import threading
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

POLL_INTERVAL = 100         # ms

#===============================================================================

@dataclass
class RunningState:
    description: str
    style: str
    change_state: str

class CONTAINER_STATE(Enum):
    STOPPED  = 0
    STARTING = 1
    STARTED  = 2
    STOPPING = 3

RUNNING_STATES: dict[CONTAINER_STATE, RunningState] = {
    CONTAINER_STATE.STOPPED: RunningState('Container stopped', constants.DANGER, 'start'),
    CONTAINER_STATE.STARTING: RunningState('Container starting...', constants.WARNING, 'start'),
    CONTAINER_STATE.STARTED: RunningState('Container started', constants.SUCCESS, 'stop'),
    CONTAINER_STATE.STOPPING: RunningState('Container stopping...', constants.WARNING, 'stop')
}

#===============================================================================

def docker_exception(error):
    logging.exception(error)
    print(error)
    if error.stderr:
        msg = error.stderr.split('\n')[0]
        ttk.Messagebox.show_error(msg)

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
            self.__settings.save()

#===============================================================================

class ContainerManager:
    def __init__(self, parent, settings: Settings):
        self.__parent = parent
        self.__settings = settings
        self.__container = Container()
        self.__container_state = CONTAINER_STATE.STARTED if self.__container.active else CONTAINER_STATE.STOPPED
        self.__progress_gauge = None
        running_state = RUNNING_STATES[self.__container_state]
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
        self.__button = ttk.Button(
            status, text=running_state.change_state.title(),
            command=lambda: self.__container_event(running_state.change_state)
        ).grid(row=0, column=2, sticky=constants.W, pady=4)
        status.columnconfigure(1, weight=1)
        self.__set_button_state()

    @property
    def active(self):
        return self.__container.active

    @property
    def state(self):
        return self.__container_state

    def check_queue(self):
        try:
            return self.__container.response_queue.get(block=False)
        except queue.Empty:
            pass

    def exit(self):
        self.__container.exit()

    def __container_event(self, change_state):
        if change_state == 'start':
            self.update_run_state(CONTAINER_STATE.STARTING)
            threading.Thread(target=self.__container.start, args=(self.__settings, )).start()
        elif change_state == 'stop':
            self.update_run_state(CONTAINER_STATE.STOPPING)
            threading.Thread(target=self.__container.stop).start()

    def __progress_bar(self, msg:str):
        self.__progress_gauge = ttk.Floodgauge(self.__parent, mode='indeterminate', text=msg, bootstyle='info')
        self.__progress_gauge.pack(fill=constants.X)
        self.__progress_gauge.start()

    def __set_button_state(self):
        self.__button.state(['!disabled' if self.__container_state in [CONTAINER_STATE.STOPPED, CONTAINER_STATE.STARTED]
                        else 'disabled'])

    def update_run_state(self, state: CONTAINER_STATE):
        if self.__progress_gauge is not None:
            self.__progress_gauge.stop()
            self.__progress_gauge.destroy()
            self.__progress_gauge = None
        running_state = RUNNING_STATES[state]
        ttk.apply_bootstyle(self.__status_icon, running_state.style)
        self.__status_label.configure(text=running_state.description)
        self.__button.configure(
            text=running_state.change_state.title(),
            command=lambda: self.__container_event(running_state.change_state)
        )
        self.__container_state = state
        self.__set_button_state()
        if state == CONTAINER_STATE.STARTING:
            self.__progress_bar('Starting...')
        elif state == CONTAINER_STATE.STOPPING:
            self.__progress_bar('Stopping...')

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

        self.__container_settings = ContainerSettings(self, self.__settings)
        self.__dashboard_link = DashboardLink(self, self.__settings)
        self.__manager = ContainerManager(self, self.__settings)

        footer = ttk.Frame(self, padding=10)
        footer.pack(fill=constants.X)
        ttk.Button(footer, text='OK', bootstyle='success', command=self.__exit).pack()
        self.__idle_loop()

    @property
    def __container_state(self):
        return CONTAINER_STATE.STARTED if self.__manager.active else CONTAINER_STATE.STOPPED

    def __idle_loop(self):
        if (response := self.__manager.check_queue()) is not None:
            if response[0] == 'status':
                new_state = CONTAINER_STATE.STARTED if response[1] == 'started' else CONTAINER_STATE.STOPPED
            elif response[0] == 'exception':
                docker_exception(response[1])
                new_state = self.__container_state
            self.__manager.update_run_state(new_state)
        self.__app.after(POLL_INTERVAL, self.__idle_loop)

    def __exit(self):
        print('exiting...')
        self.__manager.exit()
        self.__app.destroy()

#===============================================================================
