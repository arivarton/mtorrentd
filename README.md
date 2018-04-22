# Multi Torrent Downloader

Search several torrent sites for torrents and download one or more of them at once using only the terminal. For example searching for specific episodes from a series using regex as a filter.

Note that this doesn't actually download the files that the torrent contains, only the .torrent file.

Supports both magnet links and regular .torrent files.


# Usage
### Download single torrents
```
mtorrentd [-h] [-d DOWNLOAD_DIR] torrent

positional arguments:
  torrent

optional arguments:
  -h, --help            show this help message and exit
  -d DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR

`mtorrentd <https://site.com/torrents/torrentname.torrent>`
or
`mtorrentd <magnet:?xt>`
```
### Search through torrent sites
```
mtorrentd [-h] {sometracker,othertracker,thirdtracker} ...

Download multiple torrents

positional arguments:
  {sometracker,othertracker,thirdtracker}
    sometracker           No login required.
    othertracker          No login required.
    thirdtracker          Login required.

optional arguments:
  -h, --help            show this help message and exit
```
```
mtorrentd sometracker [-h] [-r REGEX_STRING] [-x] [-p PAGES]
                                 [-d DOWNLOAD_DIR]
                                 search_string

positional arguments:
  search_string

optional arguments:
  -h, --help            show this help message and exit
  -r REGEX_STRING, --regex_string REGEX_STRING
                        If necessary, filter the list of torrents down with a
                        regex string
  -x, --pretend
  -p PAGES, --pages PAGES
  -d DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
```
```
mtorrentd thirdtracker [-h] [-r REGEX_STRING] [-x] [-p PAGES]
                           [-d DOWNLOAD_DIR] [--username [USERNAME]]
                           [--password [PASSWORD]]
                           search_string

positional arguments:
  search_string

optional arguments:
  -h, --help            show this help message and exit
  -r REGEX_STRING, --regex_string REGEX_STRING
                        If necessary, filter the list of torrents down with a
                        regex string
  -x, --pretend
  -p PAGES, --pages PAGES
  -d DOWNLOAD_DIR, --download_dir DOWNLOAD_DIR
  --username [USERNAME]
  --password [PASSWORD]
```

#### Pretend download
The -x parameter is set so the torrents doesn't actually download, it will only print out information about the torrents that were found with the search criteria.
##### Examples
`mtorrentd deildu 'Mr Robot s02' username password -x`
`mtorrentd thepiratebay 'Mr Robot s02' -x`

#### Download
To download torrents remove the -x parameter. Also set the directory the torrents should be downloaded to in config.yaml.
#### Parameters
##### -p
The -p parameter overrides the default maximum page count of 100.
###### Examples
`mtorrentd thepiratebay 'Mr Robot ' -x -p 5`
##### -r
The -r parameter is for regex and will restrict the found torrents based on it.
###### Examples
`mtorrentd thepiratebay 'Mr Robot' -x -r '.*[sS]02.*'`
##### -d
Override the download directory.
###### Examples
`mtorrentd thepiratebay 'Mr Robot' -d ~/.my_torrents`


#### Config files
##### sites.yaml
Under each site these are the options that can be configured:
```
login_required (required)
username
password
login_path
page_path (required)
search_path (required)
append_path
url (required)
```
##### config.yaml
Configurable options:
```
watch_dir
```


#### Install
##### Packaged
Get it from the AUR in Archlinux.
##### Manual
`python3 setup.py install`
##### Directly from directory
It's also possible to run directly from ./mtorrentd.py just make sure dependencies are installed.


#### Dependencies
- pyyaml
- requests
- bs4
- libtorrent
