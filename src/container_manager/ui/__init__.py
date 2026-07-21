import webbrowser

import ttkbootstrap as ttk
import ttkbootstrap.constants as constants

from ..settings import Settings
from .settings import SettingsDialog


class ModellingStatusWindow(ttk.Frame):
    def __init__(self, app, settings: Settings):
        super().__init__(app, padding=16)
        self.pack(fill=constants.BOTH, expand=constants.YES)
        self.__app = app
        self.__settings = settings

        header = ttk.Frame(self, padding=10)
        header.pack(fill=constants.X)
        ttk.Label(header, text="Modular Modelling", font="-size 18 -weight bold").pack()

        status = ttk.Labelframe(self, text="Status", padding=12)
        status.pack(fill=constants.X, padx=10, pady=10)
        ttk.Label(status, icon='circle-fill', bootstyle='success').grid(row=0, column=0, sticky=constants.W, padx=4, pady=4)
        ttk.Label(status, text='Container running').grid(row=0, column=1, sticky=constants.EW, padx=4, pady=4)
        ttk.Button(status, text='Stop', command=lambda: self.__container_event('stop')).grid(row=0, column=2, sticky=constants.W, pady=4)
        status.columnconfigure(1, weight=1)

        config = ttk.Labelframe(self, text="Settings", padding=12)
        config.pack(fill=constants.X, padx=10, pady=10)
        ttk.Label(config, text='Modelling root directory:').grid(row=0, column=0, sticky=constants.W, padx=4, pady=4)
        self.__root_dir_label = ttk.Label(config, text=settings.root_directory).grid(row=0, column=1, columnspan=2, sticky=constants.EW, padx=4, pady=4)
        ttk.Label(config, text='Container port:').grid(row=1, column=0, sticky=constants.W, padx=4, pady=4)
        self.__port_label = ttk.Label(config, text=str(settings.port)).grid(row=1, column=1, sticky=constants.EW, padx=4, pady=4)
        ttk.Button(config, text='Change', command=self.__change_settings).grid(row=2, column=2, sticky=constants.W, pady=4)
        config.columnconfigure(1, weight=1)

        ttk.Button(
            self,
            text="Open Dashboard",
            bootstyle="primary link",
            command=self.__open_dashboard
        ).pack(pady=4, fill=constants.X, expand=True)

        footer = ttk.Frame(self, padding=10)
        footer.pack(fill=constants.X)
        ttk.Button(footer, text='OK', bootstyle='success', command=self.__exit).pack()

    def __container_event(self, *args):
        print(args)

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

    def __open_dashboard(self):
        print('open dashboard clicked...')
        webbrowser.open_new_tab(f'http://localhost:{self.__settings.port}')

    def __exit(self):
        print('exiting...')
        self.__app.destroy()
