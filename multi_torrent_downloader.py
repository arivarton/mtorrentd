#! /usr/bin/env python3

import argparse
import requests
import re
import yaml
from sys import argv
from urllib import parse
from pathlib import Path
from os.path import join
from collections import defaultdict
from bs4 import BeautifulSoup


with open('config.yaml', 'r') as config:
    try:
        torrent_site_list = yaml.load(config)
    except yaml.YAMLError as err:
        print(err)


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


def get_torrent_list(site, args, payload=False):
    with requests.Session() as session:
        if payload:
            session.post(parse.urljoin(site['url'], site['login_path']),
                         data=payload)
        crawled_content = list()
        for page in range(args.pages):
            search_page = session.get(parse.urljoin(site['url'],
                                                    site['search_path'] +
                                                    args.search_string +
                                                    site['page_path'] + str(page)))
            soup = BeautifulSoup(search_page.text, 'html.parser')
            download_links = soup.find(class_='torrentlist').find_all(href=re.compile(site['download_regex']))
            name_list = soup.find(class_='torrentlist').find_all(href=re.compile(site['name_regex']))
            crawled_content.append((name_list, download_links))
    search_results = defaultdict(str)
    regex = re.compile(args.regex_string)
    for name_list, download_links in crawled_content:
        # Necessary for the regex match
        search_results.update({name.get_text().strip(): parse.urljoin(site['url'], link.get('href')) for name, link in zip(name_list, download_links) if regex.match(name.get_text().strip())})
    if args.pretend:
        for key, val in search_results.items():
            print('Name: %s\nLink: %s\n' % (key, val))
    return search_results


def download_torrents(site, *args):
    site = torrent_site_list[site]

    validate_url(site['url'])
    validate_url(site['search_path'], path=True)

    get_torrent_list(site, *args)


def login(site, args):
    validate_url(torrent_site_list[site]['login_path'], path=True)
    payload = {
        'username': args.username,
        'password': args.password
    }
    download_torrents(site, args, payload)


def run():
    common_parameters = argparse.ArgumentParser(add_help=False)
    common_parameters.add_argument('search_string', type=str)
    common_parameters.add_argument('-r', '--regex_string', type=str, default='.*',
                                   help=''' If necessary, filter the list of
                                   torrents down with a regex string''')
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
    args.func(argv[1], args)


if __name__ == '__main__':
    run()
