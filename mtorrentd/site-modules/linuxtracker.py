import re


def get_torrent_list(site, soup):
    container = soup.find_all('table')[15]
    download_links = container.find_all(href=re.compile('^magnet*'))
    name_list = container.find_all(title=re.compile('^View details*'))
    return name_list, download_links
