# Mostafa CLI Application

A full-stack food delivery application with Django REST API backend and an interactive CLI frontend.

## Features

- **User Roles**: Customer and Driver with role-specific functionality
- **Restaurant Management**: Browse restaurants and menus
- **Shopping Cart**: Multi-item cart with add, remove, and checkout
- **Order Flow**: Place orders, track status, driver acceptance, delivery confirmation
- **Interactive CLI**: Rich terminal interface with interactive prompts and workflows
- **Authentication**: JWT-based secure authentication

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

### 7. Seed Database (Optional)
```bash
python manage.py seed_db
```

### 8. Run the Django Server
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`

## CLI Usage

The CLI application provides an interactive terminal interface for the food delivery system.

### Interactive Main Menu (Recommended)

**Start the interactive menu:**
```bash
python cli.py main
```

This provides a **persistent menu-driven interface** that:
- Shows your login status
- Provides context-aware options based on your role
- Returns to the menu after each action (no need to re-run commands)
- Guides you through all available features

This is the **easiest way** to use the app - just run `python cli.py menu` once and navigate through the options!

---

### Authentication Commands

**Register a new account:**
```bash
python cli.py register
```
Interactive prompts will guide you through:
- Username, email, password, phone number
- Role selection (Customer or Driver)
- Role-specific information (address for customers, license/vehicle info for drivers)

**Login:**
```bash
python cli.py login
```

**View your profile:**
```bash
python cli.py me
```

**Logout:**
```bash
python cli.py logout
```

### Restaurant & Menu Commands

**List all restaurants:**
```bash
python cli.py restaurants
```

**View menu for a specific restaurant:**
```bash
python cli.py menu <restaurant_id>
```

**Interactive browsing (recommended):**
```bash
python cli.py browse
```
This interactive workflow allows you to:
1. Browse all restaurants
2. Select a restaurant to view its menu
3. Add items to your cart
4. View cart and checkout

### Shopping Cart Commands

**Add item to cart:**
```bash
python cli.py cart add --item-id <ID> --quantity <QTY>
```

**View cart:**
```bash
python cli.py cart view
```

**Remove item from cart:**
```bash
python cli.py cart remove --item-id <ID>
```

**Clear cart:**
```bash
python cli.py cart clear
```

**Checkout:**
```bash
python cli.py cart checkout
```

### Order Commands

**Quick order (single item, bypasses cart):**
```bash
python cli.py order --item-id <ID> --qty <QUANTITY>
```

**View your orders:**
```bash
python cli.py orders
```

**Cancel an order:**
```bash
python cli.py cancel
# Or specify order ID directly:
python cli.py cancel <order_id>
```

### Driver Commands

**View available delivery jobs:**
```bash
python cli.py driver jobs
```

**Accept a job:**
```bash
python cli.py driver accept
# Or specify order ID directly:
python cli.py driver accept <order_id>
```

**Complete a delivery:**
```bash
python cli.py driver complete
# Or specify order ID directly:
python cli.py driver complete <order_id>
```

## Example Workflow

### Customer Workflow
```bash
# Start the interactive menu (recommended)
python cli.py main
# Then follow the on-screen prompts!

# OR use individual commands:
# 1. Register or login
python cli.py register

# 2. Browse restaurants and order
python cli.py browse

# 3. View your orders
python cli.py orders

# 4. Cancel if needed
python cli.py cancel
```

### Driver Workflow
```bash
# 1. Login as driver
python cli.py login

# 2. View available jobs
python cli.py driver jobs

# 3. Accept a job
python cli.py driver accept

# 4. Complete delivery
python cli.py driver complete
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
