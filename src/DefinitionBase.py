from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def callback(func):


    def callback_func(*args, **kwargs):
        # Call the base function
        func(*args, **kwargs)
        
        # Call callback if available
        name = "on_%s" % func.__name__
        if hasattr(args[0], name):
            return getattr(args[0], name)(*args[1:], **kwargs)


    return callback_func
        

class DefinitionBase:
    
    
    @callback
    def __init__(self, database):
        self.database = database
        engine = create_engine("sqlite:///%s" % database)
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        self.session = Session()


    def __del__(self):
        self.session.commit()
        self.session.close()


    @callback
    def set_architecture(self, architecture):
        self.architecture = architecture
        
    
    @callback
    def set_repositories(self, repositories):
        self.repositories = repositories
        

    @callback        
    def update(self, reporthook):
        pass

        
    @callback
    def get_available_binary_packages(self):
        pass
        

    @callback
    def get_available_binary_versions(self, package):
        pass


    @callback        
    def get_binary_dependencies(self, package):
        pass
        




