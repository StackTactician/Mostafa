from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def print_welcome():
    console.print(Panel.fit("[bold magenta]Welcome to Food Delivery CLI[/bold magenta]", border_style="green"))

def print_error(msg):
    console.print(f"[bold red]Error:[/bold red] {msg}")

def print_success(msg):
    console.print(f"[bold green]Success:[/bold green] {msg}")

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
