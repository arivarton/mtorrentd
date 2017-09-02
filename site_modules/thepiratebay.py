import re


def get_torrent_list(site, soup):
    container = soup.find(id='main-content')
    download_links = container.find_all(href=re.compile('^magnet*'))
    name_list = container.find_all(class_='detName')
    return name_list, download_links
