Catalog App
===========

This project is for the 3rd project in the Udacity NanoDegree course. Please do not sue this for productive purposes as this is mainly meant to show capabilities learnt as part of the course. This web application displays a sports catalog and provides a list of items within a variety of categories. Authentication is integrated with third party user registration and authentication. Currently supported OAuth integration includes Facebook and Google+. 
Authenticated users have the ability to post, edit, and delete their own items. Default and sample data is assigned to guru.shetti@gmail.com.
This project is similar to the UD330 course which is part of the nanodegree. This project includes the HTML, the CSS, and the files that include the application itself utilizing Flask.

Installation:
============


1. First Please Install Vagrant and VirtualBox for your operating system

Link to Vagrant: https://www.vagrantup.com/downloads.html
Link to VirtualBox: https://www.virtualbox.org/wiki/Downloads

2. Clone the fullstack-nanodegree-vm and also clone the repo for this project in the vagrant shared home directory http://github.com/udacity/fullstack-nanodegree-vm
3. Launch the Vagrant VM (vagrant up)
4. The Flask application is in the vagrant/catalog directory (which will automatically be synced to /vagrant/catalog within the VM). 
5. To run the program please run vagrant@vagrant-ubuntu-trusty-32:/vagrant/catalog$ python application.py
6. Access and test the application by visiting http://localhost:8000 locally
7. An internet access is required for login to either facebook or google+
8. Please install Flask-WTF for CSRF protection. Without this library the program will error out.
    $ sudo pip install Flask-WTF for csrf
9. Image upload functionality is accessible to object owners
10. Important: To see "Latest items" in the home page please drop database and then repopulate with sample data from lotsofitems.py. This program populates couple of items with current date. Anything with todays date is termed as just arrived
11. Sample data items is associated with authors email ID. If you need object CRUD access please replace guru.shetti@gmail.com with your email ID that you will be logging in with
12. JSON and XML api enabled


Project Contains:
=================

This project is based on SQLite database. The same is created using the script in the root folder.

$python app_database_setup.py

For sample data either login using either facebook or google+ and create a catalog and items or run the follwoing script for sample data.

$python lotsofitems.py

After running the above steps please run the actual application:

$python application.py

Following are the contents of the project and its sub-folders

README.txt		> This document you are reading	
app_database_setup.py		> Please run this script to setup the database "$python app_database_setup.py"
app_database_setup.pyc		> byte code
application.py			> Please run this for the actual application		
client_secrets.json		> Normally this is not provided. As an exception to testing this app by Udacity this is provided for you. For setting up ypur own OAuth 2 secret token and key please update this file. For instructions please refer to https://www.udacity.com/course/viewer#!/c-ud330-nd
fb_client_secrets.json  > Normally this is not provided. As an exception to testing this app by Udacity this is provided for you. For setting up ypur own OAuth 2 secret token and key please update this file. For instructions please refer to https://www.udacity.com/course/viewer#!/c-ud330-nd
lotsofitems.py  > If you wish to populate sample data
sportscatalogwithusers.db > The database shipped with sample data. To start fresh feel free to delete this if you are not running the app_database_setup.py
static (folder) > contains static files for CSS, jpgs
templates (folder) > contains the HTML files

3rd party clients
=================

This application provides an API for the catalog.
JSON
 
Examples:

1. Read entire catalog

http://localhost:8000/catalog/JSON

{
  "catalog_headers": [
    {
      "id": 1,
      "name": "Soccer"
    },
    {
      "id": 2,
      "name": "Basketball"
    },
    {
      "id": 3,
      "name": "Tennis"
    },
    {
      "id": 4,
      "name": "Motor Racing"
    },
    {
      "id": 5,
      "name": "Hockey"
    },
    {
      "id": 6,
      "name": "Swimming"
    }
  ]
}

2. Read a specific catalog category (header)

http://localhost:8000/catalog/<int:catalog_header_id>/catalogitems/JSON


http://localhost:8000/catalog/1/catalogitems/JSON

{
  "CatalogItems": [
    {
      "description": "Really Fast",
      "id": 1,
      "name": "Soccer Cleats",
      "price": "$7.50",
      "section": "Women"
    },
    {
      "description": "Max Protection",
      "id": 2,
      "name": "Shin Guards",
      "price": "$2.99",
      "section": "Men"
    },
    {
      "description": "Dry Fit",
      "id": 3,
      "name": "Shirt",
      "price": "$5.50",
      "section": "Women"
    },
    {
      "description": "Lightweight Band",
      "id": 4,
      "name": "Band",
      "price": "$3.99",
      "section": "Boys"
    },
    {
      "description": "Comfortable",
      "id": 5,
      "name": "Socks",
      "price": "$1.99",
      "section": "Girls"
    }
  ]
}


3. Get details on an Item 

http://localhost:8000//catalog/<int:catalog_header_id>/catalogitems/<int:catalog_item_id>/JSON

http://localhost:8000/catalog/1/catalogitems/2/JSON

{
  "Catalog_Item": {
    "description": "Max Protection",
    "id": 2,
    "name": "Shin Guards",
    "price": "$2.99",
    "section": "Men"
  }
}

This application provides an API for the catalog.
XML

Exmaple:

http://localhost:8000/catalog/catalog/xml

<CatalogHeaders xmlns="http://udacity.com/schemas/catalog/0.1">
<Catalog>
<ID>1</ID>
<Name>Soccer</Name>
</Catalog>
<Catalog>
<ID>2</ID>
<Name>Basketball</Name>
</Catalog>
<Catalog>
<ID>3</ID>
<Name>Tennis</Name>
</Catalog>
<Catalog>
<ID>4</ID>
<Name>Motor Racing</Name>
</Catalog>
<Catalog>
<ID>5</ID>
<Name>Hockey</Name>
</Catalog>
<wappalyzerData id="wappalyzerData" style="display: none"/>
<script id="wappalyzerEnvDetection" src="chrome-extension://gppongmhjkpfnbhagpmjfkannfbllamg/js/inject.js"/>
<head/>
</CatalogHeaders>



TODO:
=====

1. The rating system is provided as a mockup and will be incorporated in future releases
2. CSS is minimal as this is due to a project submission. 

License:
========

Copyright and licensing information: Under MIT licenings

To Run: Copy the tournament.py and tournament.sql along with the tournament_test.py into the tournament vagrant directory.

first run tournament.sql then tournamanet_test.py

Latest version of github.com/gurugithub