import os
import sys
import yaml

from .paths import CONFIG_PATHS, CONFIG_NAMES
from .default_config_values import CONFIG, SITES

def handle_undefined_sites_value(selected_config, config_selection) -> dict:
    if config_selection is 'sites':
        required_values = ['login_required', 'page_path', 'search_path', 'url']
        login_required_values = ['username', 'password']
        for site, site_values in selected_config.items():
            # Check required values
            for value in required_values:
                if value not in site_values.keys():
                    print(value, 'must be specified under configuration for', site + '.')
                    exit(78)
            # Set username and password to None if not defined in a site with
            # login_required: True
            if site_values['login_required']:
                for value in login_required_values:
                    if value not in site_values.keys():
                        selected_config[site][value] = None
    elif config_selection is 'config':
        pass

    return selected_config


def load_config(config_selection) -> dict:
    if config_selection == 'config':
        selected_config = CONFIG
    elif config_selection == 'sites':
        selected_config = SITES
    else:
        raise ValueError('Config selection value is not supported.')

    try:
        with open(os.path.join(CONFIG_PATHS['user'], CONFIG_NAMES[config_selection]), 'r') as config_readout:
            loaded_config = yaml.load(config_readout)
            try:
                # loop is required for sites to not replace the dictionary
                # inside the dictionary when updating
                if config_selection == 'sites':
                    for site in selected_config:
                        if site in loaded_config:
                            selected_config[site].update(loaded_config[site])
                else:
                    selected_config.update(loaded_config)
            except yaml.YAMLError as err:
                print(err)
                sys.exit(64)
    except FileNotFoundError:
        pass

    return handle_undefined_sites_value(selected_config, config_selection)
