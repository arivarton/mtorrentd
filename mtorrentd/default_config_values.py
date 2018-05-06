"""Default config values.

Can be replaced by creating a config.yaml or sites.yaml in user config
directory.
"""
CONFIG = {'watch_dir': '~/.mtorrentd/watch'}

# For each value that is required to be set in SITES, it must be defined in
# config.py to be handled properly.
SITES = {
    'thepiratebay': {
        'login_required': False,
        'page_path': '/',
        'search_path': 'search/',
        'url': 'https://thepiratebay.org'
    },
    'linuxtracker': {
        'login_required': False,
        'page_path': '&pages=',
        'page_start': 1,
        'search_path': 'index.php?&page=torrents&search=',
        'append_path': '&active=1',
        'url': 'http://linuxtracker.org'
    },
    'deildu': {
        'login_required': True,
        'login_path': 'takelogin.php',
        'page_path': '&page=',
        'search_path': 'browse.php?search=',
        'url': 'https://deildu.net'
    }
}
