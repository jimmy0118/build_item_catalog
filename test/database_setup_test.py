import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

class Console(Base):
    __tablename__ = 'console'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'id'           : self.id,
       }

class Game(Base):
    __tablename__ = 'game'

    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    date = Column(String(80))
    type = Column(String(80))
    developer = Column(String(250))
    console_id = Column(Integer,ForeignKey('console.id'))
    console = relationship(Console)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'type'         : self.type,
           'id'           : self.id,
           'date'         : self.date,
           'developer'    : self.developer,
       }


engine = create_engine('sqlite:///test.db')

Base.metadata.create_all(engine)
