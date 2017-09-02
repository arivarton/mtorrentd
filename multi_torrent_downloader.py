#! /usr/bin/env python3

import argparse
import requests
import re
import yaml
import importlib.util
from sys import argv
from os.path import expanduser, join
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


def search(site, args, payload=False):
    # Load site module
    spec = importlib.util.spec_from_file_location(argv[1], join('site_modules', argv[1] + '.py'))
    site_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(site_module)

    with requests.Session() as session:
        if payload:
            session.post(parse.urljoin(site['url'], site['login_path']),
                         data=payload)
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

    validate_url(site['url'])
    validate_url(site['search_path'], path=True)

    search_results = search(site, *args)

    if args[0].pretend:
        for name, link in search_results.items():
            print('Name: %s\nLink: %s\n' % (name, link))
    else:
        for name, link in search_results:
            if link.startswith('magnet:?xt'):
                print('Magnet link')
            else:
                print('Not magnet link')


def login(site, args):
    validate_url(SITE_LIST[site]['login_path'], path=True)
    payload = {
        'username': args.username,
        'password': args.password
    }
    download(site, args, payload)


def run():
    common_parameters = argparse.ArgumentParser(add_help=False)
    common_parameters.add_argument('search_string', type=str)
    common_parameters.add_argument('-r', '--regex_string', type=str, default='.*',
                                   help=''' If necessary, filter the list of
                                   torrents down with a regex string''')
    common_parameters.add_argument('-x', '--pretend', action='store_true')
    common_parameters.add_argument('-p', '--pages', type=int, default=3)
    common_parameters.add_argument('-d', '--download_dir', type=str,
                                   default=expanduser(CONFIG['watch_dir']))

    parser = argparse.ArgumentParser(description='Download multiple torrents')
    subparser = parser.add_subparsers()

    for site in SITE_LIST:
        if SITE_LIST[site]['login_required']:
            login_parser = subparser.add_parser(site, help='Enter login info.', parents=[common_parameters])
            login_parser.add_argument('username', type=str)
            login_parser.add_argument('password', type=str)
            login_parser.set_defaults(func=login)
        else:
            search_parser = subparser.add_parser(site, help='No login required.', parents=[common_parameters])
            search_parser.set_defaults(func=download)

    args = parser.parse_args()
    args.func(argv[1], args)


if __name__ == '__main__':
    run()
