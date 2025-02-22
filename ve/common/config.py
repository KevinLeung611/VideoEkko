import os
import sys

import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ve.common import constants

_config_path = os.path.join(constants.ROOT_PATH, 'conf.yaml')

def _init():
    with open(_config_path, 'r') as f:
        yaml_config = yaml.safe_load(f)

    return yaml_config

yaml_config = _init()

def get_config(name: str = None):
    if not name:
        return yaml_config
    return yaml_config[name]

if __name__ == '__main__':
    print(get_config('whisper'))