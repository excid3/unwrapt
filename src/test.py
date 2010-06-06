from DefinitionManager import DefinitionManager

loader = DefinitionManager("definitions")
apt = loader.new_instance("apt")
apt.SetArchitecture("i386")
