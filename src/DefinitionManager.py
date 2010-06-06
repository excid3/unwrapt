import logging
import os
import sys


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
        
        # Build list of folders in directory
        to_import = [f for f in os.listdir(folder) \
                     if os.path.isdir(os.path.join(folder,f))]
                     
        for module in to_import:
            self.__initialize_def(module)
        
                        
    def __initialize_def(self, module):
        """Attempt to load the definition"""
        name = "definitions.%s" % module
        __import__(name)
        definition = sys.modules[name]
        self.definitions[definition.info["name"]] = definition
        

    def new_instance(self, name):
        """Creates a new instance of a definition"""
        definition = self.definitions[name]
        return getattr(definition, definition.info["class"])("FAKE DB INFORMATION")
        
        
