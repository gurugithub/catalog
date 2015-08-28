# File to populate database with samples. Default is guru.shetti@gmail.com
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import datetime
from app_database_setup import CatalogHeader, Base, CatalogItem, User

engine = create_engine('sqlite:///sportscatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Guru Shetti", email="guru.shetti@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
catalog_header1 = CatalogHeader(user_id=1, name="Soccer")

session.add(catalog_header1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Soccer Cleats", description="Really Fast",
                     price="$7.50", section="Women", first_stock_date= func.current_date(), image="shoes.jpg",  catalog_header=catalog_header1)

session.add(catalogItem2)
session.commit()


catalogItem1 = CatalogItem(user_id=1, name="Shin Guards", description="Max Protection",
                     price="$2.99", section="Men", first_stock_date= datetime.date(2015,06,15), image="shoes.jpg", catalog_header=catalog_header1)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Shirt", description="Dry Fit",
                     price="$5.50", section="Women", first_stock_date= datetime.date(2015,06,15), image="swimtrunk.jpg", catalog_header=catalog_header1)

session.add(catalogItem2)
session.commit()

catalogItem3 = CatalogItem(user_id=1, name="Band", description="Lightweight Band",
                     price="$3.99", section="Boys", first_stock_date= datetime.date(2015,06,15), image="shoes.jpg", catalog_header=catalog_header1)

session.add(catalogItem3)
session.commit()


catalogItem5 = CatalogItem(user_id=1, name="Socks", description="Comfortable",
                     price="$1.99", section="Girls", first_stock_date= datetime.date(2015,06,15), image="shoes.jpg", catalog_header=catalog_header1)

session.add(catalogItem5)
session.commit()


# Menu for Super Stir Fry
catalog_header2 = CatalogHeader(user_id=1, name="Basketball")

session.add(catalog_header2)
session.commit()


catalogItem1 = CatalogItem(user_id=1, name="Shoes", description="Max Traction",
                     price="$237.99", section="Women", first_stock_date= datetime.date(2015,06,15), image="shoes.jpg", catalog_header=catalog_header2)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Shirt",
                     description="Lightweight Shirt imported", price="$25", section="Women", first_stock_date= datetime.date(2015,06,15), catalog_header=catalog_header2)

session.add(catalogItem2)
session.commit()

# Menu for Panda Garden
catalog_header1 = CatalogHeader(user_id=1, name="Tennis")

session.add(catalog_header1)
session.commit()


catalogItem1 = CatalogItem(user_id=1, name="Shoes", description="Tennis Shoes",
                     price="$8.99", section="Women", first_stock_date= func.current_date(), catalog_header=catalog_header1)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Racket", description="Carbon Fiber",
                     price="$96.99", section="Men", first_stock_date= datetime.date(2015,06,15), catalog_header=catalog_header1)

session.add(catalogItem2)
session.commit()


# Menu for Thyme for that
catalog_header1 = CatalogHeader(user_id=1, name="Motor Racing")

session.add(catalog_header1)
session.commit()


catalogItem1 = CatalogItem(user_id=1, name="Helmet", description="Max Projection - Ferrari Inspired",
                     price="$122.99", section="Boys", first_stock_date= datetime.date(2015,06,15), catalog_header=catalog_header1)

session.add(catalogItem1)
session.commit()

catalogItem2 = CatalogItem(user_id=1, name="Overalls", description="Fire Resistant",
                     price="$5.99", section="Women", first_stock_date= datetime.date(2015,06,15), catalog_header=catalog_header1)

session.add(catalogItem2)
session.commit()



# Menu for Tony's Bistro
catalog_header1 = CatalogHeader(user_id=1, name="Hockey")

session.add(catalog_header1)
session.commit()


catalogItem1 = CatalogItem(user_id=1, name="Racket", description="Lightweight",
                     price="$713.95", section="Men", first_stock_date= datetime.date(2015,06,15), catalog_header=catalog_header1)

session.add(catalogItem1)
session.commit()




print "added sports catalog items!"
