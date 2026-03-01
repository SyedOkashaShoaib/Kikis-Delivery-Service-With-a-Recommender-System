# Kiki's Delivery Service
**Full-Stack Food Delivery Platform with an AI-Powered Recommender System**

Kiki's Delivery Service is a comprehensive, multi-role web application designed to handle the end-to-end logistics of a food delivery ecosystem. It goes beyond standard CRUD operations by integrating a custom hybrid recommendation engine to personalize user feeds and geospatial APIs to automate delivery assignments.

## Features

* **Multi-Role Architecture:** Dedicated, secure dashboards and distinct operational workflows for three user types: **Customers**, **Vendors**, and **Delivery Personnel**.
* **Intelligent AI Recommender System:** A built-in hybrid recommendation engine that dynamically curates menu feeds for users. It utilizes **NumPy** and **scikit-learn** to process content-based item vectors (incorporating tags, price normalization, and Bayesian averaged ratings) alongside user-vector collaborative filtering via cosine similarity.
* **Real-Time Geospatial Logistics:** Automates driver assignment and calculates precise delivery distances using the **Geopy** library (integrating Nominatim and Photon APIs) for active address validation and reverse geocoding.
* **Robust Relational Backend:** Built with **Flask** and **PostgreSQL**, utilizing **SQLAlchemy ORM** to manage complex database relationships between users, orders, menus, and transaction histories.
* **Responsive User Interface:** A clean, dynamic frontend built with **HTML5, CSS3, JavaScript**, and **Jinja2** templating.

## Tech Stack

**Backend & Core Logic:**
* Python 3
* Flask & Flask-Migrate
* PostgreSQL & Flask-SQLAlchemy (ORM)

**Artificial Intelligence & Data Processing:**
* NumPy
* scikit-learn

**Third-Party APIs & Libraries:**
* Geopy (Nominatim & Photon)
* Flask-Bcrypt (Password Hashing)
* Flask-Login (Session Management)

**Frontend:**
* HTML5 / CSS3 / Vanilla JavaScript
* Jinja2 Templating

## Project Structure Overview

* `/app`: Contains the core application logic.
  * `/models.py`: SQLAlchemy database schemas and relationships.
  * `/routes.py`: Endpoint definitions and controller logic.
  * `/vectorizer.py` & `/user_vectorizer.py`: The AI recommendation engine and scoring logic.
  * `/templates/`: Jinja2 HTML templates for the UI.
  * `/static/`: CSS styling, JavaScript files, and images.
* `/migrations`: Alembic scripts for database version control.
* `run.py`: The entry point for the Flask application.

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
