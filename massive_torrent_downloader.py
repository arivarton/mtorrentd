#! /usr/bin/env python3

import argparse
import requests
import re
from sys import argv
from urllib import parse
from pathlib import Path
from os.path import join
from collections import defaultdict
from bs4 import BeautifulSoup


torrent_site_list = {
    'deildu': {
        'url': 'https://deildu.net',
        'login_required': True,
        'search_path': 'browse.php?search=',
        'page_path': '&page=',
        'login_path': 'takelogin.php',
        'name_regex': r"^details.php\?id=[0-9]{6}$",
        'download_regex': r"download.php*"
    },
    'thepiratebay': {
        'url': 'https://thepiratebay.org',
        'login_required': False,
        'search_path': 'search/',
        'name_regex': r"^details.php\?id=[0-9]{6}$",
        'download_regex': r"download.php*"
    }
}


def validate_url(url, path=False):
    if path:
        _value = parse.urlparse(url).path
    else:
        _value = parse.urlparse(url).netloc
    try:
        if _value:
            return True
        else:
            raise ValueError
    except:
        raise ValueError


def download_torrents(args, site, payload=False):
    site = torrent_site_list[site]

    validate_url(site['url'])
    validate_url(site['search_path'], path=True)

    with requests.Session() as session:
        if payload:
            post = session.post(parse.urljoin(site['url'], site['login_path']),
                                data=payload)
        search_page = session.get(parse.urljoin(site['url'],
                                  site['search_path'] + args.search_string),
                                  cookies=post.cookies)
        soup = BeautifulSoup(search_page.text, 'html.parser')
    download_links = soup.find(class_='torrentlist').find_all(href=re.compile(site['download_regex']))
    name_list = soup.find(class_='torrentlist').find_all(href=re.compile(site['name_regex']))
    search_results = defaultdict(str)
    for index, name in enumerate(name_list):
        _name = name.get_text().strip()
        _link = download_links[index].get('href')
        search_results[_name] = _link
        if args.pretend:
            print('%d: %s\n%s\n' % (index + 1, _name, _link))
    regex = re.compile('.*KILLERS.*')
    matched_list = [name for name in search_results if regex.match(name)]
    if args.pretend:
        print('\n'.join(matched_list))


def login(args, site):
    validate_url(torrent_site_list[site]['login_path'], path=True)
    payload = {
        'username': args.username,
        'password': args.password
    }
    download_torrents(args, site, payload)


def run():
    common_parameters = argparse.ArgumentParser(add_help=False)
    common_parameters.add_argument('search_string', type=str)
    common_parameters.add_argument('-x', '--pretend', action='store_true')
    common_parameters.add_argument('-p', '--pages', type=int, default=3)
    common_parameters.add_argument('-d', '--download_dir', type=str,
                                   default=join(Path.home(), 'Downloads'))

    parser = argparse.ArgumentParser(description='Download multiple torrents')
    subparser = parser.add_subparsers()

    for site in torrent_site_list:
        if torrent_site_list[site]['login_required']:
            login_parser = subparser.add_parser(site, help='Enter login info.', parents=[common_parameters])
            login_parser.add_argument('username', type=str)
            login_parser.add_argument('password', type=str)
            login_parser.set_defaults(func=login)
        else:
            search_parser = subparser.add_parser(site, help='No login required.', parents=[common_parameters])
            search_parser.set_defaults(func=download_torrents)

    args = parser.parse_args()
    args.func(args, argv[1])


if __name__ == '__main__':
    run()
