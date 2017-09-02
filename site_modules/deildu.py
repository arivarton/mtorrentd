import re


def get_torrent_list(site, soup):
    container = soup.find(class_='torrentlist')
    download_links = container.find_all(href=re.compile('download.php*'))
    name_list = container.find_all(href=re.compile('^details.php\?id=[0-9]{6}$'))
    return name_list, download_links
