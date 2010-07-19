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


#from sqlalchemy import create_engine
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import sessionmaker


#Base = declarative_base()


def callback(func):
    """
        Our decorator for giving on_<function name> callbacks to definitions
        
        The DefinitionBase functions will do their work, and then the real
        defintion will do its work. The return values from the definition will
        be the results returned.
    """
    
    def callback_func(*args, **kwargs):
        # Call the base function
        func(*args, **kwargs)
        
        # Call callback if available
        name = "on_%s" % func.__name__
        if hasattr(args[0], name):
            return getattr(args[0], name)(*args[1:], **kwargs)

    return callback_func
        

class DefinitionBase:
    """
        DefinitionBase
        
        This is the base class for all definitions and provides some default
        functionality as well as providing callbacks for definitions to
        implement their code. This helps to make sure that functionality is not
        overridden when implementing a new definition.
    """
    
    
    @callback
    def __init__(self, database=":memory:"):
        """
            __init__([database])
            
            - database is a filename for the defintion data to be stored. If
              omitted, the database will be stored in memory only and will not
              be saved.
              
            For example:
              
            client = loader.new_instance("apt", "unwrapt.db")
        """
        
        #self.database = database
        #engine = create_engine("sqlite:///%s" % database)
        #Base.metadata.create_all(engine)
        
        #Session = sessionmaker(bind=engine)
        #self.session = Session()
	
        pass
	

    #def __del__(self):
    #    self.session.commit()
    #    self.session.close()


    @callback
    def set_architecture(self, architecture):
        """
            set_architecture(architecture)
            - architecture is the platform architecture of the machine.
              Supported types are amd64, armel, i386, ia64, powerpc, sparc
               
            For example:
               
            client.set_architecture("amd64")
        """
          
        self.architecture = architecture
        
        
    @callback
    def set_proxy(self, proxy, username=None, password=None):
        """
            set_proxy(proxies, [username, [password]])
            - proxy is a dictionary of the protocols and their url's.
             
            - The last two parameters for proxy authentication and are 
              optional. If omitted, no proxy authentication will be attempted.
               
            For example:
               
            proxies = {'http': 'http://www.someproxy.com:3128'}
            client.set_proxy(proxies, "default", "admin")

        """

        pass
    
    
    @callback
    def set_repositories(self, repositories):
        """
            set_repositories(repositories)
            
            - repositories is a list of "deb url dist section" lines taken
              straight from the machine's sources.list file.
              
            For example:
              
            f = open("/etc/apt/sources.list", "rb")
            client.set_repositories(f.readlines())
            f.close()
        """
        
        self.repositories = repositories
        

    @callback
    def set_status(self, status):
        """
            set_status(status)
            
            - status is the filename containing the package statuses
            
            For example:
            
            client.set_status("/var/lib/dpkg/status")
        """
        
        pass

    @callback        
    def update(self, reporthook=None):
        """
            update(reporthook=None)
            
            - reporthook is a function name that will be called to report the 
              progress of files as they are being downloaded. If omitted, the
              function will print out progress into the console.
        
            For example:
            
            client.update()
        """
        
        pass

        
    @callback
    def get_latest_binary(self, package):
        """
            get_latest_binary(package)
            
            - package is the name of the package. 
            
            This function will return the newest version of the package 
            available.
              
            For example:
            
            metadata = client.get_latest_binary("firefox")
        """
        
        pass
        

    @callback
    def get_available_binary_versions(self, package):
        """
            get_available_binary_versions(package)
            
            - package is the name of the package. 
            
            This function will return a list of available package versions.
            
            For example:
            
            versions = client.get_available_binary_versions("firefox")
        """
        
        pass

       
    @callback
    def mark_package(self, package):
        """
            mark_package(package)
            
            - package is the name of the package.
            
            This function will mark a package and any necessary dependencies to
            be downloaded when apply_changes is called.
            
            For example:
            
            client.mark_package("firefox")
        """
        
        pass
        
    
    @callback
    def apply_changes(self, reporthook=None):
        """
            apply_changes(reporthook=None)
            
            - reporthook is a function name that will be called to report the 
              progress of files as they are being downloaded. If omitted, the
              function will print out progress into the console.
            
            This function will download marked packages and change their status
            from "to be downloaded" to "to be installed".
            
            For example:
            
            client.apply_changes()
            
        """
        
        pass
        
        
    @callback
    def save_status(self, status):
        """
            save_status(status)
            
            - status is the filename where the status information will be
              written.
              
            This function will write the status information to file. This is
            used primarily for saving packages that are marked as
            "to be downloaded" or "to be installed" so they may be retrieved at
            a later time.
            
            When implementing this function, it should write data in EXACTLY
            the same format as it was read in from the operating system.
            
            For example:
            
            client.save_status("status")
        """
        
        pass
        
        
    @callback
    def install(self, reporthook=None):
        """
            install(reporthook=None)
            
            - reporthook is the name of a function that will report the
              progress of installation.
              
            This function will install the packages that are marked as
            "to be installed"
            
            For example:
            
            client.install()
        """
        
        pass    
        
        
