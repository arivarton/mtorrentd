#! /usr/bin/env python3

import argparse
import requests
import re
import yaml
import importlib.util
import libtorrent
import tempfile
import shutil
from sys import argv, exit
from os.path import expanduser, join, isfile
from time import sleep
from urllib import parse
from collections import defaultdict
from bs4 import BeautifulSoup


with open('sites.yaml', 'r') as sites:
    try:
        SITE_LIST = yaml.load(sites)
    except yaml.YAMLError as err:
        print(err)


with open('config.yaml', 'r') as config:
    try:
        CONFIG = yaml.load(config)
    except yaml.YAMLError as err:
        print(err)


def _validate_url(url, path=False):
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


def login(site, args, session):
    _validate_url(site['login_path'], path=True)
    payload = {
        'username': args.username,
        'password': args.password
    }
    session.post(parse.urljoin(site['url'], site['login_path']),
                 data=payload)
    return session


def search(site, args):
    # Load site module
    spec = importlib.util.spec_from_file_location(argv[1], join('site_modules', argv[1] + '.py'))
    site_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(site_module)

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
                print('No more results after %d pages\n' % page)
                break
            crawled_content.append((name_list, download_links))
    search_results = defaultdict(str)
    regex = re.compile(args.regex_string)
    for name_list, download_links in crawled_content:
        search_results.update({name.get_text().strip(): parse.urljoin(site['url'], link.get('href')) for name, link in zip(name_list, download_links) if regex.match(name.get_text().strip())})
    return search_results


def download(site, *args):
    site = SITE_LIST[site]

    _validate_url(site['url'])
    _validate_url(site['search_path'], path=True)

    search_results = search(site, *args)

    for name, link in search_results.items():
        torrent_name = join(expanduser(args[0].download_dir), name + '.torrent')
        if args[0].pretend:
            print('Name: %s\nLink: %s\n' % (name, link))
        else:
            if link.startswith('magnet:?xt'):
                temp_dir = tempfile.mkdtemp()
                libt_session = libtorrent.session()
                params = {
                    'save_path': temp_dir,
                    'storage_mode': libtorrent.storage_mode_t(2),
                    'paused': False,
                    'auto_managed': True,
                    'duplicate_is_error': True
                }
                handle = libtorrent.add_magnet_uri(libt_session, link, params)
                while (not handle.has_metadata()):
                    try:
                        sleep(0.1)
                    except KeyboardInterrupt:
                        print("Aborting...")
                        libt_session.pause()
                        print("Cleanup dir " + temp_dir)
                        shutil.rmtree(temp_dir)
                        exit(0)
                libt_session.pause()
                print('Done')
                torrent_info = handle.get_torrent_info()
                torrent_file = libtorrent.create_torrent(torrent_info)
                torrent_name = torrent_info.name() + '.torrent'
                print('Torrent name: ', torrent_name)
                libt_session.remove_torrent(handle)
                shutil.rmtree(temp_dir)
            elif link.endswith('.torrent'):
                with requests.Session() as session:
                    if site['login_required']:
                        session = login(site, *args, session=session)
                    torrent_file = session.get(link)
                    if isfile(torrent_name):
                        print('Download aborted. Torrent file already exists.')
                    else:
                        with open(torrent_name, 'wb') as f:
                            f.write(torrent_file.content)
                            print(torrent_name + '. Downloaded.')
                            print(link)
            else:
                print('Download failed. Not a magnet or torrent link.')

    print(str(len(search_results)) + ' matches.')


def run():
    common_parameters = argparse.ArgumentParser(add_help=False)
    common_parameters.add_argument('search_string', type=str)
    common_parameters.add_argument('-r', '--regex_string', type=str, default='.*',
                                   help=''' If necessary, filter the list of
                                   torrents down with a regex string''')
    common_parameters.add_argument('-x', '--pretend', action='store_true')
    common_parameters.add_argument('-p', '--pages', type=int, default=100)
    common_parameters.add_argument('-d', '--download_dir', type=str,
                                   default=expanduser(CONFIG['watch_dir']))

    parser = argparse.ArgumentParser(description='Download multiple torrents')
    subparser = parser.add_subparsers()

    for site in SITE_LIST:
        if SITE_LIST[site]['login_required']:
            login_parser = subparser.add_parser(site, help='Login required.', parents=[common_parameters])
            login_parser.add_argument('username', type=str, nargs='?',
                                      default=str(SITE_LIST[site]['username']))
            login_parser.add_argument('password', type=str, nargs='?',
                                      default=str(SITE_LIST[site]['password']))
            login_parser.set_defaults(func=download)
        else:
            search_parser = subparser.add_parser(site, help='No login required.', parents=[common_parameters])
            search_parser.set_defaults(func=download)

    args = parser.parse_args()
    args.func(argv[1], args)


if __name__ == '__main__':
    run()
