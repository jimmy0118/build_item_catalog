import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Console(Base):
    __tablename__ = 'console'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

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


engine = create_engine('sqlite:///consolegames.db')

Base.metadata.create_all(engine)
