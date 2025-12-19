from flask import render_template, flash, redirect, url_for, request, session, jsonify
from app import app, db
from app.models import Menu, Vendor, Delivery_Person, Customer, Locations, Order, Order_Items
from app.forms import LoginForm, Customer_Register_Form, Add_Menu_Form, Vendor_Register_Form, DeliveryGuy_Register_Form
from flask_login import current_user, login_user, logout_user, login_required
from app.geocoder_test import Location_Handler # Static methods
from datetime import time
from sqlalchemy import func, select, or_
import sqlalchemy as sa
from urllib.parse import urlsplit
from datetime import datetime, timedelta
from app.vectorizer import compute_all_item_vectors, compute_item_similarity_matrix, recommend_similar_items, load_all_item_vectors
from app.user_vectorizer import compute_all_user_vectors, recommend_items_for_user, recommend_items_hybrid

@app.route('/customer_dashboard', methods=['GET'])
@login_required
def get_customer_dashboard():
    query= sa.select(Menu).order_by(Menu.item_id.desc()) #im gonna filter by working hours and other stuff after I have u[dated ] the schema with kumail
    page=request.args.get('page',1, type=int)
    item = db.paginate(query, page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('get_customer_dashboard', page=item.next_num) \
        if item.has_next else None
    prev_url = url_for('get_customer_dashboard', page=item.prev_num) \
        if item.has_prev else None
    print(recommend_similar_items(item_id=42, top_n=5))

    user_vectors = compute_all_user_vectors()
    item_vectors = load_all_item_vectors()

    recs = recommend_items_for_user(current_user.id, user_vectors)
    print(recs)

    hybrid_recs = recommend_items_hybrid(current_user.id, user_vectors, item_vectors)
    # first_elements = [tup[0] for tup in list_of_tuples]
    index = [tup[0] for tup in hybrid_recs]
    print(index)
    rec_items = []
    for x in index:
        temp = Menu.query.filter(Menu.item_id == x).order_by(Menu.item_id.desc()).all()
        rec_items.extend(temp)
    # print(hybrid_recs)
    print(rec_items)

    return render_template('customer_dashboard.html',items=item.items,rec_items=rec_items, next_url=next_url, prev_url=prev_url)

@app.route('/home')
@login_required   # redirects you to the function declared in login_view in innit file
def home():
    if session['user_type'] == 'customer':
        return redirect(url_for('get_customer_dashboard'))
    elif session['user_type'] == 'vendor':
        pending_orders = db.session.scalar(sa.select(func.count(Order.order_id)).where(Order.vendor_id == current_user.id and Order.order_status == "PENDING")) ### change the constant 1
        return render_template("vendor_dashboard.html", pending_orders = pending_orders)
    elif session['user_type'] == 'delivery':
        delivery_person = Delivery_Person.query.filter_by(id=current_user.id).first()
        driver = current_user  # assuming current_user is a Delivery_Person
        # Query the order that is currently assigned to this driver
        current_job = Order.query.filter_by(delivery_id=driver.id, order_status='DISPATCHED').first()
        return render_template("deliveryguy_dashboard.html", delivery_person=delivery_person, current_job=current_job)
    
@app.route("/api/pending-count") # Dynamicaly update Badge to dispaly the current number of pending orders
def pending_count():
    if session['user_type'] != 'vendor':
        return jsonify(0)
    count = db.session.scalar(
        sa.select(func.count(Order.order_id))
        .where(Order.vendor_id == current_user.id, Order.order_status == "PENDING")
    )
    return jsonify(count=count)

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
        menu= Menu(vendor_id= current_user.id,
                   name=additem_form.name.data,
                   discount=additem_form.discount.data,
                   price=additem_form.price.data,
                   cuisine=additem_form.cuisine.data,
                   category=additem_form.category.data,
                   Type=additem_form.type.data,
                   prep_time=additem_form.prep_time.data)
        db.session.add(menu)
        db.session.commit()

        compute_all_item_vectors()
        compute_item_similarity_matrix()
        
    return render_template('additem.html', form=additem_form)

@app.route('/edititem', methods=['POST', 'GET'])
@login_required
def edititem():
    id=current_user.id
    items = Menu.query.filter(Menu.vendor_id == id).order_by(Menu.item_id.desc()).all()
    return render_template('edititem.html', items=items)

@app.route('/deleteitem/<int:id>', methods=['POST'])
@login_required
def deleteitem(id):
    item=Menu.query.get_or_404(id)  #returns the row with the primary key = id 
    try:
        db.session.delete(item)
        db.session.commit()
    except:
        pass
        #figure out how to display the error message
    id=current_user.id
    items= Menu.query.filter(Menu.vendor_id==id).all()
    compute_all_item_vectors()
    compute_item_similarity_matrix()
    return render_template('edititem.html', items=items) #page reloads everytime you delete something lol

@app.route('/updateitem/<int:id>', methods=['POST','GET'])
@login_required
def updateitem(id):
    Item=Menu.query.get_or_404(id)
    UpdateForm=Add_Menu_Form()
    if UpdateForm.validate_on_submit():
        Item.name = UpdateForm.name.data
        Item.price= UpdateForm.price.data
        Item.discount = UpdateForm.discount.data
        Item.cuisine = UpdateForm.cuisine.data
        Item.category = UpdateForm.category.data
        Item.Type = UpdateForm.type.data
        Item.prep_time = UpdateForm.prep_time.data
        db.session.add(Item)
        db.session.commit()
        return redirect(url_for('edititem'))
    elif request.method == 'GET':
        UpdateForm.name.data = Item.name
        UpdateForm.price.data = Item.price
        UpdateForm.discount.data = Item.discount
        UpdateForm.cuisine.data = Item.cuisine
        UpdateForm.category.data = Item.category
        UpdateForm.type.data = Item.Type
        UpdateForm.prep_time.data = Item.prep_time
    return render_template('updateform.html',form=UpdateForm, id=id)

@app.route('/vieworders', methods=['POST', 'GET'])
@login_required
def vieworders():
    orders = Order.query.filter(Order.vendor_id == current_user.id).order_by(Order.order_id.desc()).all()
    return render_template("orders.html", orders=orders)

@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)

    if order.order_status == "PENDING":
        order.order_status = "ACCEPTED"

    elif order.order_status == "ACCEPTED":
        order.order_status = "PREPARING"

    elif order.order_status == "PREPARING":
        order.order_status = "READY"

    # READY stays ready (button disabled)

    db.session.commit()
    return redirect(request.referrer)

@app.route('/display_cuisine/<string:cuisine>', methods=['GET','POST'])
@login_required
def display_cuisine(cuisine):
    print(cuisine)
    query= sa.select(Menu).filter(Menu.category==cuisine).order_by(Menu.item_id.desc())
    page=request.args.get('page',1, type=int)
    item = db.paginate(query, page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('display_cuisine', page=item.next_num, cuisine=cuisine) \
        if item.has_next else None
    prev_url = url_for('display_cuisine', page=item.prev_num, cuisine=cuisine) \
        if item.has_prev else None
    return render_template('cuisinedisplay.html',items=item.items, next_url=next_url, prev_url=prev_url, cuisine= cuisine)

def calculate_total(id):
    items=Order_Items.query.filter(Order_Items.order_id == id).all()
    total= 25
    for x in items:
        total+=x.menu_item.price * x.quantity
    return total

@app.route('/add_to_cart/<int:vendor_id>/<int:item_id>', methods=['POST','GET'])
@login_required
def add_to_cart(vendor_id, item_id):
    order = Order.query.filter_by(customer_id=current_user.id, order_status='IN_CART').first()
    if not order:
        order = Order(customer_id=current_user.id, order_status='IN_CART', vendor_id=vendor_id)
        db.session.add(order)
        db.session.commit()
    new_item = Order_Items(order_id=order.order_id, item_id=item_id)
    db.session.add(new_item)
    db.session.commit()
    order.total = calculate_total(order.order_id)
    db.session.commit()
    
    return redirect(url_for('cart'))

@app.route('/cart')
@login_required
def cart():
    order = Order.query.filter_by(customer_id=current_user.id,order_status='IN_CART').first()
    if not order:
        return render_template('cart.html', cart_items=None, total = 0)

    cart_items = Order_Items.query.filter_by(order_id=order.order_id).all()
    return render_template('cart.html', cart_items=cart_items, total=order.total)

@app.route('/deletecartitem/<int:id>', methods=['POST'])
@login_required
def deletecartitem(id):
    item=Order_Items.query.get_or_404(id)  #returns the row with the primary key = id 
    order_id = item.order_id
    try:
        db.session.delete(item)
        db.session.commit()
        db.session.commit()

        order = Order.query.get(order_id)
        order.total = calculate_total(order_id)
        db.session.commit()

        flash("Successfully deleted item")
    except:
        pass
        #figure out how to display the error message
    return redirect(url_for('cart'))
    
@app.post('/set_quantity')
@login_required
def set_quantity():
    order_item_id = request.form.get('order_item_id')
    qty = request.form.get('quantity')

    cart_item = Order_Items.query.get_or_404(order_item_id)
    cart_item.quantity = qty
    db.session.commit()

    order = Order.query.get(cart_item.order_id)
    order.total = calculate_total(order.order_id)
    db.session.commit()

    return redirect(url_for('cart'))

@app.route('/place_order', methods=['GET','POST'])
@login_required
def place_order():
    order = Order.query.filter_by(customer_id=current_user.id, order_status='IN_CART').first()
    order.order_status = 'PENDING'
    db.session.commit()
    flash("Your order has been sent to the vendor ")
    return redirect(url_for('cart'))

@app.route('/previous_orders', methods=['GET','POST'])
@login_required
def previous_orders():
    items = []
    order = Order.query.filter_by(customer_id=current_user.id, order_status='DELIVERED').all()
    for x in order:
        for oi in x.order_items:
            items.append(oi.menu_item)
    return render_template('previousorders.html', items=items)

@app.route('/add_rating/<int:item_id>', methods=['GET', 'POST'])
@login_required
def add_rating(item_id):
    item = Menu.query.get_or_404(item_id)
    item.rating = ((item.rating * item.ratings_count) + int(request.form.get('rating'))) / (item.ratings_count + 1)
    db.session.commit()
    flash("Thank you for rating this item!")
    return redirect (url_for('previous_orders'))

@app.route('/apply_filters', methods=['GET'])
@login_required
def apply_filters():
    filter_args={}
    discount = request.args.get('discount_only')
    max_price = request.args.get('max_price')
    rating = request.args.get('rating_4_plus')
    prep_time = request.args.get('prep_time')
    cuisine = request.args.get('cuisine')
    query = Menu.query

    if cuisine:
        query = query.filter(Menu.category == cuisine)
        
    if discount: 
        query = query.filter(Menu.discount > 0)
    if max_price: 
        query = query.filter(Menu.price <= float(max_price))
    if rating:
        query = query.filter(Menu.rating >=4)
    if prep_time:
        query = query.filter(Menu.prep_time <= int(prep_time))
    for x,y in request.args.items():
        filter_args[x] = y
    print(filter_args)
    page=request.args.get('page',1, type=int)
    item = db.paginate(query, page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    next_url = url_for('apply_filters', page=item.next_num, **filter_args) \
        if item.has_next else None
    prev_url = url_for('apply_filters', page=item.prev_num, **filter_args) \
        if item.has_prev else None
    if cuisine:
        return render_template('cuisinedisplay.html',items=item.items, next_url=next_url, prev_url=prev_url, cuisine=cuisine)
    
    return render_template('customer_dashboard.html',items=item.items, next_url=next_url, prev_url=prev_url)
    
@app.route("/deliveryguy_dashboard/update_location", methods=["POST"])
@login_required
def update_location():
    data = request.json
    # Update or create location record for current user
    delivery_person = Delivery_Person.query.get(current_user.id)
    if not delivery_person.location:
        # create a new Locations record
        new_loc = Locations(full_address=data['location'], latitude=0, longitude=0, name='temp', street='temp', osm_id='temp', osm_type='temp', data_source='manual')
        db.session.add(new_loc)
        db.session.commit()
        delivery_person.current_location_id = new_loc.id
    else:
        delivery_person.location.full_address = data['location']
    db.session.commit()
    return jsonify(message="Location updated")

@app.route("/deliveryguy_dashboard/update_status", methods=["POST"])
@login_required
def update_status():
    data = request.json
    delivery_person = Delivery_Person.query.get(current_user.id)
    delivery_person.status = data['status']
    db.session.commit()
    return jsonify(message="Status updated")

def euclidean_distance(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5

OFFER_SECONDS = 60

@app.route("/api/pending-jobs")
@login_required
def pending_jobs():
    now = datetime.utcnow()

    driver = Delivery_Person.query.get(current_user.id)
    if not driver or not driver.v_verified or driver.status != "ON_DUTY" or not driver.current_location_id:
        return jsonify(jobs=[])

    expired_q = Order.__table__.update().where(
        Order.offer_expires_at != None,
        Order.offer_expires_at < now
    ).values(offered_to_driver_id=None, offer_expires_at=None)
    db.session.execute(expired_q)
    db.session.commit()

    candidate_stmt = ( ## eligible orders
        select(Order)
        .where(
            Order.delivery_id.is_(None),
            Order.order_status.in_(["ACCEPTED", "PREPARING", "READY"])
        )
        .with_for_update(skip_locked=True)
    )

    result = db.session.execute(candidate_stmt).scalars().all()
    if not result:
        return jsonify(jobs=[])

    driver_loc = driver.location  
    if not driver_loc:
        return jsonify(jobs=[])

    candidate_list = []
    for order in result:
        vendor_loc = getattr(order.vendor, "location", None)
        customer_loc = getattr(order.customer, "location", None)
        if not vendor_loc or not customer_loc:
            continue

        try:
            dist = euclidean_distance(
                float(driver_loc.latitude),
                float(driver_loc.longitude),
                float(vendor_loc.latitude),
                float(vendor_loc.longitude),
            )
        except Exception:
            continue

        candidate_list.append((dist, order))

    if not candidate_list:
        return jsonify(jobs=[])

    candidate_list.sort(key=lambda t: t[0])

    for dist, order in candidate_list:
        if order.offered_to_driver_id == driver.id and order.offer_expires_at and order.offer_expires_at > now:
            time_left = int((order.offer_expires_at - now).total_seconds())
            job = {# dictionary passed to front end and will be displayed at dashboard
                "order_id": order.order_id,
                "pickup": order.vendor.location.full_address,
                "dropoff": order.customer.location.full_address,
                "distance": float(dist),
                "seconds_left": time_left
            }
            return jsonify(jobs=[job])

        if order.offered_to_driver_id is None:
            claim_stmt = (
                Order.__table__.update()
                .where(Order.order_id == order.order_id, Order.offered_to_driver_id.is_(None))
                .values(
                    offered_to_driver_id=driver.id,
                    offer_expires_at=now + timedelta(seconds=OFFER_SECONDS)
                )
            )
            res = db.session.execute(claim_stmt)
            if res.rowcount:  # we successfully claimed it
                db.session.commit()
                job = {
                    "order_id": order.order_id,
                    "pickup": order.vendor.location.full_address,
                    "dropoff": order.customer.location.full_address,
                    "distance": float(dist),
                    "seconds_left": OFFER_SECONDS
                }
                return jsonify(jobs=[job])
            else:
                # someone else claimed it
                db.session.rollback()
                continue

    # nothing claimed 
    return jsonify(jobs=[])

@app.route("/accept_job/<int:order_id>", methods=["POST"])
@login_required
def accept_job(order_id):
    now = datetime.utcnow()
    order = Order.query.get_or_404(order_id)

    # verify the order is offered to this driver and still within the offer window
    if order.offered_to_driver_id != current_user.id:
        return jsonify(success=False, error="Not offered to you"), 403

    if not order.offer_expires_at or order.offer_expires_at < now:
        return jsonify(success=False, error="Offer expired"), 400

    order.delivery_id = current_user.id
    current_user.status = "IN_JOB"
    order.offered_to_driver_id = None
    order.offer_expires_at = None
    order.order_status = "DISPATCHED" 
    db.session.commit()

    clear_my_offers = ( # clean table and free up jobs for other drivers
    Order.__table__.update()
    .where(Order.offered_to_driver_id == current_user.id)
    .values(offered_to_driver_id=None, offer_expires_at=None)) 

    db.session.execute(clear_my_offers)
    db.session.commit()

    return jsonify(success=True)

@app.route("/api/mark-delivered/<int:order_id>", methods=["POST"])
@login_required
def mark_delivered(order_id):
    driver = Delivery_Person.query.get(current_user.id)
    if not driver or driver.status != "IN_JOB":
        return jsonify({"success": False, "error": "You have no active job."})

    order = Order.query.get(order_id)
    if not order or order.delivery_id != driver.id:
        return jsonify({"success": False, "error": "Invalid order or not assigned to you."})

    try:
        order.order_status = "DELIVERED"
        order.delivery_id = None
        order.offered_to_driver_id = None
        order.offer_expires_at = None

        dropoff_loc = order.customer.location
        if dropoff_loc:
            driver.current_location_id = dropoff_loc.id # make new location for driver. where he dropped off delivery and he becomes eligible for new job
        driver.status = "ON_DUTY"

        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})


