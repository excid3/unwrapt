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
        
        # Append the folder because we need straight access
        sys.path.append(folder)
        
        # Build list of folders in directory
        to_import = [f for f in os.listdir(folder) if not f.endswith(".pyc")]
                     
        # Do the actual importing
        for module in to_import:
            self.__initialize_def(module)
        
                        
    def __initialize_def(self, module):
        """Attempt to load the definition"""

        # Import works the same for py files and package modules so strip!
        if module.endswith(".py"):
            name = module [:3]
        else:
            name = module
        
        # Do the actual import
        __import__(name)
        definition = sys.modules[name]

        # Add the definition only if the class is available
        if hasattr(definition, definition.info["class"]):
            self.definitions[definition.info["name"]] = definition
            logging.info("Loaded %s" % name)
        

    def new_instance(self, name, *args, **kwargs):
        """Creates a new instance of a definition
        name - name of the definition to create
        
        any other parameters passed will be sent to the __init__ function
        of the definition, including those passed by keyword
        """
        definition = self.definitions[name]
        return getattr(definition, definition.info["class"])(*args, **kwargs)
        
        
