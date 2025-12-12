from textual.app import App, ComposeResult
from textual.containers import Grid, Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, Label, Input, DataTable
from textual.screen import Screen
from textual import on
from .api import ApiService

api = ApiService()

class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Please Log In", id="page_title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Button("Log In", variant="primary", id="login_btn"),
            Button("Back to Main Menu", variant="default", id="back_btn"),
            id="login_dialog"
        )

    @on(Button.Pressed, "#login_btn")
    def login(self):
        user = self.query_one("#username").value
        pw = self.query_one("#password").value
        success, msg = api.login(user, pw)
        if success:
            self.app.notify("Login Successful!")
            self.app.pop_screen()
        else:
            self.app.notify(f"Error: {msg}", severity="error")

    @on(Button.Pressed, "#back_btn")
    def back(self):
        self.app.pop_screen()

from textual.widgets import Header, Footer, Button, Static, Label, Input, DataTable, RadioButton, RadioSet

class RegisterScreen(Screen):
    CSS = """
    #driver_fields {
        display: none;
    }
    .driver-mode #driver_fields {
        display: block;
    }
    """
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Create Account", id="page_title"),
            Input(placeholder="Username", id="r_username"),
            Input(placeholder="Email", id="r_email"),
            Input(placeholder="Password", password=True, id="r_password"),
            Input(placeholder="Phone Number", id="r_phone"),
            
            Label("Select Role:"),
            RadioSet(
                RadioButton("Customer", value=True, id="role_customer"),
                RadioButton("Driver", id="role_driver"),
                id="role_selector"
            ),
            
            # Customer/Common Fields
            Input(placeholder="Address (for Customers)", id="r_address"),
            
            # Driver Fields
            Container(
                Input(placeholder="License Number", id="r_license"),
                Input(placeholder="Vehicle Plate", id="r_plate"),
                Input(placeholder="Vehicle Type (Car/Bike)", id="r_vehicle"),
                Input(placeholder="Bank Account", id="r_bank"),
                id="driver_fields"
            ),
            
            Button("Register", variant="primary", id="register_btn"),
            Button("Back", variant="default", id="back_btn"),
            id="register_dialog"
        )
    
    @on(RadioSet.Changed, "#role_selector")
    def on_role_change(self, event: RadioSet.Changed):
        # Textual 0.38+ style. 
        # Logic: if driver selected, add class 'driver-mode' to container? 
        # finding the container might be tricky.
        # Simpler: Toggle display style directly?
        driver_fields = self.query_one("#driver_fields")
        if event.pressed.id == "role_driver":
            driver_fields.styles.display = "block"
        else:
            driver_fields.styles.display = "none"

    @on(Button.Pressed, "#register_btn")
    def register(self):
        u = self.query_one("#r_username").value
        e = self.query_one("#r_email").value
        p = self.query_one("#r_password").value
        ph = self.query_one("#r_phone").value
        
        roles = self.query_one("#role_selector")
        role = "Driver" if roles.pressed_button.id == "role_driver" else "Customer"
        
        data = {
           "username": u, "email": e, "password": p, "phone_number": ph, "role": role
        }
        
        if role == "Customer":
            data["address"] = self.query_one("#r_address").value
        else:
            data["license_number"] = self.query_one("#r_license").value
            data["vehicle_plate"] = self.query_one("#r_plate").value
            data["vehicle_type"] = self.query_one("#r_vehicle").value
            data["bank_account"] = self.query_one("#r_bank").value

        success, msg = api.register(data)
        if success:
            self.app.notify("Registered & Logged In!")
            self.app.update_user_display()
            self.app.pop_screen()
        else:
            self.app.notify(msg, severity="error")

    @on(Button.Pressed, "#back_btn")
    def back(self):
        self.app.pop_screen()

class RestaurantScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            DataTable(id="resto_table"),
            Horizontal(
                 Button("Back", id="back_btn"),
                 Button("View Menu", variant="primary", id="view_menu_btn"),
            )
        )

    def on_mount(self):
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Name", "Cuisine", "Description")
        self.load_data()

    def load_data(self):
         data = api.get_restaurants()
         if not data or not isinstance(data, list): return 
         table = self.query_one(DataTable)
         table.clear()
         for r in data:
             table.add_row(r['id'], r['name'], r['cuisine'], r['description'], key=str(r['id']))

    @on(Button.Pressed, "#back_btn")
    def back(self):
        self.app.pop_screen()

    @on(Button.Pressed, "#view_menu_btn")
    def view_menu(self):
        table = self.query_one(DataTable)
        if not table.cursor_row and table.cursor_row != 0:
             return
        # Get Key
        try:
             row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
             self.app.push_screen(MenuScreen(restaurant_id=row_key.value))
        except:
             pass

class MenuScreen(Screen):
    def __init__(self, restaurant_id):
        super().__init__()
        self.restaurant_id = int(restaurant_id)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Menu", id="page_title")
        yield DataTable(id="menu_table")
        yield Horizontal(
            Button("Back", id="back_btn"),
            Button("Order Selected", variant="success", id="order_btn")
        )

    def on_mount(self):
        # Fetch data
        all_restopro = api.get_restaurants()
        r = next((x for x in all_restopro if x['id'] == self.restaurant_id), None)
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Item", "Price", "Description")
        
        if r:
            for item in r['menu_items']:
                table.add_row(item['id'], item['name'], f"${item['price']}", item['description'], key=str(item['id']))

    @on(Button.Pressed, "#back_btn")
    def back(self):
        self.app.pop_screen()

    @on(Button.Pressed, "#order_btn")
    def order(self):
        table = self.query_one(DataTable)
        try:
            item_id = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
            items = {str(item_id): 1}
            resp, code = api.create_order(items)
            if code == 201:
                self.app.notify(f"Order Placed! Total: ${resp['total_price']}")
            else:
                self.app.notify("Failed to place order", severity="error")
        except:
            self.app.notify("Select an item first", severity="warning")

class OrdersScreen(Screen):
    def compose(self) -> ComposeResult:
         yield Header()
         yield DataTable(id="orders_table")
         yield Button("Back", id="back_btn")

    def on_mount(self):
        table = self.query_one(DataTable)
        table.add_columns("ID", "Restaurant", "Status", "Total")
        data = api.get_orders()
        for o in data:
            table.add_row(o['id'], o['restaurant_name'], o['status'], f"${o['total_price']}")

    @on(Button.Pressed, "#back_btn")
    def back(self):
        self.app.pop_screen()


class FoodDeliveryApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    #main_menu {
        grid-size: 2 3;
        grid-gutter: 1 2;
        grid-rows: 1fr;
        grid-columns: 1fr;
        width: 60%;
        height: 60%;
        border: solid green;
    }
    #main_menu Button {
        width: 100%;
        height: 100%;
    }
    #page_title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }
    #login_dialog, #register_dialog {
        width: 80;
        height: auto;
        border: solid cyan;
        padding: 2;
        overflow-y: scroll;
    }
    Input {
        margin-bottom: 1;
    }
    #user_display {
        background: $primary;
        color: white;
        dock: top;
        padding: 1;
        text-align: right;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("", id="user_display")
        yield Container(
            Label("Welcome to Food Delivery CLI", id="page_title"),
            Grid(
                Button("Login", id="btn_login", variant="primary"),
                Button("Register", id="btn_register", variant="warning"),
                Button("Restaurants", id="btn_restaurants", variant="success"),
                Button("My Orders", id="btn_orders", variant="primary"),
                Button("Driver Dash", id="btn_driver", variant="error"),
                Button("Exit", id="btn_exit"),
                id="main_menu"
            )
        )
        yield Footer()
        
    def on_mount(self):
        self.update_user_display()

    def update_user_display(self):
        profile = api.get_my_profile()
        lbl = self.query_one("#user_display")
        if profile:
            # Profile has nested user: {user: {username: ...}, role: ...}
            uname = profile.get('user', {}).get('username', 'User')
            role = profile.get('role', 'Unknown')
            lbl.update(f"Logged in as: {uname} ({role})")
        else:
            lbl.update("Not Logged In")

    @on(Button.Pressed, "#btn_login")
    def open_login(self):
        self.push_screen(LoginScreen())

    @on(Button.Pressed, "#btn_register")
    def open_register(self):
        self.push_screen(RegisterScreen())

    @on(Button.Pressed, "#btn_restaurants")
    def open_restaurants(self):
        self.push_screen(RestaurantScreen())

    @on(Button.Pressed, "#btn_orders")
    def open_orders(self):
        self.push_screen(OrdersScreen())

    @on(Button.Pressed, "#btn_exit")
    def exit_app(self):
        self.exit()
