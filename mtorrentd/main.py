#! /usr/bin/env python3

import os
import argparse
import requests
import re
import yaml
import importlib.util
#  import libtorrent
import tempfile
import shutil

from sys import argv, exit
from time import sleep
from urllib import parse
from collections import defaultdict
from bs4 import BeautifulSoup

from .config import load_config
from .core import validate_url, load_site_module
from .helpers import catch_undefined_credentials

def _find_season_name(args, torrent_name):
    pass


def _find_duplicate_seasons(args, torrent_name):
    pass
    #  downloaded_torrents = listdir(self.args.download_dir)


def login(site, args, session):
    validate_url(site['login_path'], path=True)
    payload = {
        'username': args.username,
        'password': args.password
    }
    session.post(parse.urljoin(site['url'], site['login_path']),
                 data=payload)
    return session


def search(site, args):
    site_module = load_site_module(argv[1])

    with requests.Session() as session:
        if site['login_required']:
            session = login(site, args, session)
        crawled_content = list()
        for page in range(args.pages):
            search_page = session.get(parse.urljoin(site['url'],
                                                    site['search_path'] +
                                                    args.search_string +
                                                    site['page_path'] +
                                                    str(page)))
            soup = BeautifulSoup(search_page.text, 'html.parser')
            name_list, download_links = site_module.get_torrent_list(site, soup)
            if not name_list or not download_links:
                print('No more results after %d page(s)' % page)
                break
            crawled_content.append((name_list, download_links))
            print('%d match(es)' % len(crawled_content))
    search_results = defaultdict(str)
    regex = re.compile(args.regex_string, re.IGNORECASE)
    for name_list, download_links in crawled_content:
        search_results.update({name.get_text().strip(): parse.urljoin(site['url'], link.get('href')) for name, link in zip(name_list, download_links) if regex.match(name.get_text().strip(), re.IGNORECASE)})
    return search_results


def download(site, args):
    site = load_config('sites')[site]

    validate_url(site['url'])
    validate_url(site['search_path'], path=True)

    search_results = search(site, args)

    for name, link in search_results.items():
        torrent_name = os.path.join(os.path.expanduser(args.download_dir), name + '.torrent')
        if args.pretend:
            print('Name: %s\nLink: %s\n' % (name, link))
        else:
            if link.startswith('magnet:?xt'):
                print('[ERROR] Magnet links not supported yet')
            elif link.endswith('.torrent'):
                with requests.Session() as session:
                    if site['login_required']:
                        session = login(site, args, session=session)
                    torrent_file = session.get(link)
                    if os.path.isfile(torrent_name):
                        print('Download aborted. Torrent file already exists.')
                    else:
                        if not os.path.exists(args.download_dir):
                            try:
                                os.makedirs(args.download_dir)
                            except PermissionError:
                                print('[ERROR] Denied permission to create ' \
                                      'watch folder here: %s' % args.download_dir)
                                exit(77)
                        try:
                            with open(torrent_name, 'wb') as f:
                                f.write(torrent_file.content)
                                print('Torrent added here: ' + torrent_name)
                                print(link)
                        except PermissionError:
                            print('[ERROR] Denied permission to save torrent here: %s'
                                  % args.download_dir)
                            exit(77)
            else:
                print('[ERROR] Download failed. Not a magnet or torrent link.')

    print(str(len(search_results)) + ' matches.')


def run():
    common_parameters = argparse.ArgumentParser(add_help=False)
    common_parameters.add_argument('search_string', type=str)
    common_parameters.add_argument('-r', '--regex_string', type=str, default='.*',
                                   help=''' If necessary, filter the list of
                                   torrents down with a regex string''')
    common_parameters.add_argument('-x', '--pretend', action='store_true')
    common_parameters.add_argument('-n', '--pages', type=int, default=100)
    common_parameters.add_argument('-d', '--download_dir', type=str,
                                   default=os.path.expanduser(load_config('config')['watch_dir']))

    parser = argparse.ArgumentParser(description='Download multiple torrents')
    subparser = parser.add_subparsers()

    for site, values in load_config('sites').items():
        if values['login_required']:
            login_parser = subparser.add_parser(site, help='Login required.', parents=[common_parameters])
            login_parser.add_argument('--username', type=str, nargs='?',
                                      default=values['username'] or None)
            login_parser.add_argument('--password', type=str, nargs='?',
                                      default=values['password'] or None)
            login_parser.set_defaults(func=download)
        else:
            search_parser = subparser.add_parser(site, help='No login required.', parents=[common_parameters])
            search_parser.set_defaults(func=download)

    args = parser.parse_args()

    if len(argv) > 1:
        catch_undefined_credentials(argv[1], args)
        args.func(argv[1], args)
    else:
        parser.print_help()


if __name__ == '__main__':
    run()
