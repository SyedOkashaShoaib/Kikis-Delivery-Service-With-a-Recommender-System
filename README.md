# Kiki's Delivery Service

A full-stack food delivery platform built with Flask and PostgreSQL. Features a hybrid AI recommendation engine, geospatial driver assignment, and dedicated dashboards for three distinct user roles.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
  - [Multi-Role Architecture](#multi-role-architecture)
  - [Recommendation Engine](#recommendation-engine)
  - [Geospatial Logistics](#geospatial-logistics)
- [Database Design](#database-design)
- [Setup and Installation](#setup-and-installation)
- [Configuration](#configuration)

---

## Overview

Kiki's Delivery Service is a multi-role web application that manages the full lifecycle of a food delivery platform — from menu browsing and order placement through to driver assignment and delivery tracking. The platform integrates a custom-built hybrid recommendation engine that personalizes menu feeds per user, and uses geospatial APIs to automate delivery routing and address validation.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-Migrate |
| Database | PostgreSQL, SQLAlchemy ORM |
| Recommendation Engine | NumPy, scikit-learn |
| Geospatial | Geopy (Nominatim, Photon) |
| Authentication | Flask-Login, Flask-Bcrypt |
| Frontend | HTML5, CSS3, Vanilla JavaScript, Jinja2 |

---

## Project Structure

```
Kikis-Delivery-Service/
|
|-- app/
|   |-- models.py            # SQLAlchemy schemas and table relationships
|   |-- routes.py            # Route definitions and controller logic
|   |-- vectorizer.py        # Content-based item vectorization and scoring
|   |-- user_vectorizer.py   # User vector construction for collaborative filtering
|   |-- templates/           # Jinja2 HTML templates
|   |-- static/              # CSS, JavaScript, and image assets
|
|-- migrations/              # Alembic database migration scripts
|-- run.py                   # Application entry point
|-- requirements.txt         # Python dependencies
```

---

## Features

### Multi-Role Architecture

The platform supports three independently scoped user roles, each with dedicated dashboards and route-level access control enforced via Flask-Login:

- **Customers** — browse menus, place and track orders, view order history
- **Vendors** — manage menu listings, monitor incoming orders, update order statuses
- **Delivery Personnel** — view assigned deliveries, update delivery progress, manage availability

### Recommendation Engine

Menu recommendations are generated using a hybrid approach combining content-based filtering and collaborative filtering.

**Content-based filtering (`vectorizer.py`):**
Each menu item is represented as a feature vector incorporating category tags, price (min-max normalized), and a Bayesian-averaged rating that smooths scores for items with low review counts. Item similarity is computed using cosine similarity via scikit-learn.

**Collaborative filtering (`user_vectorizer.py`):**
Each user is represented as a preference vector derived from their order history. Candidate items are ranked by cosine similarity between the user vector and item vectors, allowing the engine to surface items ordered by similar users.

The two signals are combined at query time to produce a ranked feed returned to the customer dashboard.

### Geospatial Logistics

Driver assignment and delivery distance calculation are handled using the Geopy library:

- **Nominatim and Photon APIs** are used for forward geocoding (address to coordinates) and address validation at order placement.
- Delivery distances are computed from geocoded coordinates to automate the assignment of the nearest available driver.
- Reverse geocoding is used to display human-readable location data on driver and vendor dashboards.

---

## Database Design

The relational schema is managed via SQLAlchemy ORM and versioned with Alembic migrations. Key entities include users (with role differentiation), vendors, menu items, orders, order line items, and delivery assignments. Relationships are enforced at the ORM level with appropriate foreign key constraints and cascade rules.

---
