import os

from DefinitionManager import DefinitionManager


# Make sure this works being launched from any location
__path__ = os.path.dirname(os.path.abspath(__file__))
folder = "%s/definitions" % __path__

# Load definitions from folder
loader = DefinitionManager(folder)

# Instanciate an apt client
apt = loader.new_instance("apt", "database.db")

# Configure the apt client
apt.set_architecture("i386")
