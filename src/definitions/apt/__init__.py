from DefinitionBase import DefinitionBase


info = {"name"   : "apt",
        "author" : "Chris Oliver <excid3@gmail.com>",
        "version": "1.0",
        "class"  : "Apt"}

                
class Apt(DefinitionBase):

    def on_set_architecture(self, architecture):
        print architecture
