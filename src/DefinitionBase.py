def callback(func):


    def callback_func(*args, **kwargs):
        # Call the base function
        func(*args, **kwargs)
        
        # Call callback if available
        name = "on_%s" % func.__name__
        if hasattr(args[0], name):
            getattr(args[0], name)(*args[1:], **kwargs)


    return callback_func
        

class DefinitionBase:


    functions = {}
    
    @callback
    def __init__(self, database):
        self.database = database
              

    @callback
    def set_architecture(self, architecture):
        pass
        
        
    def set_repositories(self, repositories):
        pass
        
        
    def update(self, reporthook):
        pass
        

    def get_available_binary_packages(self):
        pass
        

    def get_available_binary_versions(self, package):
        pass

        
    def get_binary_dependencies(self, package):
        pass
        
        
