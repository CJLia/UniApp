"""
This file defines the Abstract Base Classes (ABCs) for all
services used in the application.

These 'interfaces' act as contracts. They define *what* a
service must do, but not *how* it must do it. This is a
core concept of OOP and the design schema, allowing for
'loose coupling'. This allows the implementation (e.g.,
from a file-based data store to a database) to be swapped
out without changing any other part of the system.
"""

# Import ABC (Abstract Base Class) and abstractmethod from
# the 'abc' (abstract base classes) module
from abc import ABC, abstractmethod

# --- Auth Service Interface ---
class IAuthService(ABC):
    """
    Interface for the Authentication Service.
    Defines the contract for all authentication-related operations.
    """

    @abstractmethod
    def login(self, user_id, password):
        """
        Authenticates a user based on their ID and password.

        Args:
            user_id (str): The ID of the user trying to log in.
            password (str): The plain-text password to check.

        Returns:
            User: The authenticated User object (e.g., Student or Admin).

        Raises:
            InvalidCredentialsException: If the ID or password is incorrect.
            UserNotFoundException: If the user ID does not exist.
        """
        # Abstract methods have no implementation, so 'pass' is used
        pass

    @abstractmethod
    def register_student(self, name, email, password):
        """
        Creates a new student account.

        Args:
            name (str): The student's full name.
            email (str): The student's email address.
            password (str): The student's plain-text password.

        Returns:
            Student: The newly created Student object.

        Raises:
            EmailAlreadyExistsException: If a user with this email
                                         is already registered.
            InvalidEmailException: If the email format is not valid.
            InvalidPasswordException: If the password is not strong enough.
        """
        pass

# --- Data Store Interface ---
class IDataStore(ABC):
    """
    Interface for the Data Storage Service.
    Defines a contract for all CRUD (Create, Read, Update, Delete)
    operations, abstracting the persistence layer (e.g., files, DB).
    """
    
    @abstractmethod
    def load_data(self):
        """
        Loads all application data from the persistent store.

        Returns:
            dict: A dictionary containing all data (e.g., {'users': [...],
                  'subjects': [...]}).
        """
        pass

    @abstractmethod
    def save_data(self):
        """
        Saves all application data to the persistent store.
        """
        pass

    @abstractmethod
    def get_all_users(self):
        """
        Retrieves all user objects from the data store.

        Returns:
            list: A list of all User objects (Students and Admins).
        """
        pass
        
    @abstractmethod
    def get_all_subjects(self):
        """
        Retrieves all subject objects from the data store.

        Returns:
            list: A list of all Subject objects.
        """
        pass
        
    @abstractmethod
    def add_user(self, user):
        """
        Adds a new user to the data store.

        Args:
            user (User): The User object to add.
        """
        pass
        
    @abstractmethod
    def update_user(self, user):
        """
        Updates an existing user in the data store.

        Args:
            user (User): The User object with updated information.
        """
        pass
        
    @abstractmethod
    def delete_user(self, user_id):
        """
        Deletes a user from the data store by their ID.

        Args:
            user_id (str): The ID of the user to delete.
        """
        pass
    
    @abstractmethod
    def clear_all_data(self):
        """
        Completely clears all student data from the data store.
        This is an administrative function.
        """
        pass

# --- Enrolment Service Interface ---
class IEnrolmentService(ABC):
    """
    Interface for the Enrolment Management Service.
    Defines the contract for all business logic related to
    student enrolments.
    """

    @abstractmethod
    def enrol(self, student_id, subject_code):
        """
        Enrols a student in a specific subject.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The ID of the subject.

        Raises:
            StudentNotFoundException: If the student ID is not found.
            SubjectNotFoundException: If the subject ID is not found.
            AlreadyEnrolledException: If the student is already enrolled.
            MaxSubjectsExceededException: If the student is already
                                          enrolled in the maximum
                                          allowed subjects.
        """
        pass

    @abstractmethod
    def unenrol(self, student_id, subject_code):
        """
        Withdraws a student from a specific subject.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The ID of the subject.

        Raises:
            StudentNotFoundException: If the student ID is not found.
            SubjectNotFoundException: If the subject ID is not found.
            NotEnrolledException: If the student is not enrolled in
                                  the specified subject.
        """
        pass

    @abstractmethod
    def set_mark(self, student_id, subject_code, mark):
        """
        Sets the numerical mark for a student's enrolment.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The ID of the subject.
            mark (int): The numerical mark (e.g., 0-100).

        Raises:
            StudentNotFoundException: ...
            SubjectNotFoundException: ...
            NotEnrolledException: ...
            InvalidMarkException: If the mark is outside the valid range.
        """
        pass

    @abstractmethod
    def change_password(self, user_id, new_password):
        """
        Changes a user's password.

        Args:
            user_id (str): The ID of the user.
            new_password (str): The new plain-text password.
            
        Raises:
            StudentNotFoundException: If the user ID is invalid.
            InvalidPasswordException: If the new password is not
                                      strong enough.
        """
        pass

# --- Reporting Service Interface ---
class IReportingService(ABC):
    """
    Interface for the Reporting Service.
    Defines the contract for operations that aggregate or
    process data for reporting purposes.
    """

    @abstractmethod
    def get_pass_fail_partition(self) -> dict:
        """
        Partitions all students into two groups: PASS and FAIL.
        A student is in FAIL if they have failed one or more subjects.
        A student is in PASS if they have no failed subjects.

        Returns:
            dict: A dictionary, e.g.,
                  {'PASS': [Student, ...], 'FAIL': [Student, ...]}
        """
        pass

    @abstractmethod
    def get_grade_grouping(self) -> dict:
        """
        Groups all students based on their average grade.

        Returns:
            dict: A dictionary, e.g.,
                  {'HD': [Student, ...], 'DN': [Student, ...], ...}
        """
        pass
        
# --- Grade Policy Interface ---
class IGradePolicy(ABC):
    """
    Interface for the Grading Policy Strategy.
    Defines the contract for calculating grades from marks.
    This separates the 'rules' of grading from the 'logic'
    of enrolment.
    """
    
    @abstractmethod
    def get_grade_for_mark(self, mark):
        """
        Calculates the grade for a given numerical mark.

        Args:
            mark (int): The numerical mark.

        Returns:
            Grade: The corresponding Grade enum (e.g., Grade.HD).
        """
        pass
        
    @abstractmethod
    def is_pass_mark(self, mark):
        """
        Determines if a numerical mark is a passing mark.

        Args:
            mark (int): The numerical mark.

        Returns:
            bool: True if the mark is passing, False otherwise.
        """
        pass

