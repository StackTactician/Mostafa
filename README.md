# Mostafa Food Delivery CLI

A command-line interface (CLI) food delivery application built with Django. This application allows users to interact with the food delivery service directly from their terminal.

## Features

- **User Roles**: Customer and Driver roles accessible via CLI commands.
- **Restaurant Management**: Manage menu items and orders through CLI commands.
- **Order Flow**: Place orders, accept driver assignments, and confirm deliveries, all via the command line.
- **Dashboard**: Access customer and driver dashboards using CLI commands to view relevant information.

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

## Usage (CLI Commands)

Once the setup is complete, you can interact with the application using the following CLI commands:

-   **Running the application**: Since this is a CLI application, you will primarily interact with it through custom management commands or scripts. Refer to the `cli/` directory for available commands.

    ```bash
    python manage.py <command> [options]
    ```

    Example:
    ```bash
    python manage.py list_restaurants
    ```

-   **Exploring available commands**: Check the `cli/` directory for custom Django management commands that implement the application's features.

## Scripts

Utility scripts are located in the `scripts/` directory.

- `python scripts/populate_data.py`: Populates the database with initial data.
- `python scripts/verify_auth_flow.py`: Verifies the authentication and order flow.
