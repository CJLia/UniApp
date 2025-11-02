import sys
import os
from pathlib import Path

try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except (NameError, AttributeError):
    cwd = Path(os.getcwd()).resolve()
    if str(cwd) not in sys.path:
        sys.path.insert(0, str(cwd))

from src.controllers.auth_controllers import AuthController
from src.controllers.enrolment_controller import EnrolmentController
from src.controllers.admin_controller import AdminController

from src.models.student import Student
from src.models.admin import Admin

from src.utils.exceptions import (
    DataPersistenceException,
    InvalidCredentialsException,
    UserNotFoundException,
    EmailAlreadyExistsException,
    InvalidEmailException,
    InvalidPasswordException,
    StudentNotFoundException,
    SubjectNotFoundException,
    AlreadyEnrolledException,
    MaxSubjectsExceededException,
    NotEnrolledException,
    InvalidMarkException
)


class MainController:
    
    def __init__(self, auth_controller, enrolment_controller, admin_controller):
        self._auth_controller = auth_controller
        self._enrolment_controller = enrolment_controller
        self._admin_controller = admin_controller
        self._current_user = None
    
    def run(self):
        while True:
            try:
                self._display_main_menu()
                choice = input("Choose your option: ").strip()
                
                if choice == '1':
                    self._handle_register()
                elif choice == '2':
                    self._handle_login()
                elif choice == '3':
                    print("\nExiting University System. Goodbye!")
                    break
                else:
                    print("\nInvalid option. Please choose 1, 2, or 3.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting University System. Goodbye!")
                break
            except DataPersistenceException as e:
                print(f"\nError: File operation failed - {e}")
                print("Please check file permissions and try again.")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")
    
    def _display_main_menu(self):
        print("\n" + "=" * 50)
        print("University System")
        print("=" * 50)
        print("1. Register as student")
        print("2. Login")
        print("3. Exit")
        print("=" * 50)
    
    def _handle_register(self):
        print("\n--- Student Registration ---")
        
        try:
            name = input("Enter your name: ").strip()
            if not name:
                print("Error: Name cannot be empty.")
                return
            
            email = input("Enter your email: ").strip()
            if not email:
                print("Error: Email cannot be empty.")
                return
            
            password = input("Enter your password: ").strip()
            if not password:
                print("Error: Password cannot be empty.")
                return
            
            student, error = self._auth_controller.register_student(name, email, password)
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"\nSuccess! Student registered with ID: {student.id}")
                print(f"Name: {student.name}")
                print(f"Email: {student.email}")
                
        except Exception as e:
            print(f"Error during registration: {e}")
    
    def _handle_login(self):
        print("\n--- Login ---")
        
        try:
            user_id = input("Enter your user ID: ").strip()
            if not user_id:
                print("Error: User ID cannot be empty.")
                return
            
            password = input("Enter your password: ").strip()
            if not password:
                print("Error: Password cannot be empty.")
                return
            
            user, error = self._auth_controller.login(user_id, password)
            
            if error:
                print(f"Error: {error}")
            else:
                self._current_user = user
                
                if isinstance(user, Student):
                    self._run_student_menu()
                elif isinstance(user, Admin):
                    self._run_admin_menu()
                else:
                    print("Error: Unknown user type.")
                    
        except Exception as e:
            print(f"Error during login: {e}")
    
    def _run_student_menu(self):
        while True:
            try:
                self._display_student_menu()
                choice = input("Choose your option: ").strip()
                
                if choice == '1':
                    self._handle_enrol_subject()
                elif choice == '2':
                    self._handle_unenrol_subject()
                elif choice == '3':
                    self._handle_view_enrolments()
                elif choice == '4':
                    self._handle_change_password()
                elif choice == '5':
                    self._current_user = None
                    print("\nLogged out successfully.")
                    break
                else:
                    print("\nInvalid option. Please choose 1-5.")
                    
            except KeyboardInterrupt:
                print("\n\nReturning to main menu...")
                self._current_user = None
                break
            except DataPersistenceException as e:
                print(f"\nError: File operation failed - {e}")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")
    
    def _display_student_menu(self):
        print("\n" + "=" * 50)
        print("Student Menu")
        print("=" * 50)
        print(f"Logged in as: {self._current_user.name} ({self._current_user.id})")
        print("=" * 50)
        print("1. Enrol in subject")
        print("2. Drop subject")
        print("3. View my enrolments")
        print("4. Change password")
        print("5. Logout")
        print("=" * 50)
    
    def _handle_enrol_subject(self):
        print("\n--- Enrol in Subject ---")
        
        if not self._current_user or not isinstance(self._current_user, Student):
            print("Error: Invalid session.")
            return
        
        try:
            subject_code = input("Enter subject code: ").strip().upper()
            if not subject_code:
                print("Error: Subject code cannot be empty.")
                return
            
            success, error = self._enrolment_controller.enrol_student(
                self._current_user.id, subject_code
            )
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Successfully enrolled in {subject_code}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _handle_unenrol_subject(self):
        print("\n--- Drop Subject ---")
        
        if not self._current_user or not isinstance(self._current_user, Student):
            print("Error: Invalid session.")
            return
        
        try:
            subject_code = input("Enter subject code: ").strip().upper()
            if not subject_code:
                print("Error: Subject code cannot be empty.")
                return
            
            success, error = self._enrolment_controller.unenrol_student(
                self._current_user.id, subject_code
            )
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Successfully dropped {subject_code}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _handle_view_enrolments(self):
        print("\n--- My Enrolments ---")
        
        if not self._current_user or not isinstance(self._current_user, Student):
            print("Error: Invalid session.")
            return
        
        try:
            enrolments = self._current_user.get_enrolments()
            
            if not enrolments:
                print("You are not enrolled in any subjects.")
            else:
                print(f"\nEnrolments for {self._current_user.name} ({self._current_user.id}):")
                print("-" * 60)
                
                for i, enrolment in enumerate(enrolments, 1):
                    mark_str = str(enrolment.mark) if enrolment.mark is not None else "N/A"
                    grade_str = enrolment.grade.value if enrolment.grade else "N/A"
                    
                    print(f"{i}. {enrolment.subject.id} - {enrolment.subject.name}")
                    print(f"   Mark: {mark_str}, Grade: {grade_str}")
                
                self._display_student_average(enrolments)
                print("-" * 60)
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _display_student_average(self, enrolments):
        try:
            marks = [e.mark for e in enrolments if e.mark is not None]
            
            if marks:
                average = sum(marks) / len(marks)
                print(f"\nAverage Mark: {average:.2f}")
            else:
                print("\nAverage Mark: N/A (no marks available)")
                
        except Exception:
            print("\nAverage Mark: N/A")
    
    def _handle_change_password(self):
        print("\n--- Change Password ---")
        
        if not self._current_user or not isinstance(self._current_user, Student):
            print("Error: Invalid session.")
            return
        
        try:
            new_password = input("Enter new password: ").strip()
            if not new_password:
                print("Error: Password cannot be empty.")
                return
            
            confirm_password = input("Confirm new password: ").strip()
            if new_password != confirm_password:
                print("Error: Passwords do not match.")
                return
            
            success, error = self._enrolment_controller.change_student_password(
                self._current_user.id, new_password
            )
            
            if error:
                print(f"Error: {error}")
            else:
                print("Password changed successfully.")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _run_admin_menu(self):
        while True:
            try:
                self._display_admin_menu()
                choice = input("Choose your option: ").strip()
                
                if choice == '1':
                    self._handle_display_all_students()
                elif choice == '2':
                    self._handle_group_by_grade()
                elif choice == '3':
                    self._handle_pass_fail_partition()
                elif choice == '4':
                    self._handle_remove_student()
                elif choice == '5':
                    self._handle_clear_all_data()
                elif choice == '6':
                    self._current_user = None
                    print("\nLogged out successfully.")
                    break
                else:
                    print("\nInvalid option. Please choose 1-6.")
                    
            except KeyboardInterrupt:
                print("\n\nReturning to main menu...")
                self._current_user = None
                break
            except DataPersistenceException as e:
                print(f"\nError: File operation failed - {e}")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")
    
    def _display_admin_menu(self):
        print("\n" + "=" * 50)
        print("Admin Menu")
        print("=" * 50)
        print(f"Logged in as: {self._current_user.name} ({self._current_user.id})")
        print("=" * 50)
        print("1. Display all students")
        print("2. Group students by grade")
        print("3. Partition students by PASS/FAIL")
        print("4. Remove student by ID")
        print("5. Clear all student data")
        print("6. Logout")
        print("=" * 50)
    
    def _handle_display_all_students(self):
        print("\n--- All Students ---")
        
        try:
            students = self._admin_controller.get_all_students()
            
            if not students:
                print("No students registered.")
            else:
                print(f"\nTotal students: {len(students)}")
                print("-" * 60)
                
                for i, student in enumerate(students, 1):
                    print(f"{i}. {student.id} - {student.name} ({student.email})")
                    
                print("-" * 60)
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _handle_group_by_grade(self):
        print("\n--- Students Grouped by Grade ---")
        
        try:
            groups, error = self._admin_controller.get_grade_grouping()
            
            if error:
                print(f"Error: {error}")
            else:
                if not groups:
                    print("No students to group.")
                else:
                    grade_order = ['HD', 'DN', 'CR', 'PS', 'FL']
                    
                    for grade in grade_order:
                        if grade in groups and groups[grade]:
                            students = groups[grade]
                            print(f"\n{grade} ({len(students)} student(s)):")
                            print("-" * 40)
                            for student in students:
                                print(f"  - {student.id} - {student.name}")
                    
                    print("-" * 40)
                    
        except Exception as e:
            print(f"Error: {e}")
    
    def _handle_pass_fail_partition(self):
        print("\n--- Students Partitioned by PASS/FAIL ---")
        
        try:
            partition, error = self._admin_controller.get_pass_fail_partition()
            
            if error:
                print(f"Error: {error}")
            else:
                if not partition:
                    print("No students to partition.")
                else:
                    if 'PASS' in partition and partition['PASS']:
                        pass_students = partition['PASS']
                        print(f"\nPASS ({len(pass_students)} student(s)):")
                        print("-" * 40)
                        for student in pass_students:
                            print(f"  - {student.id} - {student.name}")
                    
                    if 'FAIL' in partition and partition['FAIL']:
                        fail_students = partition['FAIL']
                        print(f"\nFAIL ({len(fail_students)} student(s)):")
                        print("-" * 40)
                        for student in fail_students:
                            print(f"  - {student.id} - {student.name}")
                    
                    print("-" * 40)
                    
        except Exception as e:
            print(f"Error: {e}")
    
    def _handle_remove_student(self):
        print("\n--- Remove Student ---")
        
        try:
            student_id = input("Enter student ID to remove: ").strip()
            if not student_id:
                print("Error: Student ID cannot be empty.")
                return
            
            error = self._admin_controller.remove_student(student_id)
            
            if error:
                print(f"Error: {error}")
            else:
                print(f"Student {student_id} removed successfully.")
                
        except Exception as e:
            print(f"Error: {e}")
    
    def _handle_clear_all_data(self):
        print("\n--- Clear All Student Data ---")
        
        try:
            confirm = input("Are you sure you want to clear ALL student data? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                error = self._admin_controller.clear_all_data()
                
                if error:
                    print(f"Error: {error}")
                else:
                    print("All student data cleared successfully.")
            else:
                print("Operation cancelled.")
                
        except Exception as e:
            print(f"Error: {e}")
