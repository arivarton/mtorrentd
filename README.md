Still a work in progress.

Usage:

./multi_torrent_downloader.py deildu 'Mr Robot s02' username password -x
./multi_torrent_downloader.py thepiratebay 'Mr Robot s02' -x

The -x parameter is set so the torrents doesn't actually download, it will only print out information about the torrents that were found with the search criteria.
Currently the download of torrents does not work.

./multi_torrent_downloader.py thepiratebay 'Mr Robot ' -x -p 5

The -p parameter overrides the default page count of 3. It will now search for up to 5 pages depending on if there are that many matching torrents.
