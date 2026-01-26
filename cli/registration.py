import questionary
from questionary import Style, Validator, ValidationError
from cli.api import ApiService
from cli import ui
import re

# Get instances from main cli module
api = ApiService()

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

# Validators
class EmailValidator(Validator):
    def validate(self, document):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, document.text):
            raise ValidationError(
                message='Please enter a valid email address (e.g., user@example.com)',
                cursor_position=len(document.text)
            )

class UsernameValidator(Validator):
    def validate(self, document):
        if len(document.text) < 3:
            raise ValidationError(
                message='Username must be at least 3 characters long',
                cursor_position=len(document.text)
            )
        if not re.match(r'^[a-zA-Z0-9_]+$', document.text):
            raise ValidationError(
                message='Username can only contain letters, numbers, and underscores',
                cursor_position=len(document.text)
            )

class PasswordValidator(Validator):
    def validate(self, document):
        if len(document.text) < 4:
            raise ValidationError(
                message='Password must be at least 4 characters long',
                cursor_position=len(document.text)
            )

class PhoneValidator(Validator):
    def validate(self, document):
        # Allow various phone formats: +1234567890, 123-456-7890, (123) 456-7890, etc.
        phone_pattern = r'^[\d\s\-\+\(\)]+$'
        if not re.match(phone_pattern, document.text):
            raise ValidationError(
                message='Please enter a valid phone number (digits, spaces, +, -, () allowed)',
                cursor_position=len(document.text)
            )
        # Check minimum length (at least 7 digits)
        digits_only = re.sub(r'\D', '', document.text)
        if len(digits_only) < 7:
            raise ValidationError(
                message='Phone number must contain at least 7 digits',
                cursor_position=len(document.text)
            )

class NonEmptyValidator(Validator):
    def __init__(self, field_name):
        self.field_name = field_name
    
    def validate(self, document):
        if not document.text.strip():
            raise ValidationError(
                message=f'{self.field_name} cannot be empty',
                cursor_position=0
            )


def register_interactive():
    """Interactive registration with navigation and editing capabilities."""
    ui.clear_screen()
    ui.console.print("\n[bold cyan]📝 Create New Account[/bold cyan]\n")
    
    # Registration data
    data = {
        "username": "",
        "email": "",
        "password": "",
        "phone_number": "",
        "role": "",
        "address": "",
        "license_number": "",
        "vehicle_plate": "",
        "vehicle_type": "",
        "bank_account": ""
    }
    
    # Step 1: Basic Information
    while True:
        ui.console.print("\n[bold yellow]Step 1/3: Basic Information[/bold yellow]")
        if data["username"]:
            ui.console.print(f"[dim]Current: {data['username']} | {data['email']} | {data['phone_number']}[/dim]\n")
        
        username = questionary.text(
            "Username:",
            default=data["username"],
            style=custom_style,
            validate=UsernameValidator()
        ).ask()
        
        if username is None:
            if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue
        
        email = questionary.text(
            "Email:",
            default=data["email"],
            style=custom_style,
            validate=EmailValidator()
        ).ask()
        
        if email is None:
            if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue
        
        # OTP Verification
        ui.console.print("\n[cyan]📧 Sending verification code to your email...[/cyan]")
        success, msg = api.send_otp(email)
        
        if not success:
            ui.print_error(f"Failed to send OTP: {msg}")
            retry = questionary.confirm("Try again with a different email?", style=custom_style, default=True).ask()
            if not retry:
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue
        
        ui.print_success(f"OTP sent to {email}")
        ui.console.print("[dim]Check your email (or Django console in development) for the code[/dim]\n")
        
        # OTP verification loop (3 attempts)
        otp_verified = False
        for attempt in range(3):
            otp_code = questionary.text(
                f"Enter 6-digit OTP code (Attempt {attempt + 1}/3):",
                style=custom_style
            ).ask()
            
            if otp_code is None:
                if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                    ui.console.print("[yellow]Registration cancelled[/yellow]")
                    return
                continue
            
            # Verify OTP
            verified, verify_msg = api.verify_otp(email, otp_code)
            
            if verified:
                ui.print_success("✅ Email verified!")
                otp_verified = True
                break
            else:
                ui.print_error(verify_msg)
                
                if attempt < 2:  # Not last attempt
                    action = questionary.select(
                        "What would you like to do?",
                        choices=[
                            "🔄 Try again",
                            "📧 Resend OTP",
                            "✏️  Change email",
                            "❌ Cancel"
                        ],
                        style=custom_style
                    ).ask()
                    
                    if action == "📧 Resend OTP":
                        ui.console.print("[cyan]Resending OTP...[/cyan]")
                        success, msg = api.send_otp(email)
                        if success:
                            ui.print_success("OTP resent!")
                        else:
                            ui.print_error(f"Failed to resend: {msg}")
                    elif action == "✏️  Change email":
                        break  # Go back to email input
                    elif action == "❌ Cancel":
                        ui.console.print("[yellow]Registration cancelled[/yellow]")
                        return
        
        if not otp_verified:
            ui.print_error("Too many failed attempts or verification cancelled")
            retry = questionary.confirm("Start over with a different email?", style=custom_style, default=True).ask()
            if not retry:
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue  # Go back to email input
        
        password = questionary.password(
            "Password:",
            style=custom_style,
            validate=PasswordValidator()
        ).ask()
        
        if password is None:
            if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue
        
        phone = questionary.text(
            "Phone Number:",
            default=data["phone_number"],
            style=custom_style,
            validate=PhoneValidator()
        ).ask()
        
        if phone is None:
            if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue
        
        data["username"] = username
        data["email"] = email
        if password:
            data["password"] = password
        data["phone_number"] = phone
        
        action = questionary.select(
            "\nWhat would you like to do?",
            choices=[
                "➡️  Continue to Role Selection",
                "✏️  Re-enter Basic Information",
                "❌ Cancel Registration"
            ],
            style=custom_style
        ).ask()
        
        if action == "➡️  Continue to Role Selection":
            break
        elif action == "❌ Cancel Registration":
            ui.console.print("[yellow]Registration cancelled[/yellow]")
            return
    
    # Step 2: Role Selection
    while True:
        ui.console.print("\n[bold yellow]Step 2/3: Role Selection[/bold yellow]")
        if data["role"]:
            ui.console.print(f"[dim]Current role: {data['role']}[/dim]\n")
        
        role = questionary.select(
            "Select your role:",
            choices=["Customer", "Driver"],
            default=data["role"] if data["role"] else "Customer",
            style=custom_style
        ).ask()
        
        if role is None:
            if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                ui.console.print("[yellow]Registration cancelled[/yellow]")
                return
            continue
        
        data["role"] = role
        
        action = questionary.select(
            "\nWhat would you like to do?",
            choices=[
                "➡️  Continue to Additional Information",
                "⬅️  Go Back to Basic Information",
                "❌ Cancel Registration"
            ],
            style=custom_style
        ).ask()
        
        if action == "➡️  Continue to Additional Information":
            break
        elif action == "⬅️  Go Back to Basic Information":
            # Go back to Step 1 (outer while loop continues)
            break
        elif action == "❌ Cancel Registration":
            ui.console.print("[yellow]Registration cancelled[/yellow]")
            return
    
    if action == "⬅️  Go Back to Basic Information":
        return register_interactive()  # Restart from beginning
    
    # Step 3: Role-Specific Information
    while True:
        if data["role"] == "Customer":
            ui.console.print("\n[bold yellow]Step 3/3: Customer Information[/bold yellow]")
            if data["address"]:
                ui.console.print(f"[dim]Current address: {data['address']}[/dim]\n")
            
            address = questionary.text(
                "Delivery Address (optional):",
                default=data["address"],
                style=custom_style
            ).ask()
            
            if address is None:
                if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                    ui.console.print("[yellow]Registration cancelled[/yellow]")
                    return
                continue
            
            data["address"] = address
            
        else:  # Driver
            ui.console.print("\n[bold yellow]Step 3/3: Driver Information[/bold yellow]")
            if data["license_number"]:
                ui.console.print(f"[dim]License: {data['license_number']} | Plate: {data['vehicle_plate']} | Type: {data['vehicle_type']}[/dim]\n")
            
            license_num = questionary.text(
                "License Number:",
                default=data["license_number"],
                style=custom_style,
                validate=NonEmptyValidator("License number")
            ).ask()
            
            if license_num is None:
                if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                    ui.console.print("[yellow]Registration cancelled[/yellow]")
                    return
                continue
            
            vehicle_plate = questionary.text(
                "Vehicle Plate:",
                default=data["vehicle_plate"],
                style=custom_style,
                validate=NonEmptyValidator("Vehicle plate")
            ).ask()
            
            if vehicle_plate is None:
                if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                    ui.console.print("[yellow]Registration cancelled[/yellow]")
                    return
                continue
            
            vehicle_type = questionary.select(
                "Vehicle Type:",
                choices=["Car", "Bike", "Scooter"],
                default=data["vehicle_type"] if data["vehicle_type"] else "Car",
                style=custom_style
            ).ask()
            
            if vehicle_type is None:
                if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                    ui.console.print("[yellow]Registration cancelled[/yellow]")
                    return
                continue
            
            bank_account = questionary.text(
                "Bank Account:",
                default=data["bank_account"],
                style=custom_style,
                validate=NonEmptyValidator("Bank account")
            ).ask()
            
            if bank_account is None:
                if questionary.confirm("❌ Cancel registration?", style=custom_style, default=False).ask():
                    ui.console.print("[yellow]Registration cancelled[/yellow]")
                    return
                continue
            
            data["license_number"] = license_num
            data["vehicle_plate"] = vehicle_plate
            data["vehicle_type"] = vehicle_type
            data["bank_account"] = bank_account
        
        # Review
        ui.console.print("\n[bold green]📋 Review Your Information[/bold green]")
        ui.console.print(f"[cyan]Username:[/cyan] {data['username']}")
        ui.console.print(f"[cyan]Email:[/cyan] {data['email']}")
        ui.console.print(f"[cyan]Phone:[/cyan] {data['phone_number']}")
        ui.console.print(f"[cyan]Role:[/cyan] {data['role']}")
        
        if data["role"] == "Customer":
            ui.console.print(f"[cyan]Address:[/cyan] {data['address'] or 'Not provided'}")
        else:
            ui.console.print(f"[cyan]License:[/cyan] {data['license_number']}")
            ui.console.print(f"[cyan]Vehicle Plate:[/cyan] {data['vehicle_plate']}")
            ui.console.print(f"[cyan]Vehicle Type:[/cyan] {data['vehicle_type']}")
            ui.console.print(f"[cyan]Bank Account:[/cyan] {data['bank_account']}")
        
        action = questionary.select(
            "\nWhat would you like to do?",
            choices=[
                "✅ Submit Registration",
                "✏️  Edit This Information",
                "⬅️  Go Back to Role Selection",
                "❌ Cancel Registration"
            ],
            style=custom_style
        ).ask()
        
        if action == "✅ Submit Registration":
            break
        elif action == "✏️  Edit This Information":
            continue
        elif action == "⬅️  Go Back to Role Selection":
            return register_interactive()
        elif action == "❌ Cancel Registration":
            ui.console.print("[yellow]Registration cancelled[/yellow]")
            return
    
    # Prepare and submit
    final_data = {
        "username": data["username"],
        "email": data["email"],
        "password": data["password"],
        "phone_number": data["phone_number"],
        "role": data["role"]
    }
    
    if data["role"] == "Customer":
        if data["address"]:
            final_data["address"] = data["address"]
    else:
        if data["license_number"]:
            final_data["license_number"] = data["license_number"]
        if data["vehicle_plate"]:
            final_data["vehicle_plate"] = data["vehicle_plate"]
        if data["vehicle_type"]:
            final_data["vehicle_type"] = data["vehicle_type"]
        if data["bank_account"]:
            final_data["bank_account"] = data["bank_account"]
    
    ui.console.print("\n[cyan]⏳ Submitting registration...[/cyan]")
    success, msg = api.register(final_data)
    if success:
        ui.print_success("Registration successful! You are now logged in.")
    else:
        ui.print_error(msg)
