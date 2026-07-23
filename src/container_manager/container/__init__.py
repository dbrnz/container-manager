#===============================================================================

import os
from pathlib import Path, WindowsPath
from importlib.resources import as_file, files
import logging
import sys
from tempfile import NamedTemporaryFile

#===============================================================================

from python_on_whales import DockerClient
from python_on_whales.exceptions import DockerException
import ttkbootstrap as ttk

#===============================================================================

from ..settings import Settings

#===============================================================================

def docker_exception(error):
    logging.exception(error)
    if error.stderr:
        msg = error.stderr.split('\n')[0]
        ttk.Messagebox.show_error(msg)

def toast_success(msg: str):
    ttk.ToastNotification(
        title='Modular Modelling',
        message=msg,
        duration=3000,  # ms
        bootstyle="success",
    ).show_toast()

#===============================================================================

class Container:
    def __init__(self):
        compose_yaml = files().joinpath('./compose.yaml')
        env_file = NamedTemporaryFile(suffix='.env', delete=False)
        self.__env_file = Path(env_file.name).absolute()
        logging.info(f'Environment settings: {self.__env_file}')
        env_file.close()
        self.__config_file = None
        self.__compiled = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
        if self.__compiled:
            if sys.platform == 'win32':
                podman_compose = 'podman-compose.exe'
            else:
                podman_compose = 'podman-compose'
            with as_file(files().joinpath(f'../../{podman_compose}')) as path:
                os.environ['PODMAN_COMPOSE_PROVIDER'] = str(path.resolve())
            logging.info(f'Compose provider: {os.environ['PODMAN_COMPOSE_PROVIDER']}')
        os.environ['PODMAN_COMPOSE_WARNING_LOGS'] = 'false'
        with as_file(compose_yaml) as path:
            # 'path' is a true pathlib.Path object
            self.__config_file = path.absolute()
            self.__container = DockerClient(
                client_call=['podman'],
                client_type='podman',
                compose_files=[self.__config_file],
                compose_env_files=[self.__env_file]
            )
        self.set_state()

    @property
    def active(self):
        return self.__active

    def exit(self):
        self.__env_file.unlink(missing_ok=True)

    def set_state(self):
        self.__active = False
        try:
            running_containers = self.__container.compose.ps()
            print('containers:', running_containers)
            active_count = 0
            for container in running_containers:
                if container.state.running:
                    active_count += 1
            self.__active = active_count > 0
        except DockerException as error:
            docker_exception(error)

    def start(self, settings: Settings):
        self.__set_environment(settings)
        try:
            self.__container.compose.up(detach=True, quiet=True)
            toast_success('Container started...')
        except DockerException as error:
            docker_exception(error)
        self.set_state()

    def stop(self):
        try:
            self.__container.compose.down(remove_images='all', quiet=True)
            toast_success('Container stopped...')
        except DockerException as error:
            docker_exception(error)
        self.set_state()

    def __set_environment(self, settings: Settings):
        with open(self.__env_file, 'w') as fp:
            fp.write(f'SCICRUNCH_API_KEY={os.environ.get('SCICRUNCH_API_KEY', '')}\n')
            if (root_dir := settings.root_directory) is not None:
                if sys.platform == 'win32':
                    path = WindowsPath(root_dir).absolute()
                    drive = path.drive[:-1].lower()
                    root_dir = WindowsPath(f'/mnt/{drive}', *path.parts[1:])
                fp.write(f'FLATMAP_SOURCE_ROOT={root_dir}\n')
            fp.write(f'FLATMAP_SERVER_PORT={settings.port}\n')

#===============================================================================
