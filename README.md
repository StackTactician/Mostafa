# Mostafa Food Delivery

A CLI food delivery application built with Django.

## Features

- **User Roles**: Customer and Driver.
- **Restaurant Management**: Menu items, orders.
- **Order Flow**: Place order, driver acceptance, delivery confirmation.
- **Dashboard**: Customer and Driver dashboards.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd food-delivery-app
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Setup:**
    - Ensure PostgreSQL is running.
    - Create a database named `food_delivery`.
    - Update `food_delivery_project/settings.py` with your database credentials if necessary.

5.  **Run Migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```

## Scripts

Utility scripts are located in the `scripts/` directory.

- `python scripts/populate_data.py`: Populates the database with initial data.
- `python scripts/verify_auth_flow.py`: Verifies the authentication and order flow.
