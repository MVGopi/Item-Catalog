from flask import Flask,render_template,url_for,request,redirect,flash,make_response,jsonify
from mobiles_database_setup import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#creating flask application
app=Flask(__name__)

#database connection
db_engine = create_engine('sqlite:///mobiles_store.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(db_engine)
Database_Session = sessionmaker(bind=db_engine)
session=Database_Session()

#view for home page
@app.route('/')
def  index():
    company_names=session.query(Company).all()
    return render_template("home.html",mobile_companies=company_names)

#view for displaying mobiles
@app.route('/show_mobiles/<int:company_id>/')
def show_mobiles(company_id):
    company_name=session.query(Company).filter_by(id=company_id).one()
    mobiles=session.query(Mobile).filter_by(company_id=company_id).all()
    return render_template('show_mobiles.html',mobiles_list=mobiles,company=company_name)

if __name__=='__main__':
    app.run(host="localhost",port=8080,debug=True)
