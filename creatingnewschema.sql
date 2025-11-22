CREATE USER food_delivery_project IDENTIFIED BY food_123;
GRANT CONNECT, RESOURCE TO food_delivery_project;
ALTER USER food_delivery_project QUOTA UNLIMITED ON USERS;  