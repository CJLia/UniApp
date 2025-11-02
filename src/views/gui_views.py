"""
Defines the main GUI (Graphical User Interface) view for the application.

This file contains the 'GUIView' class, which is responsible for
building and managing all the visual components (windows, buttons,
labels, etc.) using the 'tkinter' library.

It does NOT contain any business logic. It only:
1.  Displays information.
2.  Takes user input.
3.  Calls the appropriate controller method when a user acts.
4.  Receives a result from the controller and displays it.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Import the models to check the type of the logged-in user
# This relies on 'src/models/user.py' being named correctly
from src.models.student import Student
from src.models.admin import Admin

class GUIView:
    """
    Manages all GUI frames and logic.
    
    This class holds the Tkinter root and references to all controllers.
    It's responsible for switching frames (e.g., from login to menu).
    """

    def __init__(self, root, auth_controller, enrolment_controller, admin_controller, reporting_controller):
        """
        Initializes the GUIView.

        Args:
            root (tk.Tk): The main Tkinter root window.
            auth_controller: The controller for auth logic.
            enrolment_controller: The controller for student logic.
            admin_controller: The controller for admin logic.
            reporting_controller: The controller for reporting logic.
        """
        self.root = root
        self.auth_controller = auth_controller
        self.enrolment_controller = enrolment_controller
        self.admin_controller = admin_controller
        self.reporting_controller = reporting_controller

        # --- State ---
        self.current_user = None  # Stores the logged-in user object
        self._current_frame = None # The active frame (e.g., login, menu)

        # --- Setup ---
        self.root.title("University Enrolment System")
        self.root.geometry("800x600") # Set a default size
        self.root.minsize(500, 400)  # Set a minimum size

        # Configure the main window to expand its content
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Start by showing the login screen
        self.show_login_frame()

    def _clear_current_frame(self):
        """Destroys the currently active frame."""
        if self._current_frame:
            self._current_frame.destroy()
            self._current_frame = None

    def _show_frame(self, frame_class, *args, **kwargs):
        """
        Clears the old frame and displays a new one.
        
        Args:
            frame_class: The class of the frame to create (e.g., LoginFrame).
            *args, **kwargs: Arguments to pass to the frame's constructor.
        """
        self._clear_current_frame()
        # Create a new instance of the frame
        self._current_frame = frame_class(self.root, self, *args, **kwargs)
        # Place the new frame in the root window
        self._current_frame.grid(row=0, column=0, sticky="nsew")

    # --- Frame Navigation Methods ---

    def show_login_frame(self):
        """Displays the login frame."""
        self.current_user = None # Ensure user is logged out
        self._show_frame(LoginFrame)

    def show_registration_frame(self):
        """Displays the student registration frame."""
        self._show_frame(RegistrationFrame)

    def show_main_menu(self):
        """
        Displays the correct main menu based on the
        type of the self.current_user.
        """
        if isinstance(self.current_user, Student):
            self._show_frame(StudentMenuFrame)
        elif isinstance(self.current_user, Admin):
            self._show_frame(AdminMenuFrame)
        else:
            # Fallback in case of an error
            self.show_error("Login Error", "Unknown user type. Logging out.")
            self.show_login_frame()

    # --- Public API for Frames ---
    # These methods are called by the frames to interact with
    # the controllers and navigate.

    def handle_login(self, user_id, password):
        """
        Called by LoginFrame.
        Attempts to log in via the AuthController.
        """
        # Call the controller
        user_obj, error = self.auth_controller.login(user_id, password)
        
        if error:
            self.show_error("Login Failed", error)
        else:
            self.current_user = user_obj
            self.show_main_menu()

    def handle_registration(self, name, email, password):
        """
        Called by RegistrationFrame.
        Attempts to register a new student.
        """
        # Call the controller
        student_obj, error = self.auth_controller.register_student(name, email, password)
        
        if error:
            self.show_error("Registration Failed", error)
        else:
            self.show_info(
                "Registration Successful",
                f"Student {student_obj.name} created.\n"
                f"Student ID {student_obj.id} has been assigned.\n"
                "Use this ID to log in."
            )
            self.show_login_frame() # Go back to login

    def handle_logout(self):
        """Called by menu frames to log out."""
        self.show_login_frame()

    # --- GUI Utility Methods ---

    def show_error(self, title, message):
        """Displays a standard error message box."""
        messagebox.showerror(title, message)

    def show_info(self, title, message):
        """Displays a standard info message box."""
        messagebox.showinfo(title, message)
    
    def show_yesno(self, title, message):
        """Displays a yes/no confirmation box."""
        return messagebox.askyesno(title, message)


# ===================================================================
# --- BASE FRAME (for styling) ---
# ===================================================================

class BaseFrame(ttk.Frame):
    """
    A base frame with common styling for all other frames.
    This ensures a consistent look and feel.
    """
    def __init__(self, parent_container, view, **kwargs):
        # Initialize the parent ttk.Frame
        super().__init__(parent_container, padding="20 20 20 20", **kwargs)
        
        self.parent_container = parent_container
        self.view = view # This is the main GUIView object
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        self.style.configure('Menu.TButton', font=('Arial', 12), padding=10)
        self.style.configure('Danger.TButton', foreground='red')

# ===================================================================
# --- LOGIN FRAME ---
# ===================================================================

class LoginFrame(BaseFrame):
    """
    The frame for handling user login.
    """
    def __init__(self, parent_container, view):
        super().__init__(parent_container, view)

        # Configure grid to center components
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Main Content Frame ---
        # We use an inner frame to hold the content,
        # which makes centering easier.
        content_frame = ttk.Frame(self, padding=30)
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        content_frame.grid_columnconfigure(0, minsize=100)
        content_frame.grid_columnconfigure(1, weight=1, minsize=200)

        # --- Widgets ---
        ttk.Label(
            content_frame, 
            text="University System Login", 
            style='Header.TLabel'
        ).grid(row=0, column=0, columnspan=2, pady=20)

        # User ID
        ttk.Label(content_frame, text="User ID:").grid(
            row=1, column=0, sticky="w", padx=5, pady=10)
        self.user_id_var = tk.StringVar()
        self.user_id_entry = ttk.Entry(
            content_frame, 
            textvariable=self.user_id_var, 
            width=40
        )
        self.user_id_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=10)

        # Password
        ttk.Label(content_frame, text="Password:").grid(
            row=2, column=0, sticky="w", padx=5, pady=10)
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            content_frame, 
            textvariable=self.password_var, 
            show="*", 
            width=40
        )
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=10)

        # --- Buttons ---
        button_frame = ttk.Frame(content_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Login Button
        self.login_button = ttk.Button(
            button_frame, 
            text="Login", 
            command=self._on_login_press
        )
        self.login_button.pack(side=tk.LEFT, padx=10)

        # Register Button
        self.register_button = ttk.Button(
            button_frame,
            text="Register as Student",
            command=self.view.show_registration_frame
        )
        self.register_button.pack(side=tk.LEFT, padx=10)
        
        # Bind <Return> key to login
        # FIX: Changed self.root to self.view.root
        self.view.root.bind('<Return>', self._on_login_press)

    def destroy(self):
        """On frame destruction, unbind the global key press."""
        try:
            self.view.root.unbind('<Return>')
        except Exception:
            # Failsafe in case view/root is already gone
            pass
        # Call the parent's destroy method
        super().destroy()

    def _on_login_press(self, event=None):
        """Callback for the login button or <Return> key."""
        user_id = self.user_id_var.get()
        password = self.password_var.get()
        
        if not user_id or not password:
            self.view.show_error("Login Failed", "Please enter both User ID and Password.")
            return
            
        # Unbind <Return> key to prevent double-presses
        # FIX: Changed self.root to self.view.root
        self.view.root.unbind('<Return>')
        
        # Call the main view's handler
        self.view.handle_login(user_id, password)
        
        # Re-bind the key in case login fails
        # FIX: Changed self.root to self.view.root
        self.view.root.bind('<Return>', self._on_login_press)


# ===================================================================
# --- REGISTRATION FRAME ---
# ===================================================================

class RegistrationFrame(BaseFrame):
    """
    The frame for new student registration.
    """
    def __init__(self, parent_container, view):
        super().__init__(parent_container, view)
        
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = ttk.Frame(self)
        content_frame.grid(sticky="n", pady=20)

        ttk.Label(content_frame, text="New Student Registration", style='Header.TLabel').pack(pady=20)

        # --- Form Frame ---
        form_frame = ttk.Frame(content_frame, padding=10)
        form_frame.pack()

        form_frame.grid_columnconfigure(0, minsize=100)
        form_frame.grid_columnconfigure(1, weight=1, minsize=250)
        
        # Full Name
        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var, width=40).grid(row=0, column=1, sticky="ew")

        # Email
        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var, width=40).grid(row=1, column=1, sticky="ew")

        # Password
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.password_var, show="*", width=40).grid(row=2, column=1, sticky="ew")

        # Confirm Password
        ttk.Label(form_frame, text="Confirm Password:").grid(row=3, column=0, sticky="w", pady=5)
        self.confirm_pass_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirm_pass_var, show="*", width=40).grid(row=3, column=1, sticky="ew")

        # --- Buttons ---
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=20)

        self.register_button = ttk.Button(
            button_frame, 
            text="Register", 
            command=self._on_register_press
        )
        self.register_button.pack(side=tk.LEFT, padx=10)

        self.back_button = ttk.Button(
            button_frame,
            text="Back to Login",
            command=self.view.show_login_frame
        )
        self.back_button.pack(side=tk.LEFT, padx=10)

        # Bind <Return> key to register
        self.view.root.bind('<Return>', self._on_register_press)

    def destroy(self):
        """On frame destruction, unbind the global key press."""
        try:
            self.view.root.unbind('<Return>')
        except Exception:
            # Failsafe in case view/root is already gone
            pass
        # Call the parent's destroy method
        super().destroy()

    def _on_register_press(self, event=None):
        """Callback for the register button."""
        name = self.name_var.get()
        email = self.email_var.get()
        password = self.password_var.get()
        confirm = self.confirm_pass_var.get()

        # --- Basic Validation ---
        if not all([name, email, password, confirm]):
            self.view.show_error("Error", "All fields are required.")
            return
        
        if password != confirm:
            self.view.show_error("Error", "Passwords do not match.")
            return
            
        # Call the main view's handler
        self.view.handle_registration(name, email, password)

# ===================================================================
# --- STUDENT MENU FRAME ---
# ===================================================================

class StudentMenuFrame(BaseFrame):
    """
    The main menu for a logged-in Student.
    """
    def __init__(self, parent_container, view):
        super().__init__(parent_container, view)
        
        self.student = self.view.current_user
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1) # Menu column
        self.grid_columnconfigure(1, weight=4) # Content column
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Menu Panel ---
        menu_panel = ttk.Frame(self, style='TFrame', padding=10)
        menu_panel.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        ttk.Label(
            menu_panel, 
            text=f"Welcome, {self.student.name.split()[0]}",
            style='Header.TLabel'
        ).pack(pady=10)
        
        ttk.Label(menu_panel, text=f"ID: {self.student.id}").pack(pady=2)
        ttk.Label(menu_panel, text=f"Email: {self.student.email}").pack(pady=(2, 20))
        
        # --- Menu Buttons ---
        self.create_menu_button(menu_panel, "My Enrolments", self.show_enrolments)
        self.create_menu_button(menu_panel, "Enrol in Subject", self.show_enrol)
        self.create_menu_button(menu_panel, "Drop Subject", self.show_drop)
        self.create_menu_button(menu_panel, "Change Password", self.show_change_password)
        
        # Spacer
        ttk.Frame(menu_panel, height=50, style='TFrame').pack()

        # Logout Button
        ttk.Button(
            menu_panel,
            text="Logout",
            command=self.view.handle_logout
        ).pack(fill=tk.X, padx=10, pady=10)

        # --- Right Content Panel ---
        self.content_panel = ttk.Frame(self, style='TFrame', padding=20)
        self.content_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Configure content panel to resize
        self.content_panel.grid_rowconfigure(0, weight=1)
        self.content_panel.grid_columnconfigure(0, weight=1)
        
        self._current_content_frame = None

        # Show default content
        self.show_enrolments()

    def create_menu_button(self, parent, text, command):
        """Helper to create consistent menu buttons."""
        ttk.Button(
            parent,
            text=text,
            command=command,
            style='Menu.TButton'
        ).pack(fill=tk.X, padx=10, pady=5)
    
    def _show_content_frame(self, frame_class, *args, **kwargs):
        """Clears and shows a new frame inside the content_panel."""
        if self._current_content_frame:
            self._current_content_frame.destroy()
        
        # Pass self (StudentMenuFrame) as the parent,
        # and self.view (GUIView) as the view
        self._current_content_frame = frame_class(
            self.content_panel, self.view, *args, **kwargs
        )
        self._current_content_frame.grid(row=0, column=0, sticky="nsew")

    # --- Navigation for Content Panel ---
    
    def show_enrolments(self):
        self._show_content_frame(StudentEnrolmentsFrame, self.student)
        
    def show_enrol(self):
        self._show_content_frame(StudentEnrolFrame, self.student)

    def show_drop(self):
        self._show_content_frame(StudentDropFrame, self.student)
        
    def show_change_password(self):
        self._show_content_frame(ChangePasswordFrame, self.student)


# --- Student Content Sub-Frames ---

class StudentEnrolmentsFrame(BaseFrame):
    """Displays the student's current enrolments in a table."""
    def __init__(self, parent, view, student):
        super().__init__(parent, view)
        
        ttk.Label(self, text="My Enrolments", style='Header.TLabel').pack(pady=10)
        
        # --- Treeview Table ---
        columns = ('code', 'subject', 'mark', 'grade')
        tree = ttk.Treeview(self, columns=columns, show='headings')
        
        tree.heading('code', text='Subject Code')
        tree.heading('subject', text='Subject Name')
        tree.heading('mark', text='Mark')
        tree.heading('grade', text='Grade')
        
        tree.column('code', width=100, anchor=tk.W)
        tree.column('subject', width=250, anchor=tk.W)
        tree.column('mark', width=80, anchor=tk.CENTER)
        tree.column('grade', width=80, anchor=tk.CENTER)
        
        # Get enrolments from the student object
        # (This is safe as the object is held by the view)
        enrolments = student.get_enrolments()
        
        if not enrolments:
            ttk.Label(self, text="You are not enrolled in any subjects.").pack(pady=20)
        else:
            for enr in enrolments:
                mark_str = enr.mark if enr.mark is not None else "N/A"
                grade_str = enr.grade.value if enr.grade else "N/A"
                tree.insert(
                    '', 
                    tk.END, 
                    values=(enr.subject.id, enr.subject.name, mark_str, grade_str)
                )
            
            tree.pack(fill=tk.BOTH, expand=True, pady=10)

class StudentEnrolFrame(BaseFrame):
    """Form for a student to enrol in a new subject."""
    def __init__(self, parent, view, student):
        super().__init__(parent, view)
        self.student = student
        
        ttk.Label(self, text="Enrol in a Subject", style='Header.TLabel').pack(pady=10)
        
        # --- Form ---
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Subject Code:").grid(row=0, column=0, padx=5, pady=5)
        self.subject_code_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.subject_code_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Enrol", command=self._on_enrol).grid(row=1, column=0, columnspan=2, pady=20)
        
    def _on_enrol(self):
        code = self.subject_code_var.get()
        if not code:
            self.view.show_error("Error", "Please enter a Subject Code.")
            return
            
        # Call the controller
        success, error = self.view.enrolment_controller.enrol_student(
            self.student.id, code
        )
        
        if error:
            self.view.show_error("Enrolment Failed", error)
        else:
            self.view.show_info("Success", f"Successfully enrolled in {code}.")
            # Refresh the main menu to reload the parent frame
            self.view.show_main_menu()

class StudentDropFrame(BaseFrame):
    """Form for a student to drop an enrolled subject."""
    def __init__(self, parent, view, student):
        super().__init__(parent, view)
        self.student = student
        
        ttk.Label(self, text="Drop a Subject", style='Header.TLabel').pack(pady=10)
        
        # --- Form ---
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Subject Code:").grid(row=0, column=0, padx=5, pady=5)
        self.subject_code_var = tk.StringVar()
        
        # --- Dropdown of enrolled subjects ---
        enrolled_codes = [enr.subject.id for enr in student.get_enrolments()]
        if not enrolled_codes:
            ttk.Label(form_frame, text="You have no subjects to drop.").grid(row=1, column=0, columnspan=2)
            return

        self.subject_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.subject_code_var, 
            values=enrolled_codes,
            width=28,
            state='readonly'
        )
        self.subject_combo.grid(row=0, column=1, padx=5, pady=5)
        if enrolled_codes:
            self.subject_combo.current(0) # Select first one
        
        ttk.Button(form_frame, text="Drop Subject", command=self._on_drop, style='Danger.TButton').grid(row=1, column=0, columnspan=2, pady=20)

    def _on_drop(self):
        code = self.subject_code_var.get()
        if not code:
            self.view.show_error("Error", "Please select a subject to drop.")
            return
            
        if not self.view.show_yesno("Confirm Drop", f"Are you sure you want to drop {code}?"):
            return
            
        # Call the controller
        success, error = self.view.enrolment_controller.unenrol_student(
            self.student.id, code
        )
        
        if error:
            self.view.show_error("Drop Failed", error)
        else:
            self.view.show_info("Success", f"Successfully dropped {code}.")
            # Refresh the main menu to reload the parent frame
            self.view.show_main_menu()
            
class ChangePasswordFrame(BaseFrame):
    """Form for a user to change their password."""
    def __init__(self, parent, view, user):
        super().__init__(parent, view)
        self.user = user
        
        ttk.Label(self, text="Change Password", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        form_frame.grid_columnconfigure(0, minsize=150)
        form_frame.grid_columnconfigure(1, weight=1, minsize=200)

        # New Password
        ttk.Label(form_frame, text="New Password:").grid(row=0, column=0, sticky="w", pady=5)
        self.pass_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.pass_var, show="*", width=30).grid(row=0, column=1, sticky="ew")

        # Confirm New Password
        ttk.Label(form_frame, text="Confirm New Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.confirm_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirm_var, show="*", width=30).grid(row=1, column=1, sticky="ew")

        ttk.Button(form_frame, text="Update Password", command=self._on_update).grid(row=2, column=0, columnspan=2, pady=20)

    def _on_update(self):
        new_pass = self.pass_var.get()
        confirm_pass = self.confirm_var.get()
        
        if not new_pass or not confirm_pass:
            self.view.show_error("Error", "All fields are required.")
            return
        
        if new_pass != confirm_pass:
            self.view.show_error("Error", "Passwords do not match.")
            return
            
        # Call the controller
        # We use enrolment_controller as it has the change_password method
        success, error = self.view.enrolment_controller.change_student_password(
            self.user.id, new_pass
        )
        
        if error:
            self.view.show_error("Update Failed", error)
        else:
            self.view.show_info("Success", "Password updated successfully.")
            self.pass_var.set("")
            self.confirm_var.set("")


# ===================================================================
# --- ADMIN MENU FRAME ---
# ===================================================================

class AdminMenuFrame(BaseFrame):
    """
    The main menu for a logged-in Admin.
    """
    def __init__(self, parent_container, view):
        super().__init__(parent_container, view)
        
        self.admin = self.view.current_user
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1) # Menu column
        self.grid_columnconfigure(1, weight=4) # Content column
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Menu Panel ---
        menu_panel = ttk.Frame(self, style='TFrame', padding=10)
        menu_panel.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        ttk.Label(
            menu_panel, 
            text=f"Welcome, {self.admin.name.split()[0]}",
            style='Header.TLabel'
        ).pack(pady=10)
        
        ttk.Label(menu_panel, text=f"ID: {self.admin.id}").pack(pady=2)
        ttk.Label(menu_panel, text=f"Email: {self.admin.email}").pack(pady=(2, 20))

        # --- Menu Buttons ---
        self.create_menu_button(menu_panel, "View All Students", self.show_all_students)
        self.create_menu_button(menu_panel, "Remove Student", self.show_remove_student)
        self.create_menu_button(menu_panel, "Set Student Mark", self.show_set_mark)
        
        ttk.Separator(menu_panel, orient='horizontal').pack(fill='x', pady=10, padx=10)

        self.create_menu_button(menu_panel, "Pass/Fail Report", self.show_pass_fail_report)
        self.create_menu_button(menu_panel, "Grade Report", self.show_grade_report)
        
        ttk.Separator(menu_panel, orient='horizontal').pack(fill='x', pady=10, padx=10)

        self.create_menu_button(menu_panel, "Clear All Data", self.show_clear_data)

        # Spacer
        ttk.Frame(menu_panel, height=50, style='TFrame').pack()

        # Logout Button
        ttk.Button(
            menu_panel,
            text="Logout",
            command=self.view.handle_logout
        ).pack(fill=tk.X, padx=10, pady=10)

        # --- Right Content Panel ---
        self.content_panel = ttk.Frame(self, style='TFrame', padding=20)
        self.content_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.content_panel.grid_rowconfigure(0, weight=1)
        self.content_panel.grid_columnconfigure(0, weight=1)
        
        self._current_content_frame = None

        # Show default content
        self.show_all_students()

    def create_menu_button(self, parent, text, command):
        """Helper to create consistent menu buttons."""
        ttk.Button(
            parent,
            text=text,
            command=command,
            style='Menu.TButton'
        # FIX: Corrected typo '1g' to '10'
        ).pack(fill=tk.X, padx=10, pady=5)
    
    def _show_content_frame(self, frame_class, *args, **kwargs):
        """Clears and shows a new frame inside the content_panel."""
        if self._current_content_frame:
            self._current_content_frame.destroy()
        
        self._current_content_frame = frame_class(
            self.content_panel, self.view, *args, **kwargs
        )
        self._current_content_frame.grid(row=0, column=0, sticky="nsew")

    # --- Navigation for Content Panel ---
    
    def show_all_students(self):
        self._show_content_frame(AdminAllStudentsFrame)
        
    def show_remove_student(self):
        self._show_content_frame(AdminRemoveStudentFrame)
        
    def show_set_mark(self):
        self._show_content_frame(AdminSetMarkFrame)

    def show_pass_fail_report(self):
        self._show_content_frame(AdminPassFailFrame)

    def show_grade_report(self):
        self._show_content_frame(AdminGradeReportFrame)

    def show_clear_data(self):
        self._show_content_frame(AdminClearDataFrame)

# --- Admin Content Sub-Frames ---

class AdminAllStudentsFrame(BaseFrame):
    """Displays a list of all registered students."""
    def __init__(self, parent, view):
        super().__init__(parent, view)
        
        ttk.Label(self, text="All Students", style='Header.TLabel').pack(pady=10)
        
        # --- Treeview Table ---
        columns = ('id', 'name', 'email', 'enrolments')
        tree = ttk.Treeview(self, columns=columns, show='headings')
        
        tree.heading('id', text='Student ID')
        tree.heading('name', text='Name')
        tree.heading('email', text='Email')
        tree.heading('enrolments', text='Enrolments')
        
        tree.column('id', width=100, anchor=tk.W)
        tree.column('name', width=200, anchor=tk.W)
        tree.column('email', width=200, anchor=tk.W)
        tree.column('enrolments', width=80, anchor=tk.CENTER)
        
        # Call controller to get data
        students = self.view.admin_controller.get_all_students()
        
        if not students:
            ttk.Label(self, text="No students found.").pack(pady=20)
        else:
            for s in students:
                tree.insert(
                    '', 
                    tk.END, 
                    values=(s.id, s.name, s.email, len(s.get_enrolments()))
                )
            tree.pack(fill=tk.BOTH, expand=True, pady=10)
            
class AdminRemoveStudentFrame(BaseFrame):
    """Form for an admin to remove a student."""
    def __init__(self, parent, view):
        super().__init__(parent, view)
        
        ttk.Label(self, text="Remove Student", style='Header.TLabel').pack(pady=10)
        
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5)
        self.student_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.student_id_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(form_frame, text="Remove Student", command=self._on_remove, style='Danger.TButton').grid(row=1, column=0, columnspan=2, pady=20)

    def _on_remove(self):
        student_id = self.student_id_var.get()
        if not student_id:
            self.view.show_error("Error", "Please enter a Student ID.")
            return
            
        if not self.view.show_yesno("Confirm Remove", f"Are you sure you want to remove student {student_id}? This is permanent."):
            return
            
        # Call controller
        error = self.view.admin_controller.remove_student(student_id)
        
        if error:
            self.view.show_error("Failed", error)
        else:
            self.view.show_info("Success", f"Student {student_id} removed.")
            self.view.show_main_menu() # Refresh

class AdminSetMarkFrame(BaseFrame):
    """Form for an admin to set a student's mark."""
    def __init__(self, parent, view):
        super().__init__(parent, view)
        
        ttk.Label(self, text="Set Student Mark", style='Header.TLabel').pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=20)
        
        form_frame.grid_columnconfigure(0, minsize=100)
        form_frame.grid_columnconfigure(1, weight=1, minsize=200)

        # Student ID
        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.student_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.student_id_var, width=30).grid(row=0, column=1, sticky="ew")
        
        # Subject Code
        ttk.Label(form_frame, text="Subject Code:").grid(row=1, column=0, sticky="w", pady=5)
        self.subject_code_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.subject_code_var, width=30).grid(row=1, column=1, sticky="ew")
        
        # Mark
        ttk.Label(form_frame, text="Mark (0-100):").grid(row=2, column=0, sticky="w", pady=5)
        self.mark_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.mark_var, width=30).grid(row=2, column=1, sticky="ew")

        ttk.Button(form_frame, text="Set Mark", command=self._on_set_mark).grid(row=3, column=0, columnspan=2, pady=20)

    def _on_set_mark(self):
        student_id = self.student_id_var.get()
        subject_code = self.subject_code_var.get()
        mark_str = self.mark_var.get()
        
        if not all([student_id, subject_code, mark_str]):
            self.view.show_error("Error", "All fields are required.")
            return
            
        try:
            mark_int = int(mark_str)
        except ValueError:
            self.view.show_error("Error", "Mark must be a number.")
            return
            
        # Call controller
        # We use enrolment_controller as it has the set_mark method
        success, error = self.view.enrolment_controller.set_student_mark(
            student_id, subject_code, mark_int
        )
        
        if error:
            self.view.show_error("Failed", error)
        else:
            self.view.show_info("Success", f"Mark for {student_id} in {subject_code} set to {mark_int}.")
            # Clear fields
            self.student_id_var.set("")
            self.subject_code_var.set("")
            self.mark_var.set("")

class AdminPassFailFrame(BaseFrame):
    """Displays the Pass/Fail report."""
    def __init__(self, parent, view):
        super().__init__(parent, view)
        
        ttk.Label(self, text="Pass/Fail Report", style='Header.TLabel').pack(pady=10)

        # Call controller
        if not self.view.reporting_controller:
            self.view.show_error("Error", "Reporting service is not available.")
            return
            
        data, error = self.view.admin_controller.get_pass_fail_partition()
        
        if error:
            self.view.show_error("Report Failed", error)
            return
        
        if not data:
            ttk.Label(self, text="No data found.").pack(pady=20)
            return

        # --- Display in two columns ---
        report_frame = ttk.Frame(self)
        report_frame.pack(fill='both', expand=True, pady=10)
        report_frame.grid_columnconfigure(0, weight=1)
        report_frame.grid_columnconfigure(1, weight=1)
        
        # PASS Column
        pass_frame = ttk.LabelFrame(report_frame, text=f"PASS ({len(data['PASS'])})", padding=10)
        pass_frame.grid(row=0, column=0, sticky="nsew", padx=10)
        
        pass_text = tk.Text(pass_frame, height=20, width=30, wrap=tk.NONE)
        pass_scroll = ttk.Scrollbar(pass_frame, orient=tk.VERTICAL, command=pass_text.yview)
        pass_text.config(yscrollcommand=pass_scroll.set)
        pass_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        pass_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for s in data['PASS']:
            pass_text.insert(tk.END, f"{s.id} - {s.name}\n")
        pass_text.config(state=tk.DISABLED)

        # FAIL Column
        fail_frame = ttk.LabelFrame(report_frame, text=f"FAIL ({len(data['FAIL'])})", padding=10)
        fail_frame.grid(row=0, column=1, sticky="nsew", padx=10)

        fail_text = tk.Text(fail_frame, height=20, width=30, wrap=tk.NONE)
        fail_scroll = ttk.Scrollbar(fail_frame, orient=tk.VERTICAL, command=fail_text.yview)
        fail_text.config(yscrollcommand=fail_scroll.set)
        fail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        fail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for s in data['FAIL']:
            fail_text.insert(tk.END, f"{s.id} - {s.name}\n")
        fail_text.config(state=tk.DISABLED)

class AdminGradeReportFrame(BaseFrame):
    """Displays the report grouping students by average grade."""
    def __init__(self, parent, view):
        super().__init__(parent, view)
        
        ttk.Label(self, text="Student Grade Report", style='Header.TLabel').pack(pady=10)

        # Call controller
        if not self.view.reporting_controller:
            self.view.show_error("Error", "Reporting service is not available.")
            return
            
        data, error = self.view.admin_controller.get_grade_grouping()

        if error:
            self.view.show_error("Report Failed", error)
            return

        if not data:
            ttk.Label(self, text="No data found.").pack(pady=20)
            return

        # --- Display in a single scrollable text area ---
        text_area = tk.Text(self, wrap=tk.WORD, height=25)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=text_area.yview)
        text_area.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Define the order
        grade_order = ['HD', 'D', 'C', 'P', 'F', 'N/A']
        
        for grade in grade_order:
            if grade in data:
                students = data[grade]
                text_area.insert(tk.END, f"--- {grade} ({len(students)}) ---\n")
                for s in students:
                    text_area.insert(tk.END, f"  {s.id} - {s.name}\n")
                text_area.insert(tk.END, "\n")
                
        text_area.config(state=tk.DISABLED)

class AdminClearDataFrame(BaseFrame):
    """Form for an admin to clear all student data."""
    def __init__(self, parent, view):
        super().__init__(parent, view)
        
        ttk.Label(self, text="Clear All Student Data", style='Header.TLabel', foreground='red').pack(pady=10)
        
        ttk.Label(
            self, 
            text="WARNING: This will permanently delete all students\n"
                 "and their enrolment data. Admin accounts will not be affected.\n"
                 "This action cannot be undone.",
            justify=tk.CENTER
        ).pack(pady=20)
        
        ttk.Button(self, text="CLEAR ALL DATA", command=self._on_clear, style='Danger.TButton').pack(pady=20, ipady=10)

    def _on_clear(self):
        if not self.view.show_yesno("Confirm Clear", "Are you 100% sure? This will delete all student data."):
            return
        
        if not self.view.show_yesno("Final Confirmation", "FINAL WARNING. This is irreversible. Are you absolutely sure?"):
            return

        # Call controller
        error = self.view.admin_controller.clear_all_data()
        
        if error:
            self.view.show_error("Failed", error)
        else:
            self.view.show_info("Success", "All student data has been cleared.")
            self.view.show_main_menu() # Refresh

