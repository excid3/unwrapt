from DefinitionBase import DefinitionBase, Base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.schema import UniqueConstraint


info = {"name"   : "apt",
        "author" : "Chris Oliver <excid3@gmail.com>",
        "version": "1.0",
        "class"  : "Apt"}


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

        self.database = "binary-%s" % architecture
        
    
    def on_set_repositories(self, repositories):
        for repo in repositories:
            rtype, url, dist, sections = repo.split(None, 3)
            for section in sections.split():
                try:
                    self.session.query(Repository) \
                                  .filter(Repository.rtype == rtype) \
                                  .filter(Repository.url == url) \
                                  .filter(Repository.dist == dist) \
                                  .filter(Repository.section == section) \
                                  .one()
                except:
                    repo = Repository(rtype, url, dist, section)
                    self.session.add(repo)
                    
        self.session.commit()

    def on_update(self, reporthook):
        pass

        
#    def on_get_available_binary_packages(self):
#        pass
        

#    def on_get_available_binary_versions(self, package):
#        pass


#    def on_get_binary_dependencies(self, package):
#        pass
        

