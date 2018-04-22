import os
import sys
import yaml

from .paths import CONFIG_PATHS, CONFIG_NAMES
from .default_config_values import CONFIG, SITES
from .core import validate_url

CONFIG_SETTINGS = {
    'sites': {
    'required_values': ['login_required', 'page_path', 'search_path', 'url'],
    'login_required_values': ['username', 'password'],
    },
    'config': {
    }
}


def handle_undefined_values(selected_config, config_selection) -> dict:
    if config_selection is 'sites':
        for site, site_values in selected_config.items():
            # Check required values
            for value in CONFIG_SETTINGS[config_selection]['required_values']:
                if value not in site_values.keys():
                    print(value, 'must be specified under configuration for', site + '.')
                    exit(78)
            # Set username and password to None if not defined in a site with
            # login_required: True
            if site_values['login_required']:
                for value in CONFIG_SETTINGS[config_selection]['login_required_values']:
                    if value not in site_values.keys():
                        selected_config[site][value] = None
    elif config_selection is 'config':
        pass

    return selected_config


def validate_config_values(selected_config, config_selection) -> None:
    if config_selection is 'sites':
        for key, values in selected_config.items():
            try:
                validate_url(values['url'])
                validate_url(values['page_path'], path=True)
                validate_url(values['search_path'], path=True)
                validate_url(values.get('append_path', 'Not required'), path=True)
            except ValueError as err:
                print('Error when validating config value for %s: %s' % (key, err))
    elif config_selection is 'config':
        try:
            validate_url(selected_config.get('watch_dir', 'Not required'), path=True)
        except ValueError as err:
            print('Error when validating config value for %s: %s' % (key, err))


def load_config(config_selection) -> dict:
    # Load default config
    if config_selection == 'config':
        selected_config = CONFIG
    elif config_selection == 'sites':
        selected_config = SITES
    else:
        raise ValueError('Config selection value is not supported.')

    # Load user config
    try:
        with open(os.path.join(CONFIG_PATHS['user'], CONFIG_NAMES[config_selection]), 'r') as config_readout:
            loaded_config = yaml.load(config_readout)
            try:
                # loop is required for sites to not replace the dictionary
                # inside the dictionary when updating
                if config_selection == 'sites':
                    for site in loaded_config:
                        if site in selected_config:
                            selected_config[site].update(loaded_config[site])
                        else:
                            selected_config.update({site: loaded_config[site]})
                else:
                    selected_config.update(loaded_config)
            except yaml.YAMLError as err:
                print(err)
                sys.exit(64)
    except FileNotFoundError:
        pass

    selected_config = handle_undefined_values(selected_config, config_selection)
    validate_config_values(selected_config, config_selection)

    return selected_config
