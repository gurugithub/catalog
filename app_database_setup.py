# The program sets up the database that will be used for the application
# July 1st 2015
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

# User table where user names are stored that have authorization to item objects
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

# this is the header table

class CatalogHeader(Base):
    __tablename__ = 'catalog_header'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

# this is the items table

class CatalogItem(Base):
    __tablename__ = 'catalog_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    section = Column(String(10))
    first_stock_date = Column(Date, default=datetime.date)
    image = Column(String(255))
    catalog_header_id = Column(Integer, ForeignKey('catalog_header.id'))
    catalog_header = relationship(CatalogHeader)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'section': self.section,
        }


engine = create_engine('sqlite:///sportscatalogwithusers.db')


Base.metadata.create_all(engine)
