from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import os

console = Console()

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_welcome():
    console.print(Panel.fit("[bold magenta]Welcome to Mostafa CLI[/bold magenta]", border_style="green"))

def print_error(msg):
    console.print(f"[bold red]Error:[/bold red] {msg}")

def print_success(msg):
    console.print(f"[bold green]Success:[/bold green] {msg}")

def display_profile(profile):
    """Display user profile information."""
    user = profile.get('user', {})
    username = user.get('username', 'Unknown')
    email = user.get('email', 'N/A')
    role = profile.get('role', 'Unknown')
    
    table = Table(title="Your Profile", box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="cyan bold")
    table.add_column("Value", style="white")
    
    table.add_row("Username", username)
    table.add_row("Email", email)
    table.add_row("Role", role)
    table.add_row("Phone", profile.get('phone_number', 'N/A'))
    
    if role == "Customer":
        table.add_row("Address", profile.get('address', 'N/A'))
    elif role == "Driver":
        table.add_row("License", profile.get('license_number', 'N/A'))
        table.add_row("Vehicle Plate", profile.get('vehicle_plate', 'N/A'))
        table.add_row("Vehicle Type", profile.get('vehicle_type', 'N/A'))
        table.add_row("Bank Account", profile.get('bank_account', 'N/A'))
    
    console.print(table)

def display_cart(cart, all_items):
    """Display shopping cart contents."""
    table = Table(title="Shopping Cart", box=box.ROUNDED)
    table.add_column("Item ID", style="cyan", no_wrap=True)
    table.add_column("Item Name", style="yellow")
    table.add_column("Restaurant", style="blue")
    table.add_column("Price", style="green", justify="right")
    table.add_column("Quantity", style="magenta", justify="center")
    table.add_column("Subtotal", style="green bold", justify="right")
    
    total = 0
    for item_id, qty in cart.items():
        item_info = all_items.get(item_id)
        if item_info:
            price = float(item_info['price'])
            subtotal = price * qty
            total += subtotal
            
            table.add_row(
                str(item_id),
                item_info['name'],
                item_info['restaurant'],
                f"${price:.2f}",
                str(qty),
                f"${subtotal:.2f}"
            )
        else:
            table.add_row(str(item_id), "Unknown Item", "N/A", "N/A", str(qty), "N/A")
    
    console.print(table)
    console.print(f"\n[bold green]Total: ${total:.2f}[/bold green]\n")

def display_restaurants(restaurants):
    table = Table(title="Available Restaurants", box=box.ROUNDED)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Cuisine", style="green")
    table.add_column("Description", style="white")

    for r in restaurants:
        table.add_row(str(r['id']), r['name'], r['cuisine'], r['description'])
    
    console.print(table)

def display_menu(restaurant_name, menu_items):
    table = Table(title=f"Menu for {restaurant_name}", box=box.SIMPLE)
    table.add_column("ID", style="cyan")
    table.add_column("Item", style="yellow")
    table.add_column("Price", style="green")
    table.add_column("Description")

    for item in menu_items:
        table.add_row(str(item['id']), item['name'], f"${item['price']}", item['description'])
    
    console.print(table)

def display_orders(orders):
    table = Table(title="Your Orders", box=box.MINIMAL)
    table.add_column("ID", style="cyan")
    table.add_column("Restaurant", style="blue")
    table.add_column("Status", style="bold")
    table.add_column("Total", style="green")
    table.add_column("Date", style="dim")

    for o in orders:
        status_style = "green" if o['status'] == 'Delivered' else "yellow" if o['status'] == 'Delivering' else "white"
        if o['status'] == 'Cancelled': status_style = "red"
        
        table.add_row(
            str(o['id']), 
            o['restaurant_name'], 
            f"[{status_style}]{o['status']}[/{status_style}]", 
            f"${o['total_price']}", 
            o['created_at'][:10]
        )
    console.print(table)

def display_available_jobs(orders):
    table = Table(title="Available Deliveries", box=box.HEAVY)
    table.add_column("ID", style="cyan")
    table.add_column("Store", style="blue")
    table.add_column("Earnings", style="green")
    table.add_column("Date", style="dim")

    for o in orders:
        table.add_row(str(o['id']), o['restaurant_name'], f"${o['total_price']}", o['created_at'][:10])
    console.print(table)
