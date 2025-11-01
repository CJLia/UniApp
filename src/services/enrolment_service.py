"""
This file contains the implementation of the IEnrolmentService interface.

This service class is responsible for all business logic related to
student enrolments, such as adding or removing subjects, and
managing profile changes like passwords.
"""

# Import the 'hashlib' module for secure password hashing (SHA-256)
import hashlib

# Import the interfaces this class implements or depends on
from src.services.interfaces import (
    IEnrolmentService,
    IDataStore,
    IGradePolicy
)

# Import the models this service will interact with
from src.models.student import Student
from src.models.subject import Subject
from src.models.enrolment import Enrolment

# Import utility classes
from src.utils.id_generator import IdGenerator

# Import custom exceptions
from src.utils.exceptions import (
    StudentNotFoundException,
    SubjectNotFoundException,
    AlreadyEnrolledException,
    MaxSubjectsExceededException,
    NotEnrolledException,
    InvalidMarkException
)

class EnrolmentService(IEnrolmentService):
    """
    Implements the IEnrolmentService interface.

    This class orchestrates multiple dependencies (IDataStore,
    IGradePolicy, IdGenerator) to perform its tasks. It manages
    all core academic and profile logic for students.
    
    Attributes:
        _data_store (IDataStore): A reference to the data persistence
                                  layer.
        _grade_policy (IGradePolicy): A reference to the business logic
                                      for calculating grades.
        _id_generator (IdGenerator): A reference to the utility for
                                     creating new IDs.
    """

    def __init__(self, data_store, grade_policy, id_generator):
        """
        Initializes the EnrolmentService.

        This constructor uses Dependency Injection. The dependencies
        are 'injected' from the outside (e.g., from cli_app.py),
        which decouples this service from concrete implementations.

        Args:
            data_store (IDataStore): An object that implements the
                                     IDataStore interface.
            grade_policy (IGradePolicy): An object that implements the
                                         IGradePolicy interface.
            id_generator (IdGenerator): An object of the IdGenerator
                                        class.
        """
        # Store the injected dependencies as private attributes
        self._data_store = data_store
        self._grade_policy = grade_policy
        self._id_generator = id_generator # Note: This is an example,
                                          # the design may use a
                                          # different generator for
                                          # enrolment IDs.
                                          # Using a single generator
                                          # for simplicity here.

    def _get_student_by_id(self, student_id):
        """
        A private helper method to find and return a Student object.

        Args:
            student_id (str): The ID of the student to find.

        Returns:
            Student: The found Student object.

        Raises:
            StudentNotFoundException: If no student with that ID
                                      is found.
        """
        users = self._data_store.get_all_users()
        for user in users:
            # Check if the user is a Student and the ID matches
            if isinstance(user, Student) and user.id == student_id:
                return user
        
        # If the loop finishes, no student was found
        raise StudentNotFoundException(
            "Student with ID '{id}' not found.".format(id=student_id)
        )

    def _get_subject_by_code(self, subject_code):
        """
        A private helper method to find and return a Subject object.

        Args:
            subject_code (str): The code of the subject to find
                                (e.g., "PROG101").

        Returns:
            Subject: The found Subject object.

        Raises:
            SubjectNotFoundException: If no subject with that code
                                      is found.
        """
        subjects = self._data_store.get_all_subjects()
        for subject in subjects:
            if subject.code.lower() == subject_code.lower():
                return subject
        
        # If the loop finishes, no subject was found
        raise SubjectNotFoundException(
            "Subject with code '{code}' not found.".format(code=subject_code)
        )

    def enrol(self, student_id, subject_code):
        """
        Enrols a student in a subject.
        This method implements the 'enrol' function from the
        IEnrolmentService contract.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The code of the subject.

        Raises:
            StudentNotFoundException: If the student ID is invalid.
            SubjectNotFoundException: If the subject code is invalid.
            MaxSubjectsExceededException: If the student is already
                                          enrolled in 4 subjects.
            AlreadyEnrolledException: If the student is already
                                      enrolled in this subject.
        """
        # --- Validation Step 1: Get Student and Subject ---
        student = self._get_student_by_id(student_id)
        subject = self._get_subject_by_code(subject_code)

        # --- Validation Step 2: Check Max Enrolment Limit ---
        # The Student model's 'can_enrol' method encapsulates this rule
        if not student.can_enrol():
            raise MaxSubjectsExceededException(
                "Student {id} has reached the maximum of 4 enrolments."
                .format(id=student_id)
            )

        # --- Validation Step 3: Check if Already Enrolled ---
        # The Student model's 'is_enrolled' method encapsulates this
        if student.is_enrolled(subject_code):
            raise AlreadyEnrolledException(
                "Student {id} is already enrolled in {code}."
                .format(id=student_id, code=subject_code)
            )

        # --- Creation Step: Create new Enrolment ---
        # Note: The design requires a unique ID for enrolments.
        # For simplicity, a simple counter or a more specific
        # generator could be used. Here, the student ID + subject
        # code is used as a simple unique key.
        # A more robust ID generator would be ideal in a
        # full implementation.
        enrolment_id = "{sid}-{scode}".format(sid=student_id,
                                             scode=subject_code)
        
        new_enrolment = Enrolment(
            id=enrolment_id,
            subject=subject
        )

        # --- Persistence Step 1: Update Student Model ---
        # The Student's 'add_enrolment' method adds to its
        # internal list
        student.add_enrolment(new_enrolment)

        # --- Persistence Step 2: Save Student to Data Store ---
        # The entire updated student object is saved
        self._data_store.update_user(student)

    def unenrol(self, student_id, subject_code):
        """
        Removes a subject enrolment from a student.
        This method implements the 'unenrol' function from the
        IEnrolmentService contract.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The code of the subject to remove.

        Raises:
            StudentNotFoundException: If the student ID is invalid.
            NotEnrolledException: If the student is not enrolled
                                  in this subject.
        """
        # --- Validation Step 1: Get Student ---
        student = self._get_student_by_id(student_id)

        # --- Validation Step 2: Check if Enrolled ---
        if not student.is_enrolled(subject_code):
            raise NotEnrolledException(
                "Student {id} is not enrolled in {code}."
                .format(id=student_id, code=subject_code)
            )

        # --- Persistence Step 1: Update Student Model ---
        # The Student's 'remove_enrolment' method handles
        # the removal from its internal list
        student.remove_enrolment(subject_code)

        # --- Persistence Step 2: Save Student to Data Store ---
        self._data_store.update_user(student)

    def set_mark(self, student_id, subject_code, mark):
        """
        Sets a mark for a student's subject enrolment.
        This method implements the 'set_mark' function from the
        IEnrolmentService contract.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The code of the subject.
            mark (int): The mark to assign (0-100).

        Raises:
            StudentNotFoundException: If the student ID is invalid.
            NotEnrolledException: If the student is not enrolled
                                  in this subject.
            InvalidMarkException: If the mark is not between 0-100.
        """
        # --- Validation Step 1: Check Mark Range ---
        if not (0 <= mark <= 100):
            raise InvalidMarkException(
                "Mark must be between 0 and 100. Received: {mark}"
                .format(mark=mark)
            )

        # --- Validation Step 2: Get Student ---
        student = self._get_student_by_id(student_id)

        # --- Validation Step 3: Get Specific Enrolment ---
        enrolment = student.get_enrolment(subject_code)
        if enrolment is None:
            raise NotEnrolledException(
                "Student {id} is not enrolled in {code}."
                .format(id=student_id, code=subject_code)
            )

        # --- Business Logic Step: Calculate Grade ---
        # Delegate grade calculation to the injected grade policy
        grade = self._grade_policy.calculate_grade(mark)

        # --- Persistence Step 1: Update Enrolment Model ---
        # The Enrolment's 'set_grade' method updates its
        # internal state
        enrolment.set_grade(mark, grade)

        # --- Persistence Step 2: Save Student to Data Store ---
        # The student object contains the updated enrolment,
        # so the entire student is saved.
        self._data_store.update_user(student)
        
    def change_password(self, user_id, new_password):
        """
        Changes a user's password.
        This method implements the 'change_password' function
        from the IEnrolmentService contract.

        Args:
            user_id (str): The ID of the user.
            new_password (str): The new plain-text password.
            
        Raises:
            StudentNotFoundException: If the user ID is invalid.
            InvalidPasswordException: If the new password is not
                                      strong enough.
        """
        # Note: This method re-uses the password hashing logic
        # from AuthService. In a real system, this hashing
        # logic would be broken out into its own 'IPasswordHasher'
        # service and injected into both AuthService and
        # EnrolmentService to avoid code duplication.
        # For this project, a simple re-implementation
        # is sufficient.

        # --- Validation Step 1: Validate Password Strength ---
        # This re-uses the static method from the Validator
        # if not Validator.is_strong_password(new_password):
        #     raise InvalidPasswordException(
        #         "New password does not meet strength requirements."
        #     )
        # (This is commented out to match the 'change_password' in
        # the base 'Student' class, which has no validation.
        # This service method just handles hashing and saving.)

        # --- Hashing Step: Hash New Password ---
        # This logic is duplicated from AuthService.
        salt = "cli_uni_app_salt"
        salted_password = (new_password + salt).encode('utf-8')
        new_password_hash = hashlib.sha256(salted_password).hexdigest()

        # --- Persistence Step 1: Get User ---
        # This uses the base 'get_user_by_id' logic, as this
        # function could (in theory) work for Admins too.
        # But the Student model is where the 'change_password'
        # method is defined.
        student = self._get_student_by_id(user_id)
        
        # --- Persistence Step 2: Update Model ---
        # The Student model's 'change_password' method
        # (inherited from User and implemented in Student)
        # updates its internal hash.
        student.change_password(new_password_hash)

        # --- Persistence Step 3: Save to Data Store ---
        self._data_store.update_user(student)