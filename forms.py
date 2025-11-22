from wtforms import StringField, SubmitField, PasswordField, BooleanField, IntegerField, FloatField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange,Length
import sqlalchemy as sa
from app import db
from app.models import Customer_Profile, Menu



class LoginForm(FlaskForm):
    name = StringField("Enter Name:",validators=[DataRequired()])
    password = PasswordField("Enter Password:", validators=[DataRequired()])
    remember_user = BooleanField("Remember me")
    submit = SubmitField("Log in")

    
class Customer_Register_Form(FlaskForm):
    name = StringField("Enter your name: ", validators=[DataRequired()])
    password = PasswordField("Enter Password: ",validators=[DataRequired()])
    confirm_pass = PasswordField("Confirm your password:", validators=[DataRequired(), EqualTo('password')])
    customer_phone_number= StringField("Enter your Phone Number:(Optional) ")
    customer_mail = StringField("Enter your Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")

    def validate_name(self, name):
        customer = db.session.scalar(sa.select(Customer_Profile).where(name.data == Customer_Profile.username))
        #.scalar means only one result will be returned 
        if customer is not None:
            raise ValidationError("Username already taken--dick")
        
    def validate_customer_mail(self,customer_mail):
        mail= db.session.scalar(sa.select(Customer_Profile).where(customer_mail.data == Customer_Profile.user_email))
        if mail is not None:
            raise ValidationError("Email already in use by another user dick..")
            # Why use ValidateError ? Because this is how flask-wtf communicates with the form object, this validation error is stored in the form.<field anme>.error attribute and can be displayed in the form "gracefully(see register.html for example implementation)"


    #any method in this class starting with "validate_<field name> 
    #" will also be executed while checking the user input in that specific field..python is weird.
        
class Vendor_Register_Form(FlaskForm):
    name = StringField("Enter your name: ", validators=[DataRequired()])
    password = PasswordField("Enter Password: ",validators=[DataRequired()])
    confirm_pass = PasswordField("Confirm your password:", validators=[DataRequired(), EqualTo('password')])
    customer_phone_number= StringField("Enter your Phone Number:(Optional) ")
    customer_mail = StringField("Enter your Email: ", validators=[DataRequired(), Email()])
    submit = SubmitField("Register")

    def validate_name(self, name):
        customer = db.session.scalar(sa.select(Customer_Profile).where(name.data == Customer_Profile.username))
        #.scalar means only one result will be returned 
        if customer is not None:
            raise ValidationError("Username already taken--dick")
        
    def validate_customer_mail(self,customer_mail):
        mail= db.session.scalar(sa.select(Customer_Profile).where(customer_mail.data == Customer_Profile.user_email))
        if mail is not None:
            raise ValidationError("Email already in use by another user dick..")
            # Why use ValidateError ? Because this is how flask-wtf communicates with the form object, this validation error is stored in the form.<field anme>.error attribute and can be displayed in the form "gracefully(see register.html for example implementation)"

# class Menu(UserMixin, db.Model):
#     __tablename__="menu"
#     vendor_id = db.Column(db.Integer,db.ForeignKey('vendor.id'), nullable=False)    
#     item_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     discount=db.Column(db.Integer, default=0)
#     price = db.Column(db.Numeric(8,2),nullable=False)
        
class Add_Menu_Form(FlaskForm):
      name = StringField("Enter name of the dish: ", validators=[DataRequired(), Length(min=3,max=50)])
      discount= IntegerField("Enter Discount", validators=[NumberRange(min=0, max=100), DataRequired()])
      price=FloatField("Enter price of the item", validators=[DataRequired(),NumberRange(min=1,max=999999.99)]) #Need to make this better but later onnnnnn
      submit = SubmitField("Add")
      update=SubmitField("Update")

    #   def validate_name(self,name):
    #       obj=db.session.scalar(sa.select(Menu).where(name.data==Menu.name))
    #       if obj is not None:
    #           raise ValidationError("Item already in menu chotiye")
          
class DeleteItem(FlaskForm):
    delete=SubmitField("Delete")