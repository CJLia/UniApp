"""
Defines the CLI (Command Line Interface) View.

This module contains all the logic for interacting
with the user via the console. It is responsible
for:
- Printing menus
- Getting user 'input()'
- Formatting data for display
- Passing user requests to the controllers

This file should *never* import from the 'services'
or 'models' directly. It only knows about the
'controllers'.
"""

# Import 'getpass' for securely getting password input
import getpass
# Import 'time' for 'sleep' to simulate loading
import time
# Import models *only* for type-checking and display
from src.models.user import User
from src.models.student import Student
from src.models.admin import Admin
from src.models.enrolment import Grade

# Import controllers
from src.controllers.auth_controller import AuthController
from src.controllers.enrolment_controller import EnrolmentController
from src.controllers.admin_controller import AdminController

class CLIView:
    """
    Manages all Command Line Interface interactions.

    This class holds references to all the controllers
    it needs to function. It keeps track of the
    'currently logged in' user.
    """

    def __init__(self, auth_controller, enrol_controller, admin_controller):
        """
        Initializes the CLIView.

        This uses Dependency Injection. The view
        is "given" its controllers when it is created.

        Args:
            auth_controller (AuthController): The controller
                for auth actions.
            enrol_controller (EnrolmentController): The controller
                for enrolment actions.
            admin_controller (AdminController): The controller
                for admin actions.
        """
        self._auth_controller = auth_controller
        self._enrol_controller = enrol_controller
        self._admin_controller = admin_controller
        
        # '_current_user' holds the object of the user
        # who is logged in (e.g., a Student object).
        # It is 'None' if no one is logged in.
        self._current_user = None

    # --- Utility Methods ---
    
    def _prompt(self, message):
        """
        A helper method for getting user input.
        """
        return input(f"  > {message}: ")

    def _show_message(self, message):
        """
        A helper method for printing messages.
        """
        print(f"  [!] {message}")

    def _show_error(self, error):
        """
        A helper method for printing error messages.
        """
        print(f"  [X] ERROR: {error}")

    def _show_success(self, message):
        """
        A helper method for printing success messages.
        """
        print(f"  [$] SUCCESS: {message}")

    def _show_header(self, title):
        """
        A helper method for printing a nice header.
        """
        print("\n" + "=" * 30)
        print(f"    {title.upper()}")
        print("=" * 30)

    def _pause(self):
        """
        Pauses the screen to let the user read.
        """
        input("\n  ... Press Enter to continue ...")

    # --- Main Menu Loop ---

    def run(self):
        """
        Starts the main application loop.
        """
        self._show_header("Welcome to CLIUniApp")
        while True:
            # If no user is logged in, show the auth menu
            if not self._current_user:
                print("\n  [1] Login")
                print("  [2] Register as Student")
                print("  [0] Exit Application")
                choice = self._prompt("Enter choice")
                
                if choice == "1":
                    self._handle_login()
                elif choice == "2":
                    self._handle_register_student()
                elif choice == "0":
                    self._show_message("Exiting application. Goodbye.")
                    break
                else:
                    self._show_error("Invalid choice. Please try again.")
            
            # If the logged-in user is a Student
            # We use 'hasattr' for a safe check, as the
            # 'Student' class may not be imported.
            elif hasattr(self._current_user, 'enrolments'):
                # This is a safe cast for type-hinting
                student = self._current_user
                self._run_student_menu(student)
            
            # If the logged-in user is an Admin
            else:
                # This is a safe cast for type-hinting
                admin = self._current_user
                self._run_admin_menu(admin)

    # --- Authentication Menus ---

    def _handle_login(self):
        """
        Handles the login workflow.
        """
        self._show_header("Login")
        user_id = self._prompt("Enter User ID")
        
        # Use 'getpass' so the password is not
        # echoed to the screen.
        password = getpass.getpass("  > Enter Password: ")

        # --- Call the Controller ---
        # The View calls the AuthController, passing
        # the raw data.
        user, error = self._auth_controller.login(user_id, password)

        # --- Handle the Response ---
        # The controller returns a (data, error) tuple.
        if error:
            # If 'error' is not None, login failed.
            self._show_error(error)
            self._pause()
        else:
            # If 'error' is None, login succeeded.
            # 'user' holds the User object.
            self._current_user = user
            self._show_success(f"Login successful. Welcome, {user.name}!")
            time.sleep(1) # Pause for 1 second

    def _handle_register_student(self):
        """
        Handles the student registration workflow.
        """
        self._show_header("Register Student")
        name = self._prompt("Enter Full Name")
        email = self._prompt("Enter Email")
        
        # --- Password Validation Loop ---
        while True:
            password = getpass.getpass("  > Enter New Password: ")
            confirm_password = getpass.getpass("  > Confirm New Password: ")
            
            if password != confirm_password:
                self._show_error("Passwords do not match. Please try again.")
            # (A real app would also call Validator.is_strong_password
            #  but this is simplified)
            elif len(password) < 8:
                 self._show_error("Password must be at least 8 characters.")
            else:
                # Password is valid, exit the loop
                break

        # --- Call the Controller ---
        student, error = self._auth_controller.register_student(
            name, email, password
        )

        # --- Handle the Response ---
        if error:
            self._show_error(error)
            self._pause()
        else:
            self._show_success(
                f"Registration successful! Your new Student ID is: {student.id}"
            )
            self._show_message("Please log in with your new ID.")
            self._pause()

    def _handle_logout(self):
        """
        Logs out the current user.
        """
        self._show_message(f"Logging out {self._current_user.name}...")
        self._current_user = None
        time.sleep(1)

    # --- Student Menu ---

    def _run_student_menu(self, student):
        """
        Displays and handles the main menu for a Student.
        """
        self._show_header(f"Student Menu ({student.name})")
        print("  [1] View My Enrolment")
        print("  [2] Enrol in a Subject")
        print("  [3] Drop a Subject")
        print("  [4] Change My Password")
        print("  [0] Logout")
        choice = self._prompt("Enter choice")
        
        if choice == "1":
            self._handle_view_enrolment(student)
        elif choice == "2":
            self._handle_enrol_subject(student)
        elif choice == "3":
            self._handle_drop_subject(student)
        elif choice == "4":
            self._handle_change_password(student)
        elif choice == "0":
            self._handle_logout()
        else:
            self._show_error("Invalid choice. Please try again.")

    def _handle_view_enrolment(self, student):
        """
        Displays the student's current enrolments.
        """
        self._show_header("My Enrolments")
        
        # Get the list of enrolments from the
        # 'student' object directly.
        enrolments = student.enrolments
        
        if not enrolments:
            self._show_message("You are not currently enrolled in any subjects.")
            self._pause()
            return
        
        # Display a formatted table
        print(f"  {'ID':<10} | {'Subject Code':<12} | {'Mark':<5} | {'Grade':<5}")
        print("  " + "-" * 47)
        for enr in enrolments:
            # Format mark/grade display
            mark_str = str(enr.mark) if enr.mark is not None else "N/A"
            grade_str = str(enr.grade.name) if enr.grade else "N/A"
            
            print(f"  {enr.id:<10} | {enr.subject.id:<12} | {mark_str:<5} | {grade_str:<5}")
            
        self._pause()

    def _handle_enrol_subject(self, student):
        """
        Handles the workflow for enrolling in a subject.
        """
        self._show_header("Enrol in Subject")
        
        # --- Display available subjects ---
        # This is a workaround; the View asks
        # its controller for the data store to get
        # the subjects. This assumes the enrolment_controller
        # has a 'get_all_subjects(data_store)' method.
        # This accesses a "private" attribute, which is
        # not ideal but works for this structure.
        all_subjects = self._enrol_controller.get_all_subjects(
            self._admin_controller._data_store 
        )
        
        print("  --- Available Subjects ---")
        for subj in all_subjects:
            print(f"    [{subj.id}] {subj.name}")
        print("  " + "-" * 26)
        
        subject_id = self._prompt("Enter Subject ID to enrol in")
        
        # --- Call the Controller ---
        error = self._enrol_controller.enrol_subject(student, subject_id)
        
        # --- Handle the Response ---
        if error:
            self._show_error(error)
        else:
            self._show_success(
                f"Successfully enrolled in subject {subject_id}."
            )
        
        self._pause()

    def _handle_drop_subject(self, student):
        """
        Handles the workflow for dropping a subject.
        """
        self._show_header("Drop Subject")
        
        # Show enrolments first so user can see IDs
        enrolments = student.enrolments
        if not enrolments:
            self._show_message("You are not enrolled in any subjects.")
            self._pause()
            return

        print("  --- Your Enrolments ---")
        for enr in enrolments:
            print(f"    [{enr.id}] {enr.subject.id} - {enr.subject.name}")
        print("  " + "-" * 26)
        
        enrolment_id = self._prompt("Enter Enrolment ID to drop")
        
        # --- Call the Controller ---
        error = self._enrol_controller.drop_subject(student, enrolment_id)
        
        # --- Handle the Response ---
        if error:
            self._show_error(error)
        else:
            self._show_success(
                f"Successfully dropped enrolment {enrolment_id}."
            )
        
        self._pause()

    def _handle_change_password(self, user):
        """
        Handles the workflow for changing a password.
        This works for both Students and Admins.
        """
        self._show_header("Change Password")
        
        while True:
            new_password = getpass.getpass("  > Enter New Password: ")
            confirm_password = getpass.getpass("  > Confirm New Password: ")
            
            if new_password != confirm_password:
                self._show_error("Passwords do not match. Please try again.")
            elif len(new_password) < 8:
                 self._show_error("Password must be at least 8 characters.")
            else:
                break # Success
        
        # --- Call the Controller ---
        error = self._enrol_controller.change_password(user, new_password)
        
        # --- Handle the Response ---
        if error:
            self._show_error(error)
        else:
            self._show_success("Password changed successfully.")
        
        self._pause()

    # --- Admin Menu ---

    def _run_admin_menu(self, admin):
        """
        Displays and handles the main menu for an Admin.
        """
        self._show_header(f"Admin Menu ({admin.name})")
        print("  [1] View All Students")
        print("  [2] View Pass/Fail Partition")
        print("  [3] View Grade Grouping")
        print("  [4m] Set Student Mark")
        print("  [5] Remove a Student")
        print("  [6] Clear All Student Data")
        print("  [7] Change My Password")
        print("  [0] Logout")
        choice = self._prompt("Enter choice")
        
        if choice == "1":
            self._handle_view_all_students()
        elif choice == "2":
            self._handle_pass_fail_partition()
        elif choice == "3":
            self._handle_grade_grouping()
        elif choice == "4m":
            self._handle_admin_set_mark()
        elif choice == "5":
            self._handle_remove_student()
        elif choice == "6":
            self._handle_clear_all_data()
        elif choice == "7":
            self._handle_change_password(admin) # Re-use
        elif choice == "0":
            self._handle_logout()
        else:
            self._show_error("Invalid choice. Please try again.")

    def _handle_view_all_students(self):
        """
        Displays a list of all students.
        """
        self._show_header("All Students")
        
        # --- Call the Controller ---
        all_students = self._admin_controller.get_all_students()
        
        if not all_students:
            self._show_message("There are no students in the system.")
            self._pause()
            return
            
        print(f"  {'ID':<10} | {'Name':<25} | {'Email':<30}")
        print("  " + "-" * 69)
        for student in all_students:
            print(f"  {student.id:<10} | {student.name:<25} | {student.email:<30}")
            
        self._pause()

    def _handle_pass_fail_partition(self):
        """
        Displays the Pass/Fail student partition.
        """
        self._show_header("Pass/Fail Partition")
        
        # --- Call the Controller ---
        data, error = self._admin_controller.get_pass_fail_partition()
        
        if error:
            self._show_error(error)
            self._pause()
            return
            
        # --- Display PASS List ---
        print("\n  --- [PASS] Students ---")
        if not data["PASS"]:
            print("    (No students in this category)")
        else:
            for student in data["PASS"]:
                print(f"    - {student.id}: {student.name}")
        
        # --- Display FAIL List ---
        print("\n  --- [FAIL] Students ---")
        if not data["FAIL"]:
            print("    (No students in this category)")
        else:
            for student in data["FAIL"]:
                print(f"    - {student.id}: {student.name}")
                
        self._pause()

    def _handle_grade_grouping(self):
        """
        Displays enrolments grouped by grade.
        """
        self._show_header("Enrolments by Grade")
        
        # --- Call the Controller ---
        data, error = self._admin_controller.get_grade_grouping()
        
        if error:
            self._show_error(error)
            self._pause()
            return
        
        # Loop through all possible grades (HD, D, C, P, F, NA)
        for grade in Grade:
            print(f"\n  --- [{grade.name}] {grade.value} ---")
            
            enrolments = data[grade]
            if not enrolments:
                print("    (No enrolments in this category)")
            else:
                for enr in enrolments:
                    # Find which student this enrolment
                    # belongs to (this is slow, but OK for CLI)
                    student_name = "N/A"
                    all_students = self._admin_controller.get_all_students()
                    for s in all_students:
                        if s.get_enrolment_by_id(enr.id):
                            student_name = s.name
                            break
                    
                    print(f"    - {enr.id}: {enr.subject.id} (Mark: {enr.mark}) - {student_name}")
                    
        self._pause()

    def _handle_remove_student(self):
        """
        Handles the workflow for removing a student.
        """
        self._show_header("Remove a Student")
        
        # Show all students so Admin can see IDs
        self._handle_view_all_students()
        print("  " + "-" * 69)
        
        student_id = self._prompt("Enter Student ID to REMOVE")
        
        if not student_id:
            self._show_message("Cancelled.")
            self._pause()
            return
            
        # --- Call the Controller ---
        error = self._admin_controller.remove_student(student_id)
        
        # --- Handle the Response ---
        if error:
            self._show_error(error)
        else:
            self._show_success(
                f"Student {student_id} has been removed."
            )
        
        self._pause()

    def _handle_admin_set_mark(self):
        """
        A demo function for an Admin to set a mark
        on behalf of a student.
        """
        self._show_header("Set Student Mark")
        
        # Get Student
        self._handle_view_all_students()
        print("  " + "-" * 69)
        student_id = self._prompt("Enter Student ID to modify")
        
        # Find the student object
        all_students = self._admin_controller.get_all_students()
        student_to_mark = None
        for s in all_students:
            if s.id == student_id:
                student_to_mark = s
                break
        
        if not student_to_mark:
            self._show_error("Student ID not found.")
            self._pause()
            return
            
        # Get Enrolment
        self._handle_view_enrolment(student_to_mark)
        enrolment_id = self._prompt(f"Enter Enrolment ID for {student_to_mark.name}")
        
        # Get Mark
        mark_str = self._prompt("Enter Mark (e.g., 85)")
        
        # --- Call the Controller ---
        # The Admin uses the *same* EnrolmentController
        # as the student.
        error = self._enrol_controller.set_mark(
            student_to_mark, enrolment_id, mark_str
        )
        
        if error:
            self._show_error(error)
        else:
            self._show_success("Mark updated successfully.")
            
        self._pause()

    def _handle_clear_all_data(self):
        """
        Handles the workflow for clearing all student data.
        """
        self._show_header("Clear All Student Data")
        self._show_error("! WARNING ! This action is irreversible.")
        self._show_error("This will delete all registered students")
        self._show_error("and their enrolment data.")
        
        confirm = self._prompt(
            "Type 'CLEAR' to confirm, or anything else to cancel"
        )
        
        if confirm != "CLEAR":
            self._show_message("Action cancelled.")
            self._pause()
            return
            
        # --- Call the Controller ---
        error = self._admin_controller.clear_all_data()
        
        if error:
            self._show_error(error)
        else:
            self._show_success("All student data has been cleared.")
            
        self._pause()
