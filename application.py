# Guru Shetti 7/1/2015 Last edit
# Uses Flask Framework for web page rendering and other functionality

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, send_from_directory
# uses sqlalchemy for operating on DB as objects
from sqlalchemy import create_engine, asc, func, desc, types, DateTime
from sqlalchemy.orm import sessionmaker
from app_database_setup import Base, CatalogHeader, CatalogItem, User
from flask import session as login_session
import random
import string
import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from urlparse import urljoin
from werkzeug.contrib.atom import AtomFeed
# uses Flask WTF CSRF functionality 
from flask_wtf.csrf import CsrfProtect
# Use secure_filename for image upload functionality
from werkzeug import secure_filename



app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

csrf = CsrfProtect()


# We load the client secrets with Gplus secret token etc
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

APPLICATION_NAME = "Sports Catalog"


# Connect to Database and create database session
engine = create_engine('sqlite:///sportscatalogwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# In case of CSRF errors we open the following template
@csrf.error_handler
def csrf_error(reason):
    return render_template('csrf_error.html', reason=reason), 400


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# We are exempting facebook domain from csrf so that we can do OAuth
@csrf.exempt
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.2/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.2/me?%s' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.2/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

@csrf.exempt
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# We are exempting gplus domain from csrf so that we can do OAuth
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    #login_session['credentials'] = credentials
    #login_session['access_token'] = credentials.access_token
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions

# Store the user email as user field in the table based object authorization
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# gets user info by ID
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# gets user info by email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
    
# Get Category Item Header Name

def getItemHeader(catalog_header_id):
    catalog_item_headers = session.query(CatalogHeader).filter(CatalogHeader.id == catalog_header_id).one()
    
    return catalog_item_headers

# gplus DISCONNECT - Revoke a current user's token and reset their login_session

@csrf.exempt
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    #access_token = credentials.access_token
    access_token = login_session.get('credentials')
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Catalog items for a particular category
@app.route('/catalog/<int:catalog_header_id>/catalogitems/JSON')
def catalogItemsJSON(catalog_header_id):
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    items = session.query(CatalogItem).filter_by(
        catalog_header_id=catalog_header_id).all()
    return jsonify(CatalogItems=[i.serialize for i in items])

# JSON APIs to view Catalog item detail for a particular category
@app.route('/catalog/<int:catalog_header_id>/catalogitems/<int:catalog_item_id>/JSON')
def catalogItemJSON(catalog_header_id, catalog_item_id):
    Catalog_Item = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    return jsonify(Catalog_Item=Catalog_Item.serialize)

# JSON APIs to view Catalog categories for a particular category
@app.route('/catalog/JSON')
def catalogHeadersJSON():
    catalog_headers = session.query(CatalogHeader).all()
    return jsonify(catalog_headers=[r.serialize for r in catalog_headers])

# makes the url to upload image file
def make_external(url):
    return urljoin(request.url_root, url)

# gets the catalog at atom RSS

@app.route('/catalog/catalog.atom')
def catalogHeadersATOM():
    catalog_headers = session.query(CatalogHeader).all()
    
    feed = AtomFeed('SportsCatalog',
                    feed_url=request.url, url=request.url_root)
    for catalog_header in catalog_headers:
        feed.add(catalog_header.id, content_type='html')
    return feed.get_response()


# gets the list of catalog categories in XML API
@app.route('/catalog/catalog/xml')
def catalogHeadersXML():
    catalog_headers = session.query(CatalogHeader).all()
    catalog_xml = render_template('catalog_header.xml', catalog_headers=catalog_headers)
    response= make_response(catalog_xml)
    response.headers["Content-Type"] = "application/xml"   
    return response

# gets the list of catalog items for a category categories in XML API
@app.route('/catalog/<int:catalog_header_id>/catalogitems/xml')
def catalogItemsXML(catalog_header_id):
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    items = session.query(CatalogItem).filter_by(
        catalog_header_id=catalog_header_id).all()
    
    catalogItems_xml = render_template('catalog_items.xml',            catalog_headers=catalog_headers, catalog_items=items)
    response= make_response(catalogItems_xml)
    response.headers["Content-Type"] = "application/xml"   
    return response


# Show all catalogs in html page
@app.route('/')
@app.route('/catalog/')
def showCatalogHeaders():
    catalog_headers = session.query(CatalogHeader).order_by(asc(CatalogHeader.name))
    items_with_category = session.query(CatalogHeader, CatalogItem).filter(CatalogHeader.id == CatalogItem.catalog_header_id).filter(CatalogItem.first_stock_date == func.current_date()).all()
    
    if 'username' not in login_session:
        return render_template('publiccatalog.html', catalog_headers=catalog_headers, items_with_category=items_with_category)
    else:
        return render_template('catalog.html', catalog_headers=catalog_headers, items_with_category=items_with_category)
    
# Create a new catalog
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newCatalogHeader():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCatalogHeader = CatalogHeader(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newCatalogHeader)
        flash('New CatalogHeader %s Successfully Created' % newCatalogHeader.name)
        session.commit()
        return redirect(url_for('showCatalogHeaders'))
    else:
        return render_template('newCatalogHeader.html')

# Edit a catalog
@app.route('/catalog/<int:catalog_header_id>/edit/', methods=['GET', 'POST'])
def editCatalogHeader(catalog_header_id):
    editedCatalogHeader = session.query(
        CatalogHeader).filter_by(id=catalog_header_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedCatalogHeader.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this catalog. Please create your own catalog in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedCatalogHeader.name = request.form['name']
            flash('CatalogHeader Successfully Edited %s' % editedCatalogHeader.name)
            return redirect(url_for('showCatalogHeaders'))
    else:
        return render_template('editCatalogHeader.html', catalog_header=editedCatalogHeader)


# Delete a catalog
@app.route('/catalog/<int:catalog_header_id>/delete/', methods=['GET', 'POST'])
def deleteCatalogHeader(catalog_header_id):
    catalogHeaderToDelete = session.query(
        CatalogHeader).filter_by(id=catalog_header_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if catalogHeaderToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this catalog. Please create your own catalog in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(catalogHeaderToDelete)
        flash('%s Successfully Deleted' % catalogHeaderToDelete.name)
        session.commit()
        return redirect(url_for('showCatalogHeaders', catalog_header_id=catalog_header_id))
    else:
        return render_template('deleteCatalogHeader.html', catalog_header=catalogHeaderToDelete)

# Show a items for a catalog category
@app.route('/catalog/<int:catalog_header_id>/')
@app.route('/catalog/<int:catalog_header_id>/catalogitems/')
def showCatalogItems(catalog_header_id):
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    catalog_headers = session.query(CatalogHeader).order_by(asc(CatalogHeader.name))
    creator = getUserInfo(catalog_header.user_id)
    items = session.query(CatalogItem).filter_by(
        catalog_header_id=catalog_header_id).all()
    item_count = session.query(CatalogItem).filter_by(
        catalog_header_id=catalog_header_id).count()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publiccatalogitems.html', items=items, catalog_header=catalog_header, creator=creator, catalog_headers=catalog_headers, item_count=item_count)
    else:
        return render_template('catalogitems.html', items=items, catalog_header=catalog_header, creator=creator, catalog_headers=catalog_headers, item_count=item_count)

# Show a item details for a catalog category
@app.route('/catalog/<int:catalog_header_id>/catalogitems/<int:catalog_item_id>/')
def showCatalogItemDetails(catalog_header_id, catalog_item_id):
    catalog_headers = session.query(CatalogHeader).order_by(asc(CatalogHeader.name))

    itemDetails = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
#    if 'username' not in login_session or creator.id != login_session['user_id']:
    return render_template('catalogItemDetails.html', catalog_headers=catalog_headers, itemDetails=itemDetails)
#    else:
#        return render_template('catalogitems.html', items=items, catalog_header=catalog_header, creator=creator)


# Create a new catalogitems item
@app.route('/catalog/<int:catalog_header_id>/catalogitems/new/', methods=['GET', 'POST'])
def newCatalogItem(catalog_header_id):
    print "In new items"
    
    if 'username' not in login_session:
        return redirect('/login')
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    print catalog_header.user_id, login_session['user_id']
    if login_session['user_id'] != catalog_header.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add catalogitems items to this catalog. Please create your own catalog in order to add items.');}</script><body onload='myFunction()''>"
     
    if request.method == 'POST':
            print "In post"
            newItem = CatalogItem(name=request.form['name'], description=request.form['description'], price=request.form[
                               'price'], section=request.form['section'], catalog_header_id=catalog_header_id, user_id=catalog_header.user_id, first_stock_date=func.current_date())
            session.add(newItem)
            session.commit()
            flash('New Catalog Item %s Item Successfully Created' % (newItem.name))
            return redirect(url_for('showCatalogItems', catalog_header_id=catalog_header_id))
    else:
        print "In login not same"
        return render_template('newcatalogitem.html', catalog_header_id=catalog_header_id)
        

# Edit a catalogitems item

@app.route('/catalog/<int:catalog_header_id>/catalogitems/<int:catalog_item_id>/edit', methods=['GET', 'POST'])
def editCatalogItem(catalog_header_id, catalog_item_id):
    print "in edit"
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    if login_session['user_id'] != catalog_header.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit   items to this catalog. Please create your own catalog in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        print "in POST"
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['section']:
            editedItem.course = request.form['section']
        session.add(editedItem)
        session.commit()
        flash('Catalog Item Successfully Edited')
        return redirect(url_for('showCatalogItems', catalog_header_id=catalog_header.id))
    else:
        return render_template('editcatalogitem.html', catalog_header_id=catalog_header_id, catalog_item_id=catalog_item_id, item=editedItem)


# Delete a catalog_item item
@app.route('/catalog/<int:catalog_header_id>/catalogitems/<int:catalog_item_id>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(catalog_header_id, catalog_item_id):
    if 'username' not in login_session:
        return redirect('/login')
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    itemToDelete = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    if login_session['user_id'] != catalog_header.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete  items to this catalog. Please create your own catalog in order to delete items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('showCatalogItems', catalog_header_id=catalog_header_id))
    else:
        return render_template('deleteCatalogItem.html', item=itemToDelete)

# Upload image for item
@csrf.exempt
@app.route('/catalog/<int:catalog_header_id>/catalogitems/<int:catalog_item_id>/upload', methods=['GET', 'POST'])
def uploadCatalogItemImage(catalog_header_id, catalog_item_id):

    if 'username' not in login_session:
        return redirect('/login')
    catalog_header = session.query(CatalogHeader).filter_by(id=catalog_header_id).one()
    itemToUpload = session.query(CatalogItem).filter_by(id=catalog_item_id).one()
    if login_session['user_id'] != catalog_header.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete  items to this catalog. Please create your own catalog in order to delete items.');}</script><body onload='myFunction()''>"
    
    if request.method == 'POST':
        print "in upload POST"
        # Get the name of the uploaded file
        file = request.files['file']
        # Check if the file is one of the allowed types/extensions
        if file and allowed_file(file.filename):
            # Make the filename safe, remove unsupported chars
            filename = secure_filename(file.filename)
            # Move the file form the temporal folder to
            # the upload folder we setup
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        
       
        itemToUpload.image = filename
        session.add(itemToUpload)
        session.commit()
        flash('Catalog Item Image Successfully Uploaded')
        return redirect(url_for('showCatalogItems', catalog_header_id=catalog_header_id))
    else:
        return render_template('uploadCatalogItemImage.html', item=itemToUpload)

    

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalogHeaders'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalogHeaders'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    csrf.init_app(app)
    app.run(host='0.0.0.0', port=8000)
