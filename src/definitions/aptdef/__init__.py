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


import gzip
import logging
import os
import pycurl
import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.schema import UniqueConstraint

from DefinitionBase import DefinitionBase, Base
from Download import EasyCurl


info = {"name"   : "apt",
        "author" : "Chris Oliver <excid3@gmail.com>",
        "version": "1.0",
        "class"  : "Apt"}


#TODO: Move this code to proper library location
def url_join(first, last):
    """ Returns full URL """
    if first.endswith('/'):
        if last.startswith('/'): return first + last[1:]
        else:                    return first + last
    else:
        if last.startswith('/'): return first + last
        else:                    return first + '/' + last


class Repository(Base):


    __tablename__ = "apt_repositories"
    
    id = Column(Integer, primary_key=True)
    rtype = Column(String)
    url = Column(String)
    dist = Column(String)
    section = Column(String)

    # Only allow completely unique repository entries
    __table_args__ = (UniqueConstraint("rtype", "url", "dist", "section"),{})
    
    
    def __init__(self, rtype, url, dist, section):
        self.rtype = rtype
        self.url = url
        self.dist = dist
        self.section = section
        
    
    def to_url(self):
        return url_join(self.url, url_join("dists", url_join(self.dist, self.section)))
    
                
class Package(Base):


    __tablename__ = "apt_packages"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    version = Column(String)
    source = Column(Integer, ForeignKey("apt_repositories.id"))

    # Only allow completely unqiue package entries
    __table_args__ = (UniqueConstraint("name", "version", "source"))
    
    
    def __init__(self, name, version, source):
        self.name = name
        self.version = version
        self.source = source
    
                
class Apt(DefinitionBase):
    
    
    supported = ["amd64", "armel", "i386", "ia64", "powerpc", "sparc"]
    

#    def on___init__(self, database):
             

    def on_set_architecture(self, architecture):
        if not architecture in self.supported:
            raise AttributeError, "Unsupported architecture"

        self.architecture = "binary-%s" % architecture
        
    
    def on_set_repositories(self, repositories):
        #TODO: if self.repositories
        #          delete each table entry
        # This will need to actually find unlinked repository entries for
        # use in keryx-web. Deleting the Repository entries will force the
        # other projects (who might use the same entry) to recreate it
        
        for repo in self.__iter_repositories():
            logging.info("Using repository %i" % repo.id)
                    
        self.session.commit()

    
    def __iter_repositories(self):
        """Used for iterating through the repository entries
        This function yields Repository objects and creates entries as needed
        """
        for repo in self.repositories:
            rtype, url, dist, sections  = repo.split(None, 3)
            for section in sections.split():
                try:
                    repo = self.session.query(Repository) \
                                  .filter(Repository.rtype == rtype) \
                                  .filter(Repository.url == url) \
                                  .filter(Repository.dist == dist) \
                                  .filter(Repository.section == section) \
                                  .one()
                except:
                    self.session.add(Repository(rtype, url, dist, section))
                    repo = self.session.query(Repository) \
                                  .filter(Repository.rtype == rtype) \
                                  .filter(Repository.url == url) \
                                  .filter(Repository.dist == dist) \
                                  .filter(Repository.section == section) \
                                  .one()
                yield repo


    def on_update(self, reporthook=None):
        #TODO: When do we clear the repository files and require fresh?
        #      We should use the expires HTTP header and check timestamps

        ec = EasyCurl()
        
        if not reporthook:
            reporthook = ec.textprogress

        # This is a list of files we downloaded and now need to parse
        downloaded = []
        for repo in self.__iter_repositories():

            # Build the strings
            url = url_join(repo.to_url(), 
                           url_join(self.architecture, "Packages"))
            filename = os.path.join("downloads/lists",
                                    url.split("//")[1].replace("/", "_")) 
            display_name = "Repository => %s / %s" % (repo.dist, repo.section)
            # Use str() because pycurl does not support unicode strings
            gz = str("%s.gz" % url)
            
            #logging.debug(display_name)
            #logging.debug(filename)
            logging.debug(gz)

            # If the download directory does not exist, create it
            if not os.path.exists("downloads/lists"):
                os.makedirs("downloads/lists")

            # Download
            try:
                gz_file = "%s.gz" % filename
                self.__download(ec, 
                                gz, 
                                gz_file, 
                                display_name, 
                                reporthook)
                downloaded.append(gz_file)
            except Exception, e:
                #TODO: Add support for bz2 and uncompressed Packages files
                raise Exception, e

        # Now parse each file, extracting as necessary        
            # Insert items into database


    def __download(self, curl, url, filename, display_name, progress):

            try:
                curl.perform(url, 
                             filename,
                             display_name,
                             progress=progress)
                           
            except KeyboardInterrupt:
                # Download fully transfered
                raise KeyboardInterrupt
                
            except pycurl.error, e:

                if e.args[0] == 18:
                    # This exception is actually fine. It means that we are
                    # trying to download a file that is already 100% complete 
                    sys.stdout.write("\n")
                
                elif e.args[0] == 42:
                    # Callback aborted
                    raise KeyboardInterrupt
                    
                else:
                    raise IOError, "Problem downloading file. Delete %s and " \
                                   "start again." % filename
            
                    
#    def on_get_available_binary_packages(self):
#        pass
        

#    def on_get_available_binary_versions(self, package):
#        pass


#    def on_get_binary_dependencies(self, package):
#        pass
        

