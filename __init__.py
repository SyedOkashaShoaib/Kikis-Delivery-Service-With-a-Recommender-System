from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
# Flask is a class 
app = Flask(__name__)  #creating a Flask object..
# Flask uses the __name__ argument to determine the location of the application, 
#which in turn allows it to locate other files that are part of the
#  application, such as images and templates.
db = SQLAlchemy()
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login' #it tells flask-login that this function handles login. Now we can use this later to require users to login to access certain features
app.config.from_object('app.config.Config')
app.config['SECRET_KEY'] = 'ukasha0850' #definitely not standard practice for storing the secret key like this. Its used for making the forms safe (I think...)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:ukasha@localhost:5432/FoodDelivery_DB"

#URI stand s for Uniform resource identifier. Points to the resource that the app wants to connect to. Look up the syntax of this URI yourself :)
#passing a URI string like this is unsafe, its better to store it in a .env file but fuck it who cares 
db.init_app(app)
login.init_app(app)


from app import routes, models  #routes is import after all this is to avoid circlar imports problem 