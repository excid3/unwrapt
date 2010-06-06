from DefinitionBase import DefinitionBase


info = {"name"   : "apt",
        "author" : "Chris Oliver <excid3@gmail.com>",
        "version": "1.0",
        "class"  : "Apt"}

                
class Apt(DefinitionBase):


#    def on___init__(self, database):
              

    def on_set_architecture(self, architecture):
        pass
        
    
    def on_set_repositories(self, repositories):
        pass
        

    def on_update(self, reporthook):
        pass

        
    def on_get_available_binary_packages(self):
        pass
        

    def on_get_available_binary_versions(self, package):
        pass


    def on_get_binary_dependencies(self, package):
        pass
        

