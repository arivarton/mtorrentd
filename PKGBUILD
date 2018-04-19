# Maintainer: Andri Viðar Tryggvason <packager@arivarton.com>
pkgname=mtorrentd
pkgver=0.3.2
pkgrel=1
pkgdesc='Search torrent websites and download .torrent files in terminal.'
arch=('any')
url='https://github.com/arivarton/multi-torrent-downloader'
license=('GPL3')
depends=('python3'
         'python-yaml'
         'python-requests'
         'python-beautifulsoup4'
        )
source=("$pkgname-$pkgver.tar.gz"::https://github.com/arivarton/multi-torrent-downloader/archive/v"$pkgver".tar.gz)
sha256sums=('8c452833c48ee83b5d5b544b2ae3a7db250f88aae4f7c85628c428a1fb143c64')
package() {
    cd "${srcdir}/$pkgname-$pkgver"
    python3 setup.py install --prefix=/usr --root="$pkgdir/"
    install -Dm755 mtorrentd.py "${pkgdir}/usr/bin/mtorrentd"
}
