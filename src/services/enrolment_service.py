import random
import re
import sys
import os
from pathlib import Path
import hashlib

try:
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
except (NameError, AttributeError):
    cwd = Path(os.getcwd()).resolve()
    if str(cwd) not in sys.path:
        sys.path.insert(0, str(cwd))

from src.services.interfaces import (
    IEnrolmentService
)

# Import the models this service will interact with
from src.models.student import Student
from src.models.enrolment import Enrolment

# Import custom exceptions
from src.utils.exceptions import (
    StudentNotFoundException,
    SubjectNotFoundException,
    AlreadyEnrolledException,
    MaxSubjectsExceededException,
    NotEnrolledException,
    InvalidMarkException
)

# Password policy (spec): start uppercase + ≥5 letters + ≥3 digits
_PWD_RULE = r"^[A-Z][A-Za-z]{4,}\d{3,}$"
_SALT = "cli_uni_app_salt"

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
            # Subject.id is actually the code (e.g., 'ICT101')
            if subject.id.lower() == subject_code.lower():
                return subject
        
        # If the loop finishes, no subject was found
        raise SubjectNotFoundException(
            "Subject with code '{code}' not found.".format(code=subject_code)
        )
    
    def list_available_subjects(self, student_id):
        """
        Return Subject objects the student is NOT yet enrolled in.
        """
        student = self._get_student_by_id(student_id)
        all_subs = self._data_store.get_all_subjects() or []
        enrolled = {e.subject.id for e in getattr(student, "enrolments", [])}
        return [s for s in all_subs if getattr(s, "id", None) not in enrolled]


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

        # --- Validation Step 2: Check Max 4 subject Enrolment Limit ---
        if len(student.enrolments) >= Student.MAX_ENROLMENTS:
            raise MaxSubjectsExceededException(
                "Student {id} has reached the maximum of 4 enrolments."
                .format(id=student_id)
            )

        # --- Validation Step 3: Check if Already Enrolled ---
        for enrolment in student.enrolments:
            if enrolment.subject.id.lower() == subject_code.lower():
                raise AlreadyEnrolledException(
                    "Student {id} is already enrolled in {code}."
                    .format(id=student_id, code=subject_code)
                )

        # --- Step 4: Create new Enrolment ID ---
        enrolment_id = f"{student_id}-{subject_code}"
        
        # --- Step 5: Assign random mark and grade ---
        mark = random.randint(25,100)
        grade = self._grade_policy.get_grade_for_mark(mark)
        
        new_enrolment = Enrolment(
            id=enrolment_id,          # keep whatever you already assign
            subject=subject,          # Subject object you found by code
            mark=mark,
            grade=grade

        )

        # --- Persistence Step 1: Update Student Model ---
        # Use the Student's enrol method
        student.enrol(new_enrolment)

        # --- Persistence Step 2: Save Student to Data Store ---
        # The entire updated student object is saved
        self._data_store.update_user(student)
        
        # Return the new enrolment as required by interface
        return new_enrolment

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
        enrolled = False
        for enrolment in student.enrolments:
            if enrolment.subject.id.lower() == subject_code.lower():
                enrolled = True
                break
        
        if not enrolled:
            raise NotEnrolledException(
                "Student {id} is not enrolled in {code}."
                .format(id=student_id, code=subject_code)
            )

        # --- Persistence Step 1: Update Student Model ---
        # Use the Student's drop_subject method
        student.drop_subject(subject_code)

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

        # --- Hashing Step: Hash New Password ---
        if not re.match(_PWD_RULE, new_password):
            raise ValueError(
                "Password must start uppercase, have ≥5 letters, then ≥3 digits (e.g., Abcde123)."
            )

        salted = (new_password + _SALT).encode("utf-8")
        new_hash = hashlib.sha256(salted).hexdigest()

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
        student.change_password(new_hash)

        # --- Persistence Step 3: Save to Data Store ---
        self._data_store.update_user(student)
    
    # --- Interface Method Implementations ---
    # These methods implement the abstract methods from IEnrolmentService
    # using the existing methods but with different parameter names to match the interface
    
    def enrol_student_in_subject(self, student_id, subject_id):
        """
        Implements the abstract method from IEnrolmentService.
        This is an alias for enrol() that uses subject_id instead of subject_code.
        """
        return self.enrol(student_id, subject_id)
    
    def withdraw_student_from_subject(self, student_id, subject_id):
        """
        Implements the abstract method from IEnrolmentService.
        This is an alias for unenrol() that uses subject_id instead of subject_code.
        """
        self.unenrol(student_id, subject_id)
    
    def set_mark_for_enrolment(self, student_id, subject_id, mark):
        """
        Implements the abstract method from IEnrolmentService.
        This is an alias for set_mark() that uses subject_id instead of subject_code.
        """
        self.set_mark(student_id, subject_id, mark)