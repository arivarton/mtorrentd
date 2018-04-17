import os
import importlib.util

from urllib import parse

from .paths import SITE_MODULES

def validate_url(url, path=False):
    if path:
        _value = parse.urlparse(url).path
    else:
        _value = parse.urlparse(url).netloc
    try:
        if _value:
            return True
        else:
            raise ValueError('Invalid value:', _value)
    except:
        raise ValueError('Invalid value:', _value)

def load_site_module(site):
    user_module = os.path.join(SITE_MODULES['user'], site + '.py')
    system_module = os.path.join(SITE_MODULES['system'], site + '.py')
    if os.path.isfile(user_module):
        spec = importlib.util.spec_from_file_location(site, user_module)
        site_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(site_module)
    elif os.path.isfile(system_module):
        spec = importlib.util.spec_from_file_location(site, system_module)
        site_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(site_module)
    else:
        print('Site module not found. Check github for documentation and create a new site module here: %s' %(SITE_MODULES['user']))
        exit(73)
    return site_module
