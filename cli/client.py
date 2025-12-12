import typer
from .api import ApiService
from . import ui

app = typer.Typer()
api = ApiService()

@app.command()
def login(username: str = typer.Option(..., prompt=True), password: str = typer.Option(..., prompt=True, hide_input=True)):
    """Log in to the system."""
    success, msg = api.login(username, password)
    if success:
        ui.print_success(msg)
    else:
        ui.print_error(msg)

@app.command()
def register(username: str = typer.Option(..., prompt=True), email: str = typer.Option(..., prompt=True), password: str = typer.Option(..., prompt=True, hide_input=True)):
    """Register a new user."""
    success, msg = api.register(username, password, email)
    if success:
        ui.print_success(msg)
    else:
        ui.print_error(msg)

@app.command()
def tui():
    """Start interactive Text User Interface."""
    from .tui_app import FoodDeliveryApp
    app = FoodDeliveryApp()
    app.run()

@app.command()
def logout():
    """Clear local session."""
    import os
    if os.path.exists(".token_cache"):
        os.remove(".token_cache")
        ui.print_success("Logged out.")

@app.command()
def me():
    """View my profile."""
    profile = api.get_my_profile()
    if profile:
        ui.console.print(profile)
    else:
        ui.print_error("Could not fetch profile (Are you logged in?)")

# RESTAURANT COMMANDS
@app.command(name="restaurants")
def list_restaurants():
    """List all available restaurants."""
    data = api.get_restaurants()
    ui.display_restaurants(data)

@app.command(name="menu")
def view_menu(restaurant_id: int):
    """View menu for a specific restaurant."""
    restaurants = api.get_restaurants()
    # Find restaurant name locally or fetch detail (simplified here)
    r_name = next((r['name'] for r in restaurants if r['id'] == restaurant_id), "Restaurant")
    
    # We cheat a bit: get_restaurants returns full structure including menu_items in our serializer
    # Ideally should use a detail endpoint, but the list serializer has it.
    target_r = next((r for r in restaurants if r['id'] == restaurant_id), None)
    if target_r:
        ui.display_menu(r_name, target_r['menu_items'])
    else:
        ui.print_error("Restaurant not found")

# ORDER COMMANDS
@app.command(name="orders")
def list_orders():
    """List my orders."""
    data = api.get_orders()
    ui.display_orders(data)

@app.command()
def order(item_id: int = typer.Option(..., help="Menu Item ID"), qty: int = typer.Option(1, help="Quantity")):
    """Place a quick order for a single item."""
    items = {str(item_id): qty}
    resp, code = api.create_order(items)
    if code == 201:
        ui.print_success(f"Order #{resp['id']} placed! Total: ${resp['total_price']}")
    else:
        ui.print_error(f"Failed to place order: {resp}")

@app.command()
def cancel(order_id: int):
    """Cancel a pending order."""
    if api.cancel_order(order_id):
        ui.print_success(f"Order #{order_id} cancelled.")
    else:
        ui.print_error("Failed to cancel order (Is it pending?)")

# DRIVER COMMANDS
driver_app = typer.Typer()
app.add_typer(driver_app, name="driver")

@driver_app.command("jobs")
def available_jobs():
    """(Driver) List available jobs."""
    jobs = api.get_available_jobs()
    ui.display_available_jobs(jobs)

@driver_app.command("accept")
def accept_job(order_id: int):
    """(Driver) Accept a job."""
    if api.accept_job(order_id):
        ui.print_success(f"Job #{order_id} accepted!")
    else:
        ui.print_error("Failed to accept job.")

@driver_app.command("complete")
def complete_job(order_id: int):
    """(Driver) Mark a job as complete."""
    if api.complete_job(order_id):
        ui.print_success(f"Job #{order_id} completed!")
    else:
        ui.print_error("Failed to complete job.")

if __name__ == "__main__":
    app()
