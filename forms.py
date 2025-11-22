from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, FloatField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange,Length, InputRequired, Optional
from wtforms import RadioField
from app.geocoder_test import Location_Handler # Static methods
import sqlalchemy as sa
from app import db
from app.models import Customer, Menu, Vendor, Delivery_Person

class LoginForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    user_type = RadioField('Login As', choices=[
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('delivery', 'Delivery')
    ],default='customer', validators=[DataRequired()])
    remember_user = BooleanField('Remember Me')
    submit = SubmitField('Login')

class Customer_Register_Form(FlaskForm):
    name = StringField("Enter your name: ", validators=[DataRequired()])
    username = StringField("Enter your username: ", validators=[DataRequired()])
    password = PasswordField("Enter Password: ",validators=[DataRequired()])
    confirm_pass = PasswordField("Confirm your password:", validators=[DataRequired(), EqualTo('password')])
    location = StringField("Enter your location: ", validators=[DataRequired()])
    phone_number= StringField("Enter your Phone Number: ")
    mail = StringField("Enter your Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        customer = db.session.scalar(sa.select(Customer).where(username.data == Customer.username))
        #.scalar means only one result will be returned 
        if customer is not None:
            raise ValidationError("Username already taken--")
    
    def validate_location(self, location):
        First_location = Location_Handler.Address_LookUp(location.data)
        if First_location is None:
            raise ValidationError("Location could not be found--") ############# Advanded Location lookup mecha here
        
    def validate_mail(self,mail):
        mail= db.session.scalar(sa.select(Customer).where(mail.data == Customer.user_email))
        if mail is not None:
            raise ValidationError("Email already in use by another user..")
            # Why use ValidateError ? Because this is how flask-wtf communicates with the form object, this validation error is stored in the form.<field anme>.error attribute and can be displayed in the form "gracefully(see register.html for example implementation)"


    #any method in this class starting with "validate_<field name> 
    #" will also be executed while checking the user input in that specific field..python is weird.
        
class Vendor_Register_Form(FlaskForm):
    username = StringField("Enter your username: ", validators=[DataRequired()])
    password = PasswordField("Enter Password: ",validators=[DataRequired()])
    confirm_pass = PasswordField("Confirm your password:", validators=[DataRequired(), EqualTo('password')])
    name = StringField("Enter Establishment name: ",validators=[DataRequired()])
    location = StringField("Enter Establishment location: ", validators=[DataRequired()])
    phone_number= StringField("Enter your Phone Number: ", validators=[DataRequired()])
    opening_time = StringField('Enter Opening hour: ', validators=[InputRequired(), Optional()])
    closing_time = StringField('Enter Closing hour: ', validators=[InputRequired(), Optional()])
    mail = StringField("Enter your Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")

    def validate_username(self, username):
        vendor = db.session.scalar(sa.select(Vendor).where(username.data == Vendor.v_username))
        #.scalar means only one result will be returned 
        if vendor is not None:
            raise ValidationError("Username already taken--")

    def validate_location(self, location):
        First_location = Location_Handler.Address_LookUp(location.data)
        if First_location is None:
            raise ValidationError("Location could not be found--")  

    def validate_mail(self,mail):
        mail= db.session.scalar(sa.select(Vendor).where(mail.data == Vendor.v_email))
        if mail is not None:
            raise ValidationError("Email already in use by another user..")
            # Why use ValidateError ? Because this is how flask-wtf communicates with the form object, this validation error is stored in the form.<field anme>.error attribute and can be displayed in the form "gracefully(see register.html for example implementation)"

class DeliveryGuy_Register_Form(FlaskForm):
    username = StringField("Enter your username: ", validators=[DataRequired()])
    password = PasswordField("Enter Password: ",validators=[DataRequired()])
    confirm_pass = PasswordField("Confirm your password:", validators=[DataRequired(), EqualTo('password')])
    name = StringField("Enter your name: ", validators=[DataRequired()])
    phone_number= StringField("Enter your Phone Number: ", validators=[DataRequired()])
    mail = StringField("Enter your Email: ", validators=[DataRequired(), Email()])

    submit = SubmitField("Register")

    def validate_username(self, username):
        delivery_guy = db.session.scalar(sa.select(Delivery_Person).where(username.data == Delivery_Person.d_username))
        #.scalar means only one result will be returned 
        if delivery_guy is not None:
            raise ValidationError("Username already taken--")
        
    def validate_mail(self,mail):
        mail= db.session.scalar(sa.select(Delivery_Person).where(mail.data == Delivery_Person.d_email))
        if mail is not None:
            raise ValidationError("Email already in use by another user..")

# class Menu(UserMixin, db.Model):
#     __tablename__="menu"
#     vendor_id = db.Column(db.Integer,db.ForeignKey('vendor.id'), nullable=False)    
#     item_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     discount=db.Column(db.Integer, default=0)
#     price = db.Column(db.Numeric(8,2),nullable=False)
        
class Add_Menu_Form(FlaskForm):
      name = StringField("Enter name of the dish: ", validators=[DataRequired(), Length(min=3,max=50)])
      discount= IntegerField("Enter Discount", validators=[NumberRange(min=0, max=100)])
      price=FloatField("Enter price of the item", validators=[DataRequired(),NumberRange(min=1,max=999999.99)]) #Need to make this better but later onnnnnn
      submit = SubmitField("Add")

      def validate_name(self,name):
          obj=db.session.scalar(sa.select(Menu).where(name.data==Menu.name))
          if obj is not None:
              raise ValidationError("Item already in menu")
          
class DeleteItem(FlaskForm):
    delete=SubmitField("Delete")
