## Still a work in progress.

Magnet torrents aren't working correctly yet.

Contributors are welcome.

# Usage

### Pretend download

The -x parameter is set so the torrents doesn't actually download, it will only print out information about the torrents that were found with the search criteria.

##### Examples
`./multi_torrent_downloader.py deildu 'Mr Robot s02' username password -x`

`./multi_torrent_downloader.py thepiratebay 'Mr Robot s02' -x`

----

### Download

To download torrents remove the -x parameter. Also set the directory the torrents should be downloaded to in config.yaml.

----

### Parameters

#### -p
The -p parameter overrides the default page count of 3. It will now search for up to 5 pages depending on if there are that many matching torrents.
##### Examples
`./multi_torrent_downloader.py thepiratebay 'Mr Robot ' -x -p 5`

#### -r
The -r parameter is for regex and will restrict the found torrents based on it.
##### Examples
`./multi_torrent_downloader.py thepiratebay 'Mr Robot' -x -r '.*[sS]02.*'`

#### -d
Override the download directory.
##### Examples
`./multi_torrent_downloader.py thepiratebay 'Mr Robot' -d ~/.my_torrents`
