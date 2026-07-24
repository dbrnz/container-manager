#===============================================================================

from dataclasses import dataclass
import json
from pathlib import Path

#===============================================================================

SETTINGS_DIRECTORY = '.container_manager'

#===============================================================================

@dataclass
class Settings:
    root_directory: str|None
    port: int

    def __post_init__(self):
        settings_directory = Path.home() / SETTINGS_DIRECTORY
        settings_directory.mkdir(exist_ok=True)
        self.__settings_file = settings_directory / 'config.json'
        self.__settings_file.touch(mode=0o644, exist_ok=True)
        with open(self.__settings_file) as fp:
            try:
                settings = json.load(fp)
                self.root_directory = settings.get('root-directory')
                self.port = settings.get('port', self.port)
            except json.JSONDecodeError:
                fp.close()
                self.save()

    def save(self):
        settings = {
            'port': self.port
        }
        if self.root_directory is not None:
            settings['root-directory'] = self.root_directory
        with open(self.__settings_file, 'w') as fp:
            settings = json.dump(settings, fp)

#===============================================================================
