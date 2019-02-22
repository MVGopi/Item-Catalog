from flask import Flask,render_template,url_for,request,redirect,flash,make_response,jsonify
from mobiles_database_setup import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import session as login_session
import random, string, json

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import requests

#creating flask application
app=Flask(__name__)

CLIENT_ID=json.loads(open('client_secrets.json','r').read())['web']['client_id']
APPLICATION_NAME="Mobile Store Item-Catalog"
#database connection
db_engine = create_engine('sqlite:///mobiles_store.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.create_all(db_engine)
Database_Session = sessionmaker(bind=db_engine)
session=Database_Session()

#login
@app.route('/login')
def showLogin():
    state=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state']=state
    company_name=session.query(Company).all()
    mobiles=session.query(Mobile).all()
    return render_template('login.html',STATE=state,company_name=company_name,mobiles=mobiles)

#gconnect
@app.route('/gconnect',methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:

        response=make_response(json.dumps('Invalid State parameter'),401)
        response.headers['Content-Type']='application/json'
        return response
    code=request.data

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id=getUserID(login_session['email'])
    if not user_id:
        user_id=createUser(login_session)
    login_session['user_id']=user_id

    output = ''
    output += '<center><h2><font color="green">Welcome '
    output += login_session['username']
    output += '!</font></h2></center>'
    output += '<center><img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: 200px;-webkit-border-radius: 200px;-moz-border-radius: 200px;"></center>'
    flash("you are now logged in as %s" % login_session['username'])
    print("Done")
    return output
#create User
def createUser(login_session):
    newUser=User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
        )
    session.add(newUser)
    session.commit()

    user=session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    user=session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    try:
        user=session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as e:
        return None

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
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_comp = company(name=request.form['name'],icon=request.form['icon'])
        session.add(new_comp)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('new_company.html')
#edit company name
@app.route('/edit_company/<int:company_id>',methods=['POST','GET'])
def edit_company(company_id):
    if 'username' not in login_session:
        return redirect('/login')
    edit_comp = session.query(Company).filter_by(id=company_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edit_comp.name = request.form['name']
            return redirect(url_for('index'))
    else:
        return render_template('edit_company.html', company=edit_comp)
    if edit_comp.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('You are not authorized to\
        edit this mobile_company. please sign  in order\
        to edit.');}</script><body onload='myFunction()'>"


#remove company
@app.route('/remove_company/<int:company_id>',methods=['POST','GET'])
def remove_company(company_id):
    if 'username' not in login_session:
        return redirect('/login')
    remove_comp=session.query(Company).filter_by(id=company_id).one()
    if request.method=='POST':
        session.delete(remove_comp)
        session.commit()
        return redirect(url_for('index'))
    else:
        return render_template('remove_company.html',company_id=company_id)
    if remove_comp.user_id != login_session['user_id']:
        return "<script>function myFunction(){alert('You are not authorized to\
        remove this mobile_company. please sign  in order\
        to remove.');}</script><body onload='myFunction()'>"

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
        return redirect(url_for('show_mobiles',company_id=company_id))
    else:
        return render_template('insert_mobile.html',company_id=company_id)

#edit mobile
@app.route('/edit_mobile/<int:company_id>/<int:mobile_id>',methods=['POST','GET'])
def edit_mobile(mobile_id,company_id):
    update_mobile=session.query(Mobile).filter_by(id=mobile_id).one()
    if request.method=='POST':
        update_mobile.name=request.form['name']
        update_mobile.price=request.form['price']
        update_mobile.ram=request.form['ram']
        update_mobile.rom=request.form['rom']
        update_mobile.front_cam=request.form['front_cam']
        update_mobile.back_cam=request.form['back_cam']
        update_mobile.image=request.form['image']
        session.commit()
        return redirect(url_for('show_mobiles',company_id=company_id))
    else:
        return render_template('edit_mobile.html',company_id=company_id,mobile_id=mobile_id,mobile_details=update_mobile)

#delete mobile
@app.route('/remove_mobile/<int:company_id>/<int:mobile_id>',methods=['POST','GET'])
def remove_mobile(company_id,mobile_id):
    delete_mobile=session.query(Mobile).filter_by(id=mobile_id).one()
    if request.method=="POST":
        session.delete(delete_mobile)
        session.commit()
        return redirect(url_for('show_mobiles',company_id=company_id))
    else:
        return render_template('remove_mobile.html',company_id=company_id,mobile_id=mobile_id,mobile=delete_mobile)

def logout():
    access_token=login_session['access_token']
    print("In gdisconnect access token is %s",access_token)
    print("User Name is:")
    print(login_session['username'])

    if access_token is None:
        print("Access Token is None")
        response=make_response(json.dumps('Current user not connected.'),401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = login_session['access_token']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = \
        h.request(uri=url, method='POST', body=None,
                  headers={'content-type': 'application/x-www-form-urlencoded'})[0]

    print(result['status'])
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("Successfully logged out")
        return redirect(url_for('showCountry'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__=='__main__':
    app.secret_key='super_secret_key'
    app.debug=True
    app.run(host="localhost",port=8888)
