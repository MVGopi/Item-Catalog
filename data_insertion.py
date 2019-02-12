from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from database_setup import *

db_engine = create_engine('sqlite:///Mobiles_Store.db')

#For accessing declaratives through Database_Session instance need to  bind the db_engine to metadata of base class
Base.metadata.bind=db_engine

Database_Session=sessionmaker(bind=db_engine)
