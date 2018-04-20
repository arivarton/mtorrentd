from sys import exit
from os.path import join
from .paths import CONFIG_PATHS, CONFIG_NAMES

def catch_undefined_credentials(site, credential) -> None:
    if credential.username is None:
        print('Username must be defined for', site)
        print('Either set it by passing the --username parameter or set it in ' \
              'the config file: %s.' % join(CONFIG_PATHS['user'], CONFIG_NAMES['sites']))
        exit(78)
    elif credential.password is None:
        print('Password must be defined for', site)
        print('Either set it by passing the --password parameter or set it in ' \
              'the config file: %s.' % join(CONFIG_PATHS['user'], CONFIG_NAMES['sites']))
        exit(78)
