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
sha256sums=('5a23037e8ea66685748b98af3f2efc258e80264ece6e881d5051b57b7d4acedf')
package() {
    cd "${srcdir}/$pkgname-$pkgver"
    python3 setup.py install --prefix=/usr --root="$pkgdir/"
    install -Dm755 mtorrentd.py "${pkgdir}/usr/bin/mtorrentd"
}
