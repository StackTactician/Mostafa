from django.core.management.base import BaseCommand
import typer
from typing import Optional, Dict
import questionary
from questionary import Style
from cli.api import ApiService
from cli import ui

app = typer.Typer(help="Mostafa CLI Application")
api = ApiService()

# In-memory shopping cart
cart: Dict[int, int] = {}

# Custom style for questionary prompts
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])

# ==================== MAIN MENU ====================

@app.command()
def main():
    """Interactive main menu - browse, order, and manage your account."""
    while True:
        ui.clear_screen()
        ui.console.print("\n[bold magenta]Mostafa Main Menu[/bold magenta]\n")
        
        # Check if logged in
        profile = api.get_my_profile()
        if profile:
            username = profile.get('user', {}).get('username', 'User')
            role = profile.get('role', 'Unknown')
            ui.console.print(f"[green]Logged in as: {username} ({role})[/green]\n")
        else:
            ui.console.print("[yellow]Not logged in[/yellow]\n")
        
        # Build menu choices based on login status and role
        choices = []
        
        if not profile:
            choices.extend(["Login", "Register"])
        else:
            choices.extend([
                "Browse Restaurants",
                "View My Orders",
                "View Cart",
                "My Profile",
            ])
            
            # Add driver-specific options
            if profile.get('role') == 'Driver':
                choices.extend([
                    "Driver: View Jobs",
                    "Driver: Accept Job",
                    "Driver: Complete Job",
                ])
            
            choices.append("Logout")
        
        choices.append("Exit")
        
        action = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=custom_style
        ).ask()
        
        if not action or action == "Exit":
            ui.console.print("\n[cyan]Thanks for using Mostafa! Goodbye![/cyan]\n")
            break
        
        # Handle menu actions
        if action == "Login":
            ui.clear_screen()
            login()
        elif action == "Register":
            ui.clear_screen()
            register()
        elif action == "Browse Restaurants":
            ui.clear_screen()
            browse(return_to_menu=True)
        elif action == "View My Orders":
            ui.clear_screen()
            list_orders()
            input("\nPress Enter to continue...")
        elif action == "View Cart":
            ui.clear_screen()
            view_cart_internal()
            input("\nPress Enter to continue...")
        elif action == "My Profile":
            ui.clear_screen()
            ui.display_profile(profile)
            input("\nPress Enter to continue...")
        elif action == "Driver: View Jobs":
            ui.clear_screen()
            available_jobs()
            input("\nPress Enter to continue...")
        elif action == "Driver: Accept Job":
            ui.clear_screen()
            accept_job()
            input("\nPress Enter to continue...")
        elif action == "Driver: Complete Job":
            ui.clear_screen()
            complete_job()
            input("\nPress Enter to continue...")
        elif action == "Logout":
            logout()

# ==================== AUTHENTICATION COMMANDS ====================

@app.command()
def login():
    """Log in to the system with interactive prompts."""
    ui.console.print("\n[bold cyan]Login to Mostafa[/bold cyan]\n")
    
    username = questionary.text(
        "Username:",
        style=custom_style
    ).ask()
    
    if not username:
        ui.print_error("Login cancelled")
        return
    
    password = questionary.password(
        "Password:",
        style=custom_style
    ).ask()
    
    if not password:
        ui.print_error("Login cancelled")
        return
    
    success, msg = api.login(username, password)
    if success:
        ui.print_success(msg)
        profile = api.get_my_profile()
        if profile:
            role = profile.get('role', 'Unknown')
            ui.console.print(f"[green]Welcome back, {username}! ({role})[/green]")
    else:
        ui.print_error(msg)

@app.command()
def register():
    """Register a new user with interactive prompts and navigation."""
    from cli.registration import register_interactive
    register_interactive()

@app.command()
def logout():
    """Clear local session."""
    import os
    if os.path.exists(".token_cache"):
        confirm = questionary.confirm(
            "Are you sure you want to logout?",
            style=custom_style,
            default=True
        ).ask()
        
        if confirm:
            os.remove(".token_cache")
            api.access_token = None
            ui.print_success("Logged out successfully.")
        else:
            ui.console.print("[yellow]Logout cancelled[/yellow]")
    else:
        ui.print_error("You are not logged in.")

@app.command()
def me():
    """View my profile."""
    profile = api.get_my_profile()
    if profile:
        ui.display_profile(profile)
    else:
        ui.print_error("Could not fetch profile. Are you logged in?")

# ==================== RESTAURANT COMMANDS ====================

@app.command(name="restaurants")
def list_restaurants():
    """List all available restaurants."""
    data = api.get_restaurants()
    if data:
        ui.display_restaurants(data)
    else:
        ui.print_error("No restaurants found or you need to login.")

@app.command(name="menu")
def view_menu(restaurant_id: int):
    """View menu for a specific restaurant."""
    restaurants = api.get_restaurants()
    target_r = next((r for r in restaurants if r['id'] == restaurant_id), None)
    if target_r:
        ui.display_menu(target_r['name'], target_r['menu_items'])
    else:
        ui.print_error("Restaurant not found")

# ==================== INTERACTIVE BROWSE COMMAND ====================

@app.command()
def browse(return_to_menu: bool = False):
    """Interactive browsing: restaurants → menu → add to cart."""
    ui.clear_screen()
    ui.console.print("\n[bold magenta]Browse Restaurants & Menus[/bold magenta]\n")
    
    restaurants = api.get_restaurants()
    if not restaurants:
        ui.print_error("No restaurants available or you need to login.")
        return
    
    while True:
        # Display restaurants
        ui.display_restaurants(restaurants)
        
        # Create choices for restaurant selection
        restaurant_choices = [
            f"{r['id']}: {r['name']} ({r['cuisine']})" 
            for r in restaurants
        ]
        restaurant_choices.append("Exit")
        
        selected = questionary.select(
            "Select a restaurant to view menu:",
            choices=restaurant_choices,
            style=custom_style
        ).ask()
        
        if not selected or selected == "Exit":
            break
        
        # Extract restaurant ID
        restaurant_id = int(selected.split(":")[0])
        restaurant = next((r for r in restaurants if r['id'] == restaurant_id), None)
        
        if not restaurant:
            continue
        
        # Show menu
        ui.console.print(f"\n[bold cyan]Menu for {restaurant['name']}[/bold cyan]\n")
        ui.display_menu(restaurant['name'], restaurant['menu_items'])
        
        # Menu interaction loop
        while True:
            menu_choices = [
                f"{item['id']}: {item['name']} - ${item['price']}" 
                for item in restaurant['menu_items']
            ]
            menu_choices.extend(["View Cart", "Checkout", "Back to Restaurants"])
            
            menu_action = questionary.select(
                "Select an item to add to cart:",
                choices=menu_choices,
                style=custom_style
            ).ask()
            
            if not menu_action or menu_action == "Back to Restaurants":
                break
            elif menu_action == "View Cart":
                view_cart_internal()
            elif menu_action == "Checkout":
                checkout_cart()
                if not return_to_menu:
                    return
                else:
                    ui.console.print("\n[cyan]Returning to main menu...[/cyan]")
                    return
            else:
                # Add item to cart
                item_id = int(menu_action.split(":")[0])
                item = next((i for i in restaurant['menu_items'] if i['id'] == item_id), None)
                
                if item:
                    qty = questionary.text(
                        f"Quantity for {item['name']}:",
                        default="1",
                        style=custom_style
                    ).ask()
                    
                    try:
                        qty = int(qty)
                        if qty > 0:
                            cart[item_id] = cart.get(item_id, 0) + qty
                            ui.print_success(f"Added {qty}x {item['name']} to cart!")
                        else:
                            ui.print_error("Quantity must be positive")
                    except ValueError:
                        ui.print_error("Invalid quantity")

# ==================== CART COMMANDS ====================

cart_app = typer.Typer(help="Shopping cart management")
app.add_typer(cart_app, name="cart")

@cart_app.command("add")
def add_to_cart(item_id: int, quantity: int = 1):
    """Add an item to the shopping cart."""
    if quantity <= 0:
        ui.print_error("Quantity must be positive")
        return
    
    cart[item_id] = cart.get(item_id, 0) + quantity
    ui.print_success(f"Added {quantity}x item #{item_id} to cart!")

@cart_app.command("remove")
def remove_from_cart(item_id: int):
    """Remove an item from the shopping cart."""
    if item_id in cart:
        del cart[item_id]
        ui.print_success(f"Removed item #{item_id} from cart")
    else:
        ui.print_error("Item not in cart")

@cart_app.command("view")
def view_cart():
    """View current shopping cart."""
    view_cart_internal()

def view_cart_internal():
    """Internal function to view cart (used by both command and browse)."""
    if not cart:
        ui.console.print("[yellow]Your cart is empty[/yellow]")
        return
    
    # Fetch all restaurants to get item details
    restaurants = api.get_restaurants()
    all_items = {}
    for r in restaurants:
        for item in r['menu_items']:
            all_items[item['id']] = {
                'name': item['name'],
                'price': item['price'],
                'restaurant': r['name']
            }
    
    ui.display_cart(cart, all_items)

@cart_app.command("clear")
def clear_cart():
    """Clear all items from the shopping cart."""
    if not cart:
        ui.console.print("[yellow]Cart is already empty[/yellow]")
        return
    
    confirm = questionary.confirm(
        "Are you sure you want to clear the cart?",
        style=custom_style,
        default=False
    ).ask()
    
    if confirm:
        cart.clear()
        ui.print_success("Cart cleared!")
    else:
        ui.console.print("[yellow]Cancelled[/yellow]")

@cart_app.command("checkout")
def checkout():
    """Checkout and place order from cart."""
    checkout_cart()

def checkout_cart():
    """Internal checkout function."""
    if not cart:
        ui.print_error("Cart is empty! Add items first.")
        return
    
    view_cart_internal()
    
    confirm = questionary.confirm(
        "\nProceed with checkout?",
        style=custom_style,
        default=True
    ).ask()
    
    if not confirm:
        ui.console.print("[yellow]Checkout cancelled[/yellow]")
        return
    
    # Convert cart to API format
    items = {str(item_id): qty for item_id, qty in cart.items()}
    resp, code = api.create_order(items)
    
    if code == 201:
        ui.print_success(f"Order #{resp['id']} placed successfully!")
        ui.console.print(f"[green]Total: ${resp['total_price']}[/green]")
        cart.clear()
    else:
        ui.print_error(f"Failed to place order: {resp}")

# ==================== ORDER COMMANDS ====================

@app.command(name="orders")
def list_orders():
    """List my orders."""
    data = api.get_orders()
    if data:
        ui.display_orders(data)
    else:
        ui.print_error("No orders found or you need to login.")

@app.command()
def order(item_id: int = typer.Option(..., help="Menu Item ID"), 
          qty: int = typer.Option(1, help="Quantity")):
    """Place a quick order for a single item (bypasses cart)."""
    items = {str(item_id): qty}
    resp, code = api.create_order(items)
    if code == 201:
        ui.print_success(f"Order #{resp['id']} placed! Total: ${resp['total_price']}")
    else:
        ui.print_error(f"Failed to place order: {resp}")

@app.command()
def cancel(order_id: Optional[int] = None):
    """Cancel a pending order."""
    if not order_id:
        # Interactive mode
        orders = api.get_orders()
        pending_orders = [o for o in orders if o['status'] == 'Pending']
        
        if not pending_orders:
            ui.print_error("No pending orders to cancel")
            return
        
        order_choices = [
            f"Order #{o['id']} - {o['restaurant_name']} (${o['total_price']})"
            for o in pending_orders
        ]
        
        selected = questionary.select(
            "Select order to cancel:",
            choices=order_choices,
            style=custom_style
        ).ask()
        
        if not selected:
            return
        
        order_id = int(selected.split("#")[1].split(" ")[0])
    
    confirm = questionary.confirm(
        f"Cancel order #{order_id}?",
        style=custom_style,
        default=False
    ).ask()
    
    if confirm:
        if api.cancel_order(order_id):
            ui.print_success(f"Order #{order_id} cancelled.")
        else:
            ui.print_error("Failed to cancel order (Is it pending?)")
    else:
        ui.console.print("[yellow]Cancellation aborted[/yellow]")

# ==================== DRIVER COMMANDS ====================

driver_app = typer.Typer(help="Driver-specific commands")
app.add_typer(driver_app, name="driver")

@driver_app.command("jobs")
def available_jobs():
    """(Driver) List available delivery jobs."""
    jobs = api.get_available_jobs()
    if jobs:
        ui.display_available_jobs(jobs)
    else:
        ui.console.print("[yellow]No available jobs at the moment[/yellow]")

@driver_app.command("accept")
def accept_job(order_id: Optional[int] = None):
    """(Driver) Accept a delivery job."""
    if not order_id:
        # Interactive mode
        jobs = api.get_available_jobs()
        if not jobs:
            ui.print_error("No available jobs")
            return
        
        job_choices = [
            f"Order #{j['id']} - {j['restaurant_name']} (${j['total_price']})"
            for j in jobs
        ]
        
        selected = questionary.select(
            "Select job to accept:",
            choices=job_choices,
            style=custom_style
        ).ask()
        
        if not selected:
            return
        
        order_id = int(selected.split("#")[1].split(" ")[0])
    
    if api.accept_job(order_id):
        ui.print_success(f"Job #{order_id} accepted!")
    else:
        ui.print_error("Failed to accept job.")

@driver_app.command("complete")
def complete_job(order_id: Optional[int] = None):
    """(Driver) Mark a job as complete."""
    if not order_id:
        # Interactive mode - show driver's accepted jobs
        orders = api.get_orders()
        active_jobs = [o for o in orders if o['status'] in ['Confirmed', 'Delivering']]
        
        if not active_jobs:
            ui.print_error("No active jobs to complete")
            return
        
        job_choices = [
            f"Order #{o['id']} - {o['restaurant_name']} (${o['status']})"
            for o in active_jobs
        ]
        
        selected = questionary.select(
            "Select job to complete:",
            choices=job_choices,
            style=custom_style
        ).ask()
        
        if not selected:
            return
        
        order_id = int(selected.split("#")[1].split(" ")[0])
    
    confirm = questionary.confirm(
        f"Mark order #{order_id} as delivered?",
        style=custom_style,
        default=True
    ).ask()
    
    if confirm:
        if api.complete_job(order_id):
            ui.print_success(f"Job #{order_id} completed!")
        else:
            ui.print_error("Failed to complete job.")
    else:
        ui.console.print("[yellow]Cancelled[/yellow]")

class Command(BaseCommand):
    help = 'Runs the interactive CLI'

    def handle(self, *args, **options):
        # Call the interactive main menu
        main()
