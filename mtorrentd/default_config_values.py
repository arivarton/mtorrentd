CONFIG = {'watch_dir': '~/.mtorrentd/watch'}

SITES = {
    'thepiratebay': {
            'login_required': False,
            'page_path': '/',
            'search_path': 'search/',
            'url': 'https://thepiratebay.org'
    },
    'deildu': {
        'login_required': True,
        'login_path': 'takelogin.php',
        'page_path': '&page=',
        'search_path': 'browse.php?search=',
        'url': 'https://deildu.net'
    }
}
