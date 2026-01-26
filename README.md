# Food Delivery App

A full-stack food delivery application built with Django.

## Features

- **User Roles**: Customer and Driver.
- **Restaurant Management**: Menu items, orders.
- **Order Flow**: Place order, driver acceptance, delivery confirmation.
- **Dashboard**: Customer and Driver dashboards.

## Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd food-delivery-app
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
- Ensure PostgreSQL is running
- Create a database named `food_delivery`
- Update `food_delivery_project/settings.py` with your database credentials if necessary

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

7.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```

## Scripts

Utility scripts are located in the `scripts/` directory:

- `python scripts/populate_data.py`: Populates the database with sample data
- `python scripts/verify_auth_flow.py`: Verifies authentication and order flow
- `python manage.py seed_db`: Comprehensive database seeding

## Technology Stack

### Backend
- Django 5.0+
- Django REST Framework
- PostgreSQL
- JWT Authentication

### CLI
- Typer (CLI framework)
- Rich (terminal formatting)
- Questionary (interactive prompts)
- Requests (HTTP client)

## Project Structure

```
food-delivery-app/
├── cli.py                      # Main CLI application
├── cli/                        # CLI module
│   ├── api.py                 # API service layer
│   └── ui.py                  # UI/display functions
├── delivery/                   # Django app
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── api_views.py           # API views
│   └── management/commands/   # Management commands
├── food_delivery_project/      # Django project settings
├── scripts/                    # Utility scripts
└── requirements.txt           # Python dependencies
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License
