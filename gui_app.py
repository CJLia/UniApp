"""
Main application file for the Graphical User Interface (GUI).

This file is the entry point for running the application. It is
responsible for setting up the Dependency Injection (DI) container
by instantiating all services and controllers, wiring them together,
and starting the main GUI loop.
"""

import sys
import os
import tkinter as tk
import hashlib # For admin password hashing

# --- Fix Python Path for imports ---
# This ensures Python can find modules inside the 'src' directory.
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Import Services and Models ---
# The explicit imports are necessary for DI and type checking.
from src.services.data_store import FileDataStore # Data persistence
from src.services.grade_policy import DefaultGradePolicy # Grading logic
from src.services.auth_service import AuthService # Authentication logic
from src.services.enrolment_service import EnrolmentService # Student subject logic
from src.services.reporting_service import ReportingService # Admin reports logic
from src.utils.id_generator import IdGenerator # ID generation
from src.models.admin import Admin # Admin model for creation logic

# --- Import Controllers ---
from src.controllers.auth_controllers import AuthController
from src.controllers.enrolment_controller import EnrolmentController
from src.controllers.admin_controller import AdminController
from src.controllers.reporting_controller import ReportingController

# --- Import View ---
# This file is expected to be located at src/views/gui_view.py
from src.views.gui_views import GUIView 

# --- Constants ---
# Define the path to your data file
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DATA_FILE_PATH = os.path.join(DATA_DIR, 'university_data.dat')

# Ensure the "data" directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Admin Setup Constants ---
ADMIN_ID = "admin001"
ADMIN_PASSWORD = "AdminPassword123" 
ADMIN_EMAIL = "admin@uniapp.com"

# ===================================================================
# --- Admin Initialization Logic ---
# ===================================================================

def _hash_password(password):
    """Hashes a plain-text password using SHA-256 (duplicated from AuthService)."""
    salt = "cli_uni_app_salt"
    salted_password = (password + salt).encode('utf-8')
    return hashlib.sha256(salted_password).hexdigest()

def ensure_base_admin_exists(data_store):
    """
    Checks if the default admin exists and creates it if not.
    This ensures the application is usable immediately.
    """
    all_users = data_store.get_all_users()
    
    # Check if the admin ID is already present
    admin_exists = any(user.id == ADMIN_ID for user in all_users)

    if not admin_exists:
        try:
            # 1. Generate the hash for the default password
            password_hash = _hash_password(ADMIN_PASSWORD)

            # 2. Create the Admin model object
            new_admin = Admin(
                id=ADMIN_ID,
                name="System Administrator",
                email=ADMIN_EMAIL,
                password_hash=password_hash
            )
            
            # 3. Add the user to the store and save the data file
            data_store.add_user(new_admin)

            print("==================================================")
            print(f"INFO: Created base admin user: ID='{ADMIN_ID}', Password='{ADMIN_PASSWORD}'")
            print("==================================================")
            
        except Exception as e:
            # Catch errors in the data persistence layer
            print("==================================================")
            print(f"FATAL ERROR: Could not create base admin user: {e}")
            print("==================================================")


# ===================================================================
# --- Application Startup ---
# ===================================================================

def main():
    """Main function to configure and run the application."""
    
    # 1. Initialize Services (DI)
    try:
        data_store = FileDataStore(DATA_FILE_PATH)
        grade_policy = DefaultGradePolicy()
        
        # IdGenerator requires the data store
        id_generator = IdGenerator(data_store) 
        
        # Authentication Service requires the data store and ID generator
        auth_service = AuthService(data_store, id_generator)
        
        # Enrolment Service requires the data store, grade policy, and ID generator
        enrolment_service = EnrolmentService(data_store, grade_policy, id_generator)
        
        # Reporting Service requires the data store
        reporting_service = ReportingService(data_store, grade_policy)
        
    except Exception as e:
        # Handle exceptions during service initialization (e.g., corrupted data file)
        print("Failed to initialize services:")
        print(e)
        return

    # 2. Ensure the base admin account exists
    ensure_base_admin_exists(data_store)

    # 3. Initialize Controllers
    auth_controller = AuthController(auth_service)
    enrolment_controller = EnrolmentController(enrolment_service)
    admin_controller = AdminController(data_store, reporting_service)
    reporting_controller = ReportingController(reporting_service)

    # 4. Initialize and Run GUI
    root = tk.Tk()
    
    # Pass controllers to the view
    app = GUIView(
        root,
        auth_controller,
        enrolment_controller,
        admin_controller,
        reporting_controller
    )
    
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()