class DefinitionBase:
    def __init__(self, database):
        self.database = database
        
    def SetArchitecture(self, architecture):
        if hasattr(self, "OnSetArchitecture"):
            getattr(self, "OnSetArchitecture")(architecture)
        
    def SetRepositories(self, repositories):
        pass
        
    def Update(self, reporthook):
        """Update"""
        pass
