import imp
import logging
import os

class DefinitionManager:
    """Definition Manager
    
    Loads the definitions from a folder and manages them
    """

    definitions = {}
    
    def __init__(self, folder):
        """Load all available definitions stored in folder"""
        
        #TODO: User path and variable expansions
        folder = os.path.abspath(folder)
        
        if not os.path.isdir(folder):
            logging.error("Unable to load plugins because '%s' is not a folder" % folder)
            return
        
        # Build list of py files
        to_import = [f for f in os.listdir(folder) if f.endswith(".py")]
        for filename in to_import:
            self.__initialize_def(os.path.join(folder,filename))
                        
    def __initialize_def(self, filename):
        """Attempt to load the definition at filename"""
        try:
            definition = imp.load_source("", filename)
            self.definitions[definition.info["name"]] = definition
        except IOError, e:
            # File error
            logging.error("%s: %s" % (e, filename))
            
        except AttributeError, e:
            # Definition is not built properly
            logging.error(e)

    def new_instance(self, name):
        """Creates a new instance of a definition"""
        definition = self.definitions[name]
        return getattr(definition, definition.info["class"])("FAKE DB INFORMATION")
        
