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

#home page
@app.route('/')
def  index():
    company_names=session.query(Company).all()
    return render_template("home.html",mobile_companies=company_names)

#displaying mobiles
@app.route('/show_mobiles/<int:company_id>/')
def show_mobiles(company_id):
    company_name=session.query(Company).filter_by(id=company_id).one()
    mobiles=session.query(Mobile).filter_by(company_id=company_id).all()
    return render_template('show_mobiles.html',mobiles_list=mobiles,company=company_name)

#adding new company name
@app.route('/new_company',methods=['POST','GET'])
def new_company():
	if request.method=='POST':
		new_comp=Company(name=request.form['name'])
		session.add(new_comp)
		session.commit()
		return redirect(url_for('index'))
	else:
		return render_template('new_company.html')
#edit company name
@app.route('/edit_company/<int:company_id>',methods=['POST','GET'])
def edit_company(company_id):
	edit_comp=session.query(Company).filter_by(id=company_id).one()
	if request.method=='POST':
		if request.form['name']:
			edit_comp.name=request.form['name']
			session.commit()
			return redirect(url_for('index'))
	else:
		return render_template('edit_company.html',company=edit_comp)

#remove company
@app.route('/remove_company/<int:company_id>',methods=['POST','GET'])
def remove_company(company_id):
	remove_comp=session.query(Company).filter_by(id=company_id).one()
	if request.method=='POST':
		if request.form['name']:
			session.delete(remove_comp)
			session.commit()
			return redirect(url_for('index'))
	else:
		return render_template('remove_company.html',company=remove_comp)

#add mobile
@app.route('/insert_mobile/<int:company_id>',methods=['POST','GET'])
def insert_mobile(company_id):
	if request.method=='POST':
		new_mobile=Mobile(name=request.form['name'],price=request.form['price'],
				  ram=request.form['ram'],rom=request.form['rom'],
	  			  front_cam=request.form['front_cam'],back_cam=request.form['back_cam'],
				  image=request.form['image'],company_id=company_id)
		session.add(new_mobile)
		session.commit()
		return redirect(url_for('show_mobiles'))
	else:
		return render_template('insert_mobile.html')
	


if __name__=='__main__':
    app.run(host="localhost",port=8888,debug=True)
