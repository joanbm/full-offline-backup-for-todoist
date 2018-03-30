# Maintainer: Joan Bruguera Micó <joanbrugueram@gmail.com>
pkgname=todoist-full-offline-backup-git
_gitname="todoist-full-offline-backup"
pkgver=0.1
pkgrel=1
pkgdesc="Small, dependency-less Python script to make a backup of all Todoist tasks and attachments that is accessible offline"
arch=('any')
url="https://github.com/joanbm/todoist-full-offline-backup"
license=('GPLv3')
depends=('python' 'python-setuptools')
makedepends=('git' 'python-setuptools')
provides=('todoist-full-offline-backup')
conflicts=('todoist-full-offline-backup')
options=(!emptydirs)
source=('git+https://github.com/joanbm/todoist-full-offline-backup.git')
sha256sums=('SKIP')

package() {
  cd "$srcdir/$_gitname"
  python setup.py install --root="$pkgdir/" --optimize=1
}
