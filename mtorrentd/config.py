"""Handling of config settings and files."""
import os
import sys
import copy
import yaml

from .paths import CONFIG_PATHS, CONFIG_NAMES
from .default_config_values import CONFIG, SITES
from .validators import integer_0_or_1, true_or_false, validate_url

possible_site_values = {
    'login_required': {'required': True, 'validate': true_or_false},
    'page_path': {'required': True, 'validate': lambda x: validate_url(x, path=True)},
    'search_path': {'required': True, 'validate': lambda x: validate_url(x, path=True)},
    'url': {'required': True, 'validate': validate_url},
    'login_path': {'required': False, 'default_value': None, 'validate': lambda x: validate_url(x, path=True)},
    'page_start': {'required': False, 'default_value': 0, 'validate': integer_0_or_1},
    'append_path': {'required': False, 'default_value': '', 'validate': lambda x: validate_url(x, path=True)},
    'username': {'required': False, 'default_value': None, 'validate': False},
    'password': {'required': False, 'default_value': None, 'validate': False}
}


def handle_undefined_values(selected_config, config_selection) -> dict:
    """Handle undefined values in config files.

    Will exit if value is not specified and required. Otherwise value will be
    set to it's default that is specified in possible_site_values.
    """
    if config_selection is 'sites':
        for site, site_values in selected_config.items():
            # Check required values
            for value in possible_site_values:
                if value not in site_values.keys():
                    # If value is required then exit if not specified.
                    if possible_site_values[value]['required']:
                        print(value, 'must be specified under configuration for',
                              site + '.')
                        exit(78)
                    # If value is not required then set it to its default value
                    # if it's not specified.
                    else:
                        selected_config[site][value] = possible_site_values[value]['default_value']
    elif config_selection is 'config':
        pass

    return selected_config


def validate_config_values(selected_config, config_selection) -> None:
    """Validate config values."""
    if config_selection is 'sites':
        for site, values in selected_config.items():
            for key, value in values.items():
                try:
                    if possible_site_values[key]['validate']:
                        possible_site_values[key]['validate'](value)
                except ValueError as err:
                    raise ValueError('Error when validating config value for the option ' +
                                     '%s under %s: %s' % (key, site, err))
    elif config_selection is 'config':
        try:
            validate_url(selected_config.get('watch_dir', 'Not required'), path=True)
        except ValueError as err:
            print('Error when validating config value for %s: %s' % (site, err))


def load_config(config_selection) -> dict:
    """Load config.

    User defined config files will take precedence over the built in config.
    """
    selected_config = dict()
    if config_selection == 'config':
        selected_config = copy.deepcopy(CONFIG)
    elif config_selection == 'sites':
        selected_config = copy.deepcopy(SITES)
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

    validate_config_values(selected_config, config_selection)
    selected_config = handle_undefined_values(selected_config, config_selection)

    return selected_config
