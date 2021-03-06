"""Core functions of mtorrentd."""
import os
import importlib.util
import libtorrent
import tempfile
import shutil
import requests
from urllib import parse

from sys import exit
from time import sleep

from .paths import SITE_MODULES



def session_login(site, username, password, session):
    """When login is needed for session."""
    payload = {
        'username': username,
        'password': password
    }
    session.post(parse.urljoin(site['url'], site['login_path']),
                 data=payload)

    return session


def load_site_module(site):
    """Load module to use it as a function."""
    user_module = os.path.join(SITE_MODULES['user'], site + '.py')
    system_module = os.path.join(SITE_MODULES['system'], site + '.py')
    if os.path.isfile(user_module):
        spec = importlib.util.spec_from_file_location(site, user_module)
    elif os.path.isfile(system_module):
        spec = importlib.util.spec_from_file_location(site, system_module)
    else:
        print('Site module not found. Check github for documentation and create a new site module here: %s' %(SITE_MODULES['user']))
        exit(73)
    site_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(site_module)

    return site_module


def write_torrent_to_file(full_torrent_path, torrent_content, download_dir):
    if os.path.isfile(full_torrent_path):
        print('Download aborted. Torrent file already exists.')
    try:
        with open(full_torrent_path, "wb") as f:
            f.write(torrent_content)
            print('Torrent added here: ' + full_torrent_path)
    except PermissionError:
        print('[ERROR] Denied permission to save torrent here: %s'
                % download_dir)
        exit(77)
    except FileNotFoundError as err:
        print('[ERROR] Create the directory to store the torrent file in.', err)
        exit(77)


def download_torrent(torrent_link, download_dir, torrent_name=None, session=None) -> None:
    """Download .torrent from link."""
    if torrent_name:
        full_torrent_path = os.path.join(download_dir, torrent_name + '.torrent')
    else:
        torrent_name = torrent_link.split('/')
        torrent_name = torrent_name[len(torrent_name) - 1]
        full_torrent_path = os.path.join(download_dir, torrent_name)

    if session:
        torrent_file = session.get(torrent_link)
    else:
        with requests.Session() as session:
            torrent_file = session.get(torrent_link)

    write_torrent_to_file(full_torrent_path, torrent_file.content, download_dir)


def download_magnet2torrent(torrent_link, download_dir, torrent_name=None) -> None:
    """Download magnet link."""
    tempdir = tempfile.mkdtemp()
    libtorrent_session = libtorrent.session()
    params = {
        'url': torrent_link,
        'save_path': tempdir,
        'storage_mode': libtorrent.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True
    }
    handle = libtorrent_session.add_torrent(params)

    print("Downloading Metadata (this may take a while)")
    while (not handle.has_metadata()):
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Aborting...")
            libtorrent_session.pause()
            print("Cleanup dir " + tempdir)
            shutil.rmtree(tempdir)
            exit(0)
    libtorrent_session.pause()
    print("Done")

    if torrent_name:
        full_torrent_path = os.path.join(download_dir, torrent_name + '.torrent')
    else:
        torrent_name = handle.torrent_file().name()
        full_torrent_path = os.path.join(download_dir, torrent_name + '.torrent')

    torrent_info = handle.get_torrent_info()
    torrent_file = libtorrent.create_torrent(torrent_info)

    write_torrent_to_file(full_torrent_path, libtorrent.bencode(torrent_file.generate()), download_dir)

    print("Saved! Cleaning up dir: " + tempdir)
    libtorrent_session.remove_torrent(handle)
    shutil.rmtree(tempdir)
