CREATE TABLE customer_profile (
    username VARCHAR(30),
    user_password VARCHAR(8) NOT NULL,  --the password will ideally have to be encrypted before it is stored, but that is for later.
    user_phone VARCHAR(11),
    user_email VARCHAR(30),
    user_reg_date DATE NOT NULL,
    CONSTRAINT username_pk 
    PRIMARY KEY(username)
    );


CREATE TABLE vendor_profile (
    vendorname VARCHAR(50),
    vendor_password VARCHAR(8) NOT NULL,
    vendor_phone VARCHAR(11),
    vendor_email VARCHAR(30),
    vendor_reg_date DATE NOT NULL,
    vendor_verified NUMBER(1) DEFAULT 1 NOT NULL, ---no booelans in oralle 11g sadly..
    CONSTRAINT vendorname_pk
    PRIMARY KEY(vendorname),
    CONSTRAINT verified_check
    CHECK (vendor_verified = 1 OR vendor_verified = 0)
    );

ALTER TABLE vendor_profile RENAME COLUMN vendorname TO vendorusername;
--CREATE TABLE location (
--    location_id INT,
--    address VARCHAR(50),
--    city VARCHAR(20)

CREATE TABLE region (
    region_id INT,
    region_name VARCHAR(20) NOT NULL,
    CONSTRAINT regionid_pk
    PRIMARY KEY(region_id)
    );

CREATE TABLE country (
    country_id INT,
    country_name VARCHAR(30) NOT NULL,
    region_id INT,
    CONSTRAINT countryid_pk
    PRIMARY KEY (country_id),
    CONSTRAINT regionid_fk
    FOREIGN KEY (region_id)
    REFERENCES region(region_id)
    );
CREATE TABLE locations (
    location_id INT,
    country_id INT,
    address VARCHAR(50) NOT NULL,
    city VARCHAR(30) NOT NULL,
    coordinates VARCHAR(50) NOT NULL, --fuck ass attribute
    postal_code VARCHAR(12),
    CONSTRAINT locationid_pk
    PRIMARY KEY(location_id),
    CONSTRAINT countryid_fk
    FOREIGN KEY(location_id) 
    REFERENCES country(country_id)
    );
ALTER TABLE locations DROP COLUMN coordinates;
CREATE TABLE customer ( 
    customer_id INT,
    location_id INT,
    customer_firstname varchar(30) NOT NULL,
    customer_lastname varchar(30) NOT NULL,
    customer_username VARCHAR(30),
    CONSTRAINT customerid_pk
    PRIMARY KEY(customer_id),
    CONSTRAINT locationid_fk
    FOREIGN KEY(location_id) 
    REFERENCES locations(location_id),
    CONSTRAINT c_username_fk
    FOREIGN KEY(customer_username)
    REFERENCES customer_profile(username)
    );

CREATE TABLE vendor (
    vendor_id INT,
    location_id INT,
    vendor_username VARCHAR(30),
    workinghr_start DATE NOT NULL,   --oracle doesnt have a dedicated datatype that solely stores time. We will ignore the date part and only extract the time part while running queries
    workinghr_end DATE NOT NULL,
    CONSTRAINT vendorid_pk
    PRIMARY KEY (vendor_id),
    CONSTRAINT v_locationid_fk
    FOREIGN KEY(location_id)
    REFERENCES locations(location_id),
    CONSTRAINT v_username_fk
    FOREIGN KEY(vendor_username)
    REFERENCES vendor_profile(vendorusername)
    );
ALTER TABLE vendor ADD CONSTRAINT time_check CHECK(workinghr_start < workinghr_end);
    
CREATE TABLE items (
    vendor_id INT,
    item_id INT,
    item_name VARCHAR(30) NOT NULL,
    item_discount DECIMAL(4,2) DEFAULT 0 NOT NULL,
    type1 VARCHAR(30) NOT NULL,
    type2 VARCHAR(30) NOT NULL,
    type3 VARCHAR(30) NOT NULL,
    type4 VARCHAR(30) NOT NULL,
    price NUMBER(6,2) NOT NULL,
    prep_time INTERVAL DAY TO SECOND NOT NULL,  --datatype can be changed later  it saves the interval as : 'D HH:MM:SS' D-> day
    item_rating INT,
    CONSTRAINT itemid_pk 
    PRIMARY KEY(item_id),
    CONSTRAINT vendorid_fk
    FOREIGN KEY(vendor_id)
    REFERENCES vendor(vendor_id),
    CONSTRAINT rating_chck
    CHECK ( item_rating >=0 AND item_rating <= 5)
    );

CREATE TABLE it_profile (
    delivery_username VARCHAR(30),
    delivery_password VARCHAR(8) NOT NULL,
    delivery_phone VARCHAR(11),
    delivery_email VARCHAR(30),
    delivery_reg_date DATE NOT NULL,
    last_paid_date DATE,    --initially NULL?
    license_status VARCHAR(10) NOT NULL,
    expiry_date DATE NOT NULL,
    CONSTRAINT deliveryusername_pk
    PRIMARY KEY (delivery_username),
    CONSTRAINT licence_stat_check
    CHECK (license_status = 'EXPIRED' OR license_status = 'VALID')
    );
    
CREATE TABLE it (
    delivery_id INT,
    delivery_username VARCHAR(30),
    base_loc_id INT,
    curr_loc_id INT,
    delivery_f_name VARCHAR(30) NOT NULL,
    delivery_l_name VARCHAR(30) NOT NULL,
    delivary_status VARCHAR(10) NOT NULL,
    salary_per_hr NUMBER(5,2) NOT NULL,
    worked_hrs_per_week NUMBER (5,2) DEFAULT 0 NOT NULL,
    wallet_money NUMBER(7,2) DEFAULT 0 NOT NULL,
    delivery_starthr DATE NOT NULL,
    delivery_endhr DATE NOT NULL,
    CONSTRAINT deliveryid_pk
    PRIMARY KEY(delivery_id),
    CONSTRAINT delusername_fk
    FOREIGN KEY(delivery_username)
    REFERENCES it_profile(delivery_username),
    CONSTRAINT basloc_fk
    FOREIGN KEY(base_loc_id)
    REFERENCES locations(location_id),
    CONSTRAINT curlocid_fk
    FOREIGN KEY(curr_loc_id)
    REFERENCES locations(location_id),
    CONSTRAINT workedhrsalary_check
    CHECK (worked_hrs_per_week <= 168),  --no rest
    CONSTRAINT hr_check 
    CHECK (delivery_endhr > delivery_starthr)
    );
    
    
    
CREATE TABLE orders (
    delivery_id INT,
    order_id INT,
    order_list INT, ---self join the item id I think
    item_id INT,
    customer_id INT,
    order_status VARCHAR(10) NOT NULL,
--    EAT 
    instructions VARCHAR(50),
    quantity INT NOT NULL,
    CONSTRAINT orderid_pk
    PRIMARY KEY(order_id),
    CONSTRAINT delivery_fk
    FOREIGN KEY(delivery_id) 
    REFERENCES it(delivery_id),
    CONSTRAINT itemid_fk
    FOREIGN KEY(item_id)
    REFERENCES items(item_id),
    CONSTRAINT customerid_fk
    FOREIGN KEY (customer_id)
    REFERENCES customer(customer_id),
    CONSTRAINT status_check
    CHECK ( order_status = 'PENDING' OR order_status = 'ACCEPT' OR order_status ='REJECT' OR order_status ='PREPPING' OR order_status ='READY' OR order_status ='DISPATCHED'
         OR order_status ='DELIVERED' OR order_status ='CANCELLED'),
    CONSTRAINT quantity_chck
    CHECK (quantity > 0 )
         );
         
CREATE TABLE history AS (
    SELECT * 
    FROM orders
    );


CREATE TABLE reviews (
    review_id INT,
    item_id INT,
    customer_id INT,
    review_str VARCHAR(200),
    CONSTRAINT reviewid_pk
    PRIMARY KEY(review_id),
    CONSTRAINT itemid2_fk
    FOREIGN KEY(item_id)
    REFERENCES items(item_id),
    CONSTRAINT customerid2_fk
    FOREIGN KEY(customer_id)
    REFERENCES customer(customer_id)
    );
    
    
CREATE TABLE accounts (
    acc_id INT,
    delivery_id INT,
    salary_per_hr NUMBER(5,2) NOT NULL,
    worked_hrs_per_week NUMBER (5,2) DEFAULT 0 NOT NULL,
    wallet_return NUMBER(7,2) DEFAULT 0 NOT NULL,
    CONSTRAINT accid_pk
    PRIMARY KEY(acc_id),
    CONSTRAINT deliveryid2_fk
    FOREIGN KEY (delivery_id)
    REFERENCES it(delivery_id)
    );
    
    