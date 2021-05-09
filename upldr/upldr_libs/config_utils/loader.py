from clilib.util.util import Util
from pathlib import Path
import json


class Loader:
    def __init__(self, config, fmt="json", keys=None, auto_create=False):
        self.logger = Util.configure_logging(name=__name__)
        self.config_file = config
        self.format = fmt
        self.keys = keys
        self.auto_create = auto_create
        data = self._load_config()
        if keys:
            self._validate_top_level(data)
        self.config = data

    def _validate_top_level(self, data):
        if len(self.keys) < 1:
            raise TypeError("Loaded config (%s) has no keys. Required keys are: %s"
                            % (self.config_file, ', '.join(self.keys)))
        for key in self.keys:
            if key not in data:
                raise TypeError("Loaded config (%s) missing required key \"%s\" from key list [%s]"
                                % (self.config_file, key, ', '.join(self.keys)))

    def write_config_from_keys(self):
        new_config = {}
        for key in self.keys:
            new_config[key] = ""

        if self.format == "json":
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=4)
        self.config = new_config

    def _load_config(self):
        if not Path(self.config_file).exists():
            if self.auto_create:
                self.write_config_from_keys()
            else:
                raise FileNotFoundError(self.config_file)

        if self.format == "json":
            with open(self.config_file) as f:
                return json.load(f)
        else:
            return {}

    def get_config(self):
        class Config(dict):
            def __init__(self, d, path):
                self.__dict__ = d
                self.path = path

            def write_config(self):
                with open(self.path, 'w', encoding='utf-8') as f:
                    json.dump(self.__dict__, f, ensure_ascii=False, indent=4)

            def get_dict(self):
                return self.__dict__

        return Config(self.config, self.config_file)
