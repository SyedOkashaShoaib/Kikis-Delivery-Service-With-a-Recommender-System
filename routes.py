from flask import render_template, flash, redirect, url_for, request, session
from app import app, db
from app.models import Menu, Vendor, Delivery_Person, Customer, Locations
from app.forms import LoginForm, Customer_Register_Form, Add_Menu_Form, Vendor_Register_Form, DeliveryGuy_Register_Form
from flask_login import current_user, login_user, logout_user, login_required
from app.geocoder_test import Location_Handler # Static methods
from datetime import time
import sqlalchemy as sa
from urllib.parse import urlsplit

@app.route('/home')
@login_required   # redirects you to the function declared in login_view in innit file
def home():
    if session['user_type'] == 'customer':
        return render_template("customer_dashboard.html")
    elif session['user_type'] == 'vendor':
        return render_template("vendor_dashboard.html")
    elif session['user_type'] == 'delivery':
        return render_template('deliveryguy_dashboard.html')

@app.route('/', methods = ['GET', 'POST'])
@app.route('/login', methods = ['GET', 'POST'])
def login():
    loginform = LoginForm()
    if loginform.validate_on_submit():   # Checks if the request is a POST requ. also checks if the constraints defined in form class are not violated
       user = None
       user_type = loginform.user_type.data
       session['user_type'] = user_type

       if user_type == 'customer':
           user = db.session.scalar(sa.select(Customer).where(Customer.username == loginform.name.data))
       elif user_type == 'vendor':
           user = db.session.scalar(sa.select(Vendor).where(Vendor.v_username == loginform.name.data))
       elif user_type == 'delivery':
           user = db.session.scalar(sa.select(Delivery_Person).where(Delivery_Person.d_username == loginform.name.data))
     
       if user is None or not user.check_password(loginform.password.data): #the above query will return None if no such user exists
            flash('Invalid username or password')
            return redirect(url_for('login'))
       
       login_user(user, remember=loginform.remember_user.data)
       next_page = request.args.get('next')  #after redirecting to login the url is appended as : /login?next=/home 
       
       if not next_page or urlsplit(next_page).netloc == '': #case 1 : next_page is empty ->ridirect to home case 2 : there is a direct link (bots can access the address bar and type in malicous links) -> ridirect to home ppage for safety
            return redirect(url_for('home'))        
            
       return redirect(url_for(next_page)) #else redirect to the next page
    return render_template('index.html', form=loginform, title='Login')
#user navigates to the login page, an object of the LoginForm class is created, the validate function returns false cause user has not 
#filled the login form yet, the user is then taken to index.html where the user fills the form. in my index.html page the action variable 
#determines at which url the data is sent back to, if not specified it is sent back to the same url which in this case is /login, and this time 
#validate functino returns true and the user is redirected to the home page (this explanation was written on day 1 and im pretty sure wont hold up )


@app.route('/registercustomer', methods=['GET','POST']) 
def register_customer():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    registerform=Customer_Register_Form()
    if registerform.validate_on_submit():
        #i have already checked the database for duplicates in the validate_name method in the forms module so ill just directly add the customer to the database

        customer_location = Location_Handler.Address_LookUp(registerform.location.data)
        location_dict = Location_Handler.Reverse_Address_LookUp(customer_location)

        location = Locations(latitude=location_dict['latitude'],
                              longitude=location_dict['longitude'],
                              full_address=location_dict['full_address'],
                              name=location_dict['name'],
                              street=location_dict['street'],
                              city=location_dict['city'],
                              osm_id=location_dict['osm_id'],
                              osm_type=location_dict['osm_type'],
                              data_source=location_dict['data_source'])
        db.session.add(location)
        db.session.commit()

        customer=Customer(username=registerform.username.data, user_phone=registerform.phone_number.data,
                                    user_email=registerform.mail.data, name=registerform.name.data)
        customer.set_password(registerform.password.data)
        customer.customer_location_id = location.id
        db.session.add(customer)
        db.session.commit()
        
        flash("Registeration successful")
        return redirect(url_for('login'))  #customer needs to login so that he can be added to current_user
    #else:
    #    print("FORM VALIDATION FAILED!")
    #    print("Form errors:", registerform.errors)
    #    print("Form data:", registerform.data)
    #    flash(f"Validation failed: {registerform.errors}")
    return render_template('register_customer.html', form=registerform, title='Register')

@app.route('/registervendor', methods=['GET','POST'])
def register_vendor():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    registerform=Vendor_Register_Form()
    if registerform.validate_on_submit():

        customer_location = Location_Handler.Address_LookUp(registerform.location.data)
        location_dict = Location_Handler.Reverse_Address_LookUp(customer_location)

        location = Locations(latitude=location_dict['latitude'],
                              longitude=location_dict['longitude'],
                              full_address=location_dict['full_address'],
                              name=location_dict['name'],
                              street=location_dict['street'],
                              city=location_dict['city'],
                              osm_id=location_dict['osm_id'],
                              osm_type=location_dict['osm_type'],
                              data_source=location_dict['data_source'])
        db.session.add(location)
        db.session.commit()
        #i have already checked the database for duplicates in the validate_name method in the forms module so ill just directly add the customer to the database
        
        time_str1 = registerform.opening_time.data
        time_str2 = registerform.closing_time.data  # example "14:30"

        hours1, minutes1 = map(int, time_str1.split(':'))
        time_obj1 = time(hour=hours1, minute=minutes1) # opening
        hours2, minutes2 = map(int, time_str2.split(':'))
        time_obj2 = time(hour=hours2, minute=minutes2) # closing
        
        vendor = Vendor(v_username=registerform.username.data,
                        v_phone=registerform.phone_number.data,
                        v_email=registerform.mail.data,
                        name=registerform.name.data,
                        working_hours_start=time_obj1,
                        working_hours_end=time_obj2)
        vendor.set_password(registerform.password.data)
        vendor.vendor_location_id = location.id
        db.session.add(vendor)
        db.session.commit()
        flash("Registeration successful")
        return redirect(url_for('login'))  #customer needs to login so that he can be added to current_user
    return render_template('register_vendor.html', form=registerform, title='Register')

@app.route('/registerdelivery', methods=['GET','POST'])
def register_delivery():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    registerform=DeliveryGuy_Register_Form()
    if registerform.validate_on_submit():
        #i have already checked the database for duplicates in the validate_name method in the forms module so ill just directly add the customer to the database
        delivery_guy = Delivery_Person(d_username=registerform.username.data,
                                       d_phone=registerform.phone_number.data,
                                       d_email=registerform.mail.data,
                                       name=registerform.name.data)
        delivery_guy.set_password(registerform.password.data)
        db.session.add(delivery_guy)
        db.session.commit()
        flash("Registeration successful")
        return redirect(url_for('login'))  #customer needs to login so that he can be added to current_user
    return render_template('register_delivery_person.html', form=registerform, title='Register')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#    <a href="{{ url_for('register_customer') }}">Register as Customer</a>
#                         <a href="{{ url_for('register_vendor') }}">Register as Vendor</a>
#                         <a href="{{ url_for('register_delivery') }}">Register as Delivery Guy</a>

@app.route('/additem', methods=['GET', 'POST'])
@login_required
def additem(): 
    additem_form = Add_Menu_Form()
    if additem_form.validate_on_submit():
        menu= Menu(vendor_id=sa.select(Vendor.id).where(Vendor.vendor_username == current_user.username ),name=additem_form.name.data, discount=additem_form.discount.data,price=additem_form.price.data )
        db.session.add(menu)
        db.session.commit()
        
    return render_template('additem.html', form=additem_form)

@app.route('/edititem', methods=['POST', 'GET'])
@login_required
def edititem():
    id=db.session.query(Vendor.id).filter(Vendor.vendor_username==current_user.username).scalar()
    items = Menu.query.filter(Menu.vendor_id == id).order_by(Menu.item_id.desc()).all()


    return render_template('edititem.html', items=items)
@app.route('/deleteitem/<int:id>', methods=['POST'])
@login_required
def deleteitem(id):
    item=Menu.query.get_or_404(id)  #returns the row with the primary key = id 
    try:
        db.session.delete(item)
        db.session.commit()
        flash("Successfully deleted item")
    except:
        #figure out how to display the error message
        flash("Shit went down cuh")
    id=db.session.query(Vendor.id).filter(Vendor.vendor_username==current_user.username).scalar()
    items= Menu.query.filter(Menu.vendor_id==id).all()
    return render_template('edititem.html', items=items) #page reloads everytime you delete something lol

@app.route('/updateitem/<int:id>', methods=['POST','GET'])
@login_required
def updateitem(id):
    Item=Menu.query.order_by(Menu.item_id.desc()).get_or_404(id)
    UpdateForm=Add_Menu_Form()
    if UpdateForm.validate_on_submit():
        Item.name = UpdateForm.name.data
        Item.price= UpdateForm.price.data
        Item.discount = UpdateForm.discount.data
        db.session.add(Item)
        db.session.commit()
        return redirect(url_for('edititem'))
    elif request.method == 'GET':
        UpdateForm.name.data = Item.name
        UpdateForm.price.data = Item.price
        UpdateForm.discount.data = Item.discount
    return render_template('updateform.html',form=UpdateForm, id=id)

@app.route('/display_cuisine/<string:cuisine>', methods=['GET','POST'])
@login_required
def display_cuisine(cuisine):
    query= sa.select(Menu).filter(Menu.category==cuisine).order_by(Menu.item_id.desc())
    page=request.args.get('page',1, type=int)
    item = db.paginate(query, page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('display_cuisine', page=item.next_num, cuisine=cuisine) \
        if item.has_next else None
    prev_url = url_for('display_cuisine', page=item.prev_num, cuisine=cuisine) \
        if item.has_prev else None
    return render_template('cuisinedisplay.html',items=item.items, next_url=next_url, prev_url=prev_url)
