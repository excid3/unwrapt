#    Unwrapt - cross-platform package system emulator
#    Copyright (C) 2010 Chris Oliver <chris@excid3.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os

from DefinitionManager import DefinitionManager

logging.basicConfig(level=logging.DEBUG)

# Make sure this works being launched from any location
__path__ = os.path.dirname(os.path.abspath(__file__))
folder = "%s/definitions" % __path__

# Load definitions from folder
loader = DefinitionManager(folder)

# Instanciate an apt client
apt = loader.load("apt")

# Set proxy and authentication if needed
#apt.set_proxy({"http": "http://192.168.1.100:3128"}, "username", "password")

# Configure the apt client
apt.set_architecture("amd64")

apt.set_status("/var/lib/dpkg/status")

apt.set_repositories([
"deb http://us.archive.ubuntu.com/ubuntu/ lucid main restricted",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid-updates main restricted",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid universe",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid-updates universe",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid multiverse",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid-updates multiverse",
"deb http://security.ubuntu.com/ubuntu lucid-security main restricted",
"deb http://security.ubuntu.com/ubuntu lucid-security universe",
"deb http://security.ubuntu.com/ubuntu lucid-security multiverse",
"deb http://archive.canonical.com/ lucid partner",
"deb http://download.virtualbox.org/virtualbox/debian lucid non-free",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid-proposed restricted main multiverse universe",
"deb http://us.archive.ubuntu.com/ubuntu/ lucid-backports restricted main multiverse universe"
])

print "%i available packages" % len(apt.get_available_package_names())

#apt.update(directory="/var/lib/apt/lists", download=False)

apt.update()

#print "%i available packages" % len(apt.get_available_package_names())

#print len(apt.get_available_package_names())

# Get a list of available versions of a package
versions = apt.get_available_binary_versions("abiword")
#print versions

# Get the newest version of a package
package = apt.get_latest_binary("firefox")
#print package

# Get a list of dependencies of the package and set them all to be installed
# Throws an exception because the package is already installed and has a status
# Keryx is only good for downloading new packages and updated ones
try:
    apt.mark_package(package)
except AttributeError, e:
    print e

package = apt.get_latest_binary("abiword")
apt.mark_package(package)

size = apt.get_changes_download_size()
print "Need to get %sB of archives." % size[0]

apt.apply_changes()

apt.save_changes("keryx_status")

apt.set_status("keryx_status")

status = apt.get_package_status("abiword")
print "abiword is %s" % status

#apt.install("downloads")

#print "Cancelling changes"
#apt.cancel_changes(downloads=True, installs=True)

#status = apt.get_package_status("abiword")
#print "abiword is %s" % status

count = 0
for item in apt.get_upgrades():
    count += 1
    print "%s has a newer version of %s" % (item["Package"], item["Version"])

print "%i packages upgradable" % count
