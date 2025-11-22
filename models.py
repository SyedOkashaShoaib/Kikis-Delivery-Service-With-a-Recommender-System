from . import db, login
from sqlalchemy.sql import func
import sqlalchemy.orm as so
import enum
from sqlalchemy import Enum, PrimaryKeyConstraint, Time
from datetime import date
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
'''
class Registered_Users(UserMixin, db.Model):
    __tablename__="registered_users"
    register_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    userpassword = db.Column(db.String(255), nullable=False)
    userrole = db.Column(db.String(15), nullable=False)
    
    __table_args__ = (
        db.CheckConstraint("userrole IN ('ADMIN','CUSTOMER','VENDOR','DELIVERY')", name='role_check'),
    )

    def set_password(self,password):
        self.userpassword = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.userpassword, password)
    
    def get_id(self):
        return self.register_id 
    
    def __rep__(self):
        return f"<Registered User : {self.username} > " #remove this
'''

class Menu(UserMixin, db.Model):
    _tablename_="menu"
    vendor_id = db.Column(db.Integer,db.ForeignKey('vendor.id'), nullable=False)    
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    discount=db.Column(db.Integer, default=0)
    price = db.Column(db.Numeric(8,2),nullable=False)
    cuisine = db.Column(db.String(35),nullable=True) # Indian, Chinese, American etc
    category = db.Column(db.String(35),nullable=True) # Rice, Noodles, BBQ, Vegetables, Roti, Gravy, FastFood
    Type = db.Column(db.String(35),nullable=True) # Burger, Biryani, Ramen, etc
    prep_time = db.Column(db.Integer,nullable=False) # Minutes
    rating = db.Column(db.Integer,nullable=False) # 1-5
    
    
@login.user_loader  #registers this fun with flask-login #####################################################
def load_user(id):
    try:
        prefix, user_id = id.split('_')#since id in the parameter is a sring we first have to convert it 
        
        if prefix == 'cust':
            return db.session.get(Customer, int(user_id))
        elif prefix == 'vend':
            return db.session.get(Vendor, int(user_id))
        elif prefix == 'deliv':
            return db.session.get(Delivery_Person, int(user_id))
                
    except (ValueError, AttributeError):
        pass
    return None

class Locations(UserMixin, db.Model):
    __tablename__ = "location"
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Numeric(15,10), nullable=False) 
    longitude = db.Column(db.Numeric(15,10), nullable=False)
    full_address = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=True)
    osm_id = db.Column(db.String(75), nullable=False)
    osm_type = db.Column(db.String(50), nullable=False)
    data_source = db.Column(db.String(50), nullable=False)

class Customer(UserMixin, db.Model):
    __tablename__ = "customer"
    id = db.Column(db.Integer, primary_key=True)
    customer_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    name = db.Column(db.String(50), nullable=False)

    username = db.Column(db.String(30), unique=True)
    user_phone = db.Column(db.String(11), nullable=False)
    user_email = db.Column(db.String(30), nullable=False)
    user_reg_date=db.Column(db.Date, nullable=False, default=date.today)
    userpassword = db.Column(db.String(255), nullable=False)

    def set_password(self,password):
        self.userpassword = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.userpassword, password)
      
    def get_id(self):
        return f"cust_{self.id}"
    
    def __rep__(self):
        return f"<Customer : {self.username} > " #remove this

class Vendor(UserMixin, db.Model):
    __tablename__ = "vendor"
    id = db.Column(db.Integer, primary_key=True)
    vendor_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    name = db.Column(db.String(50), nullable=False)
    working_hours_start = db.Column(db.Time, nullable=False)
    working_hours_end = db.Column(db.Time, nullable= False)

    v_username = db.Column(db.String(30), unique=True)
    v_phone = db.Column(db.String(11), nullable=False)
    v_email = db.Column(db.String(30), nullable=False)
    v_reg_date = db.Column(db.Date, nullable=False, default=date.today)  #How to add a date field in the form?
    v_verified = db.Column(db.Boolean, nullable=False, default=False)
    userpassword = db.Column(db.String(255), nullable=False)

    def set_password(self,password):
        self.userpassword = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.userpassword, password)
      
    def get_id(self):
        return f"vend_{self.id}"

    def pending_order_count(self):
        1

class Delivery_Person(UserMixin, db.Model):
    __tablename__ = "delivery_person"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=True) # Person has an option to log in duty in the UI
    salary = db.Column(db.Integer, nullable=True) #Save later in config File
    #Salary is fixed per hour
    last_paid=db.Column(db.Date, default=date.today)
    worked_hours = db.Column(db.Integer, default=0) #worked_hours since last paid, to be reset and paid every week. Automated
    current_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    wallet = db.Column(db.Numeric(8,2), default=12000) # he will be given an allowance to deal with orders. which is a minimum 12k when the allowance reaches 20k it has to be returned and dealt by admin
    
    d_username= db.Column(db.String(30), unique=True)
    d_phone = db.Column(db.String(11), nullable=False)
    d_email = db.Column(db.String(30), nullable=False)
    d_reg_date = db.Column(db.Date, nullable=False, default=date.today)
    v_verified = db.Column(db.Boolean, nullable=False, default=False)
    userpassword = db.Column(db.String(255), nullable=False)

    def set_password(self,password):
        self.userpassword = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.userpassword, password)
    
    def get_id(self):
        return f"deliv_{self.id}"

    __table_args__ = (
        db.CheckConstraint("status IN ('ON_DUTY','OFF_DUTY','IN_JOB')", name='status_check'),
    )

class Order(UserMixin, db.Model): #This table will also be used as history i.e. order_status = DONE is history?
    __tablename__ = "order"
    #make composite key for id and item_id
    order_id = db.Column(db.Integer) # order id will be the same for a list of items that are from the same order i.e. same cart, Note they also have to be from the same vendor
    item_id = db.Column(db.Integer, db.ForeignKey('menu.item_id')) # Composite primary key of id and item_id
    delivery_person_id = db.Column(db.Integer, db.ForeignKey('delivery_person.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    status = db.Column(db.String(256), nullable=True)
    instructions = db.Column(db.String(256), nullable=True)
    quantity = db.Column(db.Integer , nullable=False, default=1)
    order_timestamp = db.Column(db.DateTime, default=datetime.now())

    __table_args__ = (
        db.CheckConstraint("status IN ('PENDING','ACCEPTED','REJECTED','PREPPING','DISPATCHED','DONE')", name='order_status_check'),
        PrimaryKeyConstraint('order_id', 'item_id')
    )

#NOTE: change the Primary key of all profile classes from username to id later on and cascade the changes. Much better I think.


