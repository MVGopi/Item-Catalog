import sys
import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
Base = declarative_base()

class Company(Base):
	__tablename__ = 'company'
	"""This table for storing mobile companies list"""
	id=Column(Integer,primary_key=True)
	name=Column(String(250),nullable=False)

	@property
	def serialize(self):
                """Return object data easily  in serailize format"""
                return{
                        'id':self.id,
                        'name':self.name
                        }
		

class Mobile(Base):
	__tablename__ = 'mobile'
	"""This table for storing mobiles data"""
	id = Column(Integer, primary_key=True)
	name = Column(String(250),nullable=False)
	price = Column(Integer,nullable=False)
	ram = Column(String(150),nullable=False)
	rom =Column(String(150),nullable=False)
	front_cam=Column(String(150),nullable=False)
	back_cam=Column(String(150),nullable=False)
	image=Column(String(250),nullable=False)
	company_id=Column(Integer,ForeignKey('company.id'))
	comp=relationship(Company,backref=backref("mobile",cascade="all,delete"))


	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return 
		{
                	'Id':self.id,
	    		'Name': self.name,
            		'Price': self.price,
             		'RAM': self.ram,
            		'ROM': self.ROM,
            		'Front_Cam': self.front_cam,
            		'Back_Cam': self.back_cam,
                        'image':self.image
        
        	}
db_engine = create_engine('sqlite:///mobiles_store.db')
Base.metadata.create_all(db_engine)
	
	
	
         

