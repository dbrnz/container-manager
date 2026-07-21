#===============================================================================

from pathlib import Path

#===============================================================================

import ttkbootstrap as ttk
import ttkbootstrap.constants as constants

#===============================================================================

from ..settings import Settings

#===============================================================================

def select_root_directory(root_directory: str|None=None) -> str|None:
    root_directory = ttk.Querybox.get_directory(
        title="Select the base directory that holds Workspaces",
        initialdir=root_directory if root_directory is not None else Path.home()
    )
    return root_directory

#===============================================================================

class SettingsDialog(ttk.Dialog):
    def __init__(self, settings: Settings):
        super().__init__(parent=None, title='Container settings', alert=False)
        self.__settings = settings

    def create_body(self, master):
        frame = ttk.Frame(master, padding=(20, 20))
        self.root_directory = ttk.StringVar(value=self.__settings.root_directory)
        self.port = ttk.IntVar(value=self.__settings.port)
        self.create_form_field(frame, "root directory", self.root_directory)
        port_field = self.create_form_field(frame, "port", self.port)
        ttk.Validation.range(port_field, 1024, 65535)
        frame.pack(fill=constants.X, expand=True)

    def create_form_field(self, master, label: str, variable: ttk.Variable):
        container = ttk.Frame(master)
        container.pack(fill=constants.X, expand=constants.YES, pady=5)
        lbl = ttk.Label(master=container, text=label.title(), width=10)
        lbl.pack(side=constants.LEFT, padx=5)
        field = ttk.Entry(master=container, textvariable=variable)
        field.pack(side=constants.LEFT, padx=5, fill=constants.X, expand=constants.YES)
        return field

    def create_buttonbox(self, master):
        frame = ttk.Frame(master, padding=(5, 10))
        sub_btn = ttk.Button(
            frame,
            text="Submit",
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
            'root_directory': self.root_directory.get(),
            'port': self.port.get(),
        }
        self.close()

    def on_cancel(self):
        self.close()

#===============================================================================
