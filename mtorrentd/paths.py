import os

MTORRENTD_DIR = os.path.abspath(os.path.dirname(__file__))
USER_CONFIG_ROOT = os.environ.get('XDG_CONFIG_HOME',
                             os.path.join(os.environ.get('HOME'), '.config/'))
CONFIG_PATHS = {'system': os.path.join(MTORRENTD_DIR, 'default-configs'),
                'user': os.path.join(USER_CONFIG_ROOT, 'mtorrentd')}
CONFIG_NAMES = {'sites': 'sites.yaml', 'config': 'config.yaml'}
SITE_MODULES = {'system': os.path.join(MTORRENTD_DIR, 'site-modules'), 'user': os.path.join(USER_CONFIG_ROOT, 'site_modules')}
