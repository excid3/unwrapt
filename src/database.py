from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

class Projects(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)

class Repositories(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True)

class Packages(Base):
    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)

class Relations(Base):
    __tablename__ = "relations"

    id = Column(Integer, primary_key=True)

def initialize():
    engine = create_engine("sqlite:///database.db", echo=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    session = initialize()

    test_user = User()
    session.add(test_user)

    session.commit()
    session.close()

