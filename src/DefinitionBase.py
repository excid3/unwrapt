#    Unwrapt - cross-platform package system emulator
#    Copyright (C) 2010 Chris Oliver <chris@excid3.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
        




