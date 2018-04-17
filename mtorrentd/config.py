import os
import sys
import yaml

from .paths import CONFIG_PATHS
from .default_config_values import CONFIG, SITES

# Default values for configuration

def load_config(config_selection) -> dict:

    if config_selection == 'config':
        selected_config = CONFIG
    elif config_selection == 'sites':
        selected_config = SITES
    else:
        raise ValueError('Config selection value is not supported.')

    try:
        with open(os.path.join(CONFIG_PATHS['user'], config_selection + '.yaml'), 'r') as sites:
            try:
                selected_config.update(yaml.load(sites))
            except yaml.YAMLError as err:
                print(err)
                sys.exit(1)
    except FileNotFoundError:
        pass

    return selected_config
