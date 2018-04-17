import os

MTORRENTD_DIR = os.path.abspath(os.path.dirname(__file__))
CONFIG_ROOT = os.environ.get('XDG_CONFIG_HOME',
                             os.path.join(os.environ.get('HOME'), '.config/'))
CONFIG_HOME = os.path.join(CONFIG_ROOT, 'mtorrentd')
CONFIG_PATHS = {'system': os.path.join(MTORRENTD_DIR, 'default-configs'), 'user': CONFIG_HOME}
SITE_MODULES = {'system': os.path.join(MTORRENTD_DIR, 'site-modules'), 'user': os.path.join(CONFIG_HOME, 'site_modules')}
