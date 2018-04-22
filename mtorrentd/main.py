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
from .core import (load_site_module, download_torrent, download_magnet2torrent,
                   session_login)
from .helpers import catch_undefined_credentials


def search(site, args):
    site_module = load_site_module(argv[1])

    with requests.Session() as session:
        if site['login_required']:
            session = session_login(site, args.username, args.password, session)
        crawled_content = list()
        for page in range(args.pages):
            search_url = parse.urljoin(site['url'],
                                                    site['search_path'] +
                                                    args.search_string +
                                                    site['page_path'] +
                                                    str(page) +
                                                    site.get('append_path', ''))
            search_page = session.get(search_url)
            soup = BeautifulSoup(search_page.text, 'html.parser')
            name_list, download_links = site_module.get_torrent_list(site, soup)
            if not name_list or not download_links:
                print('No more results after %d page(s)\n' % page)
                break
            crawled_content.append((name_list, download_links))
    search_results = defaultdict(str)
    regex = re.compile(args.regex_string, re.IGNORECASE)
    for name_list, download_links in crawled_content:
        search_results.update({name.get_text().strip(): parse.urljoin(site['url'], link.get('href')) for name, link in zip(name_list, download_links) if regex.match(name.get_text().strip(), re.IGNORECASE)})
    return search_results


def download(site, args):
    site = load_config('sites')[site]

    search_results = search(site, args)

    with requests.Session() as session:
        if site['login_required']:
            session = session_login(site, args.username, args.password, session=session)
        for name, link in search_results.items():
            if args.pretend:
                print('Name: %s\nLink: %s\n' % (name, link))
            else:
                # Create directory if missing
                if not os.path.exists(args.download_dir):
                    try:
                        os.makedirs(args.download_dir)
                    except PermissionError:
                        print('[ERROR] Denied permission to create ' \
                                'watch folder here: %s' % args.download_dir)
                        exit(77)
                if link.startswith('magnet:?xt'):
                    download_magnet2torrent(link, args.download_dir, name)
                elif link.endswith('.torrent'):
                    download_torrent(link, args.download_dir, name, session)
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
    common_parameters.add_argument('-p', '--pages', type=int, default=100)
    common_parameters.add_argument('-d', '--download_dir', type=lambda path: os.path.expanduser(path),
                                   default=os.path.expanduser(load_config('config')['watch_dir']))

    parser = argparse.ArgumentParser(description='Download multiple torrents')
    subparser = parser.add_subparsers()

    sites_config = load_config('sites')

    for site, values in sites_config.items():
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


    if len(argv) > 1:
        if argv[1].startswith('magnet:?xt') or argv[1].endswith('.torrent'):
            single_torrent_parser = argparse.ArgumentParser(add_help=False)
            single_torrent_parser.add_argument('torrent', type=str)
            single_torrent_parser.add_argument('-d', '--download_dir', type=lambda path: os.path.expanduser(path),
                                               default=os.path.expanduser(load_config('config')['watch_dir']))
            args = single_torrent_parser.parse_args()
            if argv[1].startswith('magnet:?xt'):
                download_magnet2torrent(args.torrent, args.download_dir)
            elif argv[1].endswith('.torrent'):
                download_torrent(args.torrent, args.download_dir)
        else:
            args = parser.parse_args()

            if sites_config[argv[1]]['login_required']:
                catch_undefined_credentials(argv[1], args)

            args.func(argv[1], args)
    else:
        parser.print_help()


if __name__ == '__main__':
    run()
