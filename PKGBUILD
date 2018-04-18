# Maintainer: Andri Viðar Tryggvason <packager@arivarton.com>
pkgname=mtorrentd
pkgver=0.3.2
pkgrel=1
pkgdesc='Search torrent websites and download .torrent files in terminal.'
arch=('any')
url='https://github.com/arivarton/multi-torrent-downloader'
license=('GPL3')
depends=('python3'
         'python-requests'
         'python-beautifulsoup4'
        )
source=("$pkgname-$pkgver.tar.gz"::https://github.com/arivarton/multi-torrent-downloader/archive/v"$pkgver".tar.gz)
sha256sums=('4ca16ec75967d67c4a03900df029f4755ba95a3421010ea259ebe2d253c3e72c')
package() {
    cd "${srcdir}/$pkgname-$pkgver"
    python3 setup.py install --prefix=/usr --root="$pkgdir/"
    install -Dm755 mtorrentd.py "${pkgdir}/usr/bin/mtorrentd"
}
