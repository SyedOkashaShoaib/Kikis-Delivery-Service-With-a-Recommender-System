from . import db, login
from sqlalchemy.sql import func
import enum
from sqlalchemy import Enum
from datetime import date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class Customer_Profile(db.Model, UserMixin):
    __tablename__ = 'customer_profile'
    username = db.Column(db.String(30), primary_key=True)
    # user_password = db.Column(db.String(255), nullable=False) #remove this
    user_phone = db.Column(db.String(11), nullable=True)
    user_email = db.Column(db.String(30), nullable=True)
    user_reg_date=db.Column(db.Date, nullable=False, default=date.today)


    def __rep__(self):
        return f"<Customer : {self.username} > " #remove this
    
    # def set_password(self, password):
    #     self.user_password = generate_password_hash(password)  #remove this
    # def check_password(self, password):
    #     return check_password_hash(self.user_password, password) #remove this..

    def get_id(self):
        return self.username   #i have overridden the usermixin function,for now ...


class Vendor_Profile(UserMixin, db.Model):
    __tablename__='vendor_profile'
    v_username = db.Column(db.String(30), primary_key=True)
    v_phone = db.Column(db.String(11), nullable=False)
    v_email = db.Column(db.String(30), nullable=False)
    v_reg_date = db.Column(db.Date, nullable=False)  #How to add a date field in the form?
    v_verified = db.Column(db.Boolean, nullable=False, default=True)
    #  vendorusername VARCHAR(50) PRIMARY KEY,
    # -- vendor_password VARCHAR(8) NOT NULL,
    # vendor_phone VARCHAR(11),
    # vendor_email VARCHAR(30),
    # vendor_reg_date DATE NOT NULL,
    # vendor_verified BOOLEAN DEFAULT TRUE NOT NULL,
    # CONSTRAINT verified_check CHECK (vendor_verified IN (TRUE, FALSE))



class Delivery_Profile(UserMixin, db.Model):
    __tablename__='it_profile'
    d_username= db.Column(db.String(30), primary_key=True)
    d_phone = db.Column(db.String(11), nullable=False)
    d_email = db.Column(db.String(30), nullable=False)
    d_reg_date = db.Column(db.Date, nullable=False)
    d_last_paid=db.Column(db.Date, nullable=True)
    d_license_stat = db.Column( db.Boolean, nullable=False, default=True) #change this to db.checkconstraint 
#     CREATE TABLE it_profile (
#     delivery_username VARCHAR(30) PRIMARY KEY,
#     delivery_password VARCHAR(8) NOT NULL,
#     delivery_phone VARCHAR(11),
#     delivery_email VARCHAR(30),
#     delivery_reg_date DATE NOT NULL,
#     last_paid_date DATE,
#     license_status VARCHAR(10) NOT NULL CHECK (license_status IN ('EXPIRED', 'VALID')),
#     expiry_date DATE NOT NULL
# );



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


class Vendor(UserMixin, db.Model):
    __tablename__ = "vendor"
    id = db.Column(db.Integer, primary_key=True)
    vendor_username = db.Column(db.String(30), db.ForeignKey('vendor_profile.v_username'))

class Menu(UserMixin, db.Model):
    __tablename__="menu"
    vendor_id = db.Column(db.Integer,db.ForeignKey('vendor.id'), nullable=False)    
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    discount=db.Column(db.Integer, default=0)
    price = db.Column(db.Numeric(8,2),nullable=False)
    category = db.Column(db.String(20),nullable=False)
    
@login.user_loader  #registers this fun with flask-login
def load_user(id):
    return db.session.get(Registered_Users,int(id))  #since id in the parameter is a sring we first have to convert it 

#NOTE: change the Primary key of all profile classes from username to id later on and cascade the changes. Much better I think.


