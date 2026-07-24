#===============================================================================

from pathlib import Path

#===============================================================================

import ttkbootstrap as ttk
import ttkbootstrap.constants as constants

#===============================================================================

from ..settings import Settings
from .styles import LEFT_LINK_BUTTON_LABEL

#===============================================================================

EMPTY_DIRECTORY = 'Click to set'

#===============================================================================

@ttk.validator
def valid_port(event, warning):
    try:
        port = int(event.postchangetext)
        if 1024 <= port <= 65535:
            ttk.apply_bootstyle(event.widget, constants.PRIMARY)
            warning.configure(text='')
            return True
        else:
            warning.configure(text='Port must be between 1024 and 65535')
    except ValueError:
        warning.configure(text='Port must be numeric')
    ttk.apply_bootstyle(event.widget, constants.WARNING)
    return True

class PortEntry:
    def __init__(self, parent, variable: ttk.StringVar):
        container = ttk.Frame(parent)
        container.pack(fill=constants.X, expand=constants.YES, pady=5)
        lbl = ttk.Label(container, text='Port:', width=10)
        lbl.pack(side=constants.LEFT, padx=5)
        self.__field = ttk.Entry(container, textvariable=variable, width=5)
        self.__field.pack(side=constants.LEFT, padx=5, fill=constants.X, expand=constants.NO)
        warning_field = ttk.Label(container, text='', bootstyle=constants.DANGER)
        warning_field.pack(side=constants.LEFT, padx=5, fill=constants.X, expand=constants.YES)
        ttk.Validation.add(self.__field, valid_port, when='key', warning=warning_field)

#===============================================================================

class SettingsDialog(ttk.Dialog):
    def __init__(self, settings: Settings):
        super().__init__(parent=None, title='Container settings', alert=False)
        self.__settings = settings
        self.__root_directory = ttk.StringVar(value=settings.root_directory if settings.root_directory is not None else EMPTY_DIRECTORY)
        self.__port = ttk.StringVar(value=settings.port)

    def create_body(self, parent):
        frame = ttk.Frame(parent, padding=(20, 20))
        self.__root_link = self.__create_entry_link(frame, "root directory", self.__root_directory)
        PortEntry(frame, self.__port)
        frame.pack(fill=constants.X, expand=True)

    def __create_entry_link(self, parent, label: str, variable: ttk.StringVar):
        container = ttk.Frame(parent)
        container.pack(fill=constants.X, expand=constants.YES, pady=5)
        lbl = ttk.Label(container, text=f'{label.title()}:', width=10)
        lbl.pack(side=constants.LEFT, padx=5)
        button = ttk.Button(
            container,
            text=variable.get(),
            bootstyle='link',
            style=LEFT_LINK_BUTTON_LABEL,
            width=40,
            command=self.__set_directory
        )
        button.pack(side=constants.LEFT, padx=5, fill=constants.X, expand=constants.YES)
        return button

    def create_buttonbox(self, parent):
        frame = ttk.Frame(parent, padding=(5, 10))
        sub_btn = ttk.Button(
            frame,
            text="Save",
            command=self.on_submit,
            bootstyle=constants.SUCCESS,
            width=6,
        )
        sub_btn.pack(side=constants.RIGHT, padx=5)
        sub_btn.focus_set()
        cnl_btn = ttk.Button(
            frame,
            text="Cancel",
            command=self.on_cancel,
            bootstyle=constants.DANGER,
            width=6,
        )
        cnl_btn.pack(side=constants.RIGHT, padx=5)
        frame.pack(side=constants.BOTTOM, fill=constants.X, anchor=constants.S)

    def on_submit(self):
        self._result = {
            'root_directory': self.__root_directory.get(),
            'port': self.__port.get(),
        }
        self.close()

    def on_cancel(self):
        self.close()

    def __set_directory(self):
        current_directory = self.__root_directory.get()
        if current_directory == EMPTY_DIRECTORY:
            current_directory = Path.home()
        root_directory = ttk.Querybox.get_directory(
            title="Select the base directory that holds Workspaces",
            initialdir=current_directory
        )
        if root_directory is not None:
            self.__root_link.configure(text=root_directory)
            self.__root_directory.set(root_directory)

#===============================================================================
