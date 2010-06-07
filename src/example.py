import os

from DefinitionManager import DefinitionManager

import logging
logging.basicConfig(level=logging.DEBUG)

# Make sure this works being launched from any location
__path__ = os.path.dirname(os.path.abspath(__file__))
folder = "%s/definitions" % __path__

# Load definitions from folder
loader = DefinitionManager(folder)

# Instanciate an apt client
apt = loader.new_instance("apt", "database.db")

# Configure the apt client
apt.set_architecture("i386")

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
])
