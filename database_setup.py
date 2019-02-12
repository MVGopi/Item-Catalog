import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()

class Customers(Base):
	__tablename__ = 'Customers'
	"""This table for storing users data"""
	Customer_Id = Column(Integer, primary_key=True)
	Customer_Name = Column(String(150), nullable=False)
	Customer_Email = Column(String(150), nullable=False)
	Customer_Mobileno = Column(Integer)
	Customer_Picture = Column(String(250)) 
		

class Mobiles(Base):
	__tablename__ = 'Mobiles'
	"""This table for storing mobiles data"""
	Id = Column(Integer, primary_key=True)
	Name = Column(String(250), nullable=False)
	Price = Column(Integer)
	RAM = Column(String(150),nullable=False)
	ROM =Column(String(150),nullable=False)
	Front_Cam=Column(String(150),nullable=False)
	Back_Cam=Column(String(150),nullable=False)


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return 
		{
                	'Id':self.Id,
	    		'Name': self.Name,
            		'Price': self.Price,
             		'RAM': self.RAM,
            		'ROM': self.ROM,
            		'Front_Cam': self.Front_Cam,
            		'Back_Cam': self.Back_Cam,
        
        	}
db_engine = create_engine('sqlite:///Mobiles_Store.db')
Base.metadata.create_all(db_engine)
	
	
	
         


