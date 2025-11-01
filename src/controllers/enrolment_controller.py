"""
This file contains the Enrolment Controller class.

The controller acts as an intermediary between the View layer
(e.g., CLI or GUI) and the Service layer (e.g., EnrolmentService).
It handles user input from the view, calls the appropriate
service, and returns the result (or error) back to the view.
"""

# Import the service interface it depends on
from src.services.interfaces import IEnrolmentService

# Import custom exceptions that it needs to catch
from src.utils.exceptions import (
    StudentNotFoundException,
    SubjectNotFoundException,
    AlreadyEnrolledException,
    MaxSubjectsExceededException,
    NotEnrolledException,
    InvalidMarkException,
    InvalidPasswordException
)

class EnrolmentController:
    """
    Handles enrolment-related requests from the view.

    This class is 'injected' with an IEnrolmentService implementation,
    decoupling it from the concrete service logic.
    
    Attributes:
        _enrolment_service (IEnrolmentService): A reference to the
                                                enrolment service.
    """

    def __init__(self, enrolment_service):
        """
        Initializes the EnrolmentController.

        This constructor uses Dependency Injection. The specific
        implementation of 'enrolment_service' is 'injected' from
        the outside (e.g., from cli_app.py).

        Args:
            enrolment_service (IEnrolmentService): An object that
                                  implements the IEnrolmentService
                                  interface.
        """
        self._enrolment_service = enrolment_service

    def enrol_student(self, student_id, subject_code):
        """
        Attempts to enrol a student in a subject.

        It calls the EnrolmentService and catches potential
        errors, returning a (success, error) tuple.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The code of the subject.

        Returns:
            tuple: A tuple containing (True, None) on success,
                   or (False, error_message) on failure.
        """
        try:
            # Delegate the actual logic to the service layer
            self._enrolment_service.enrol(student_id, subject_code)
            
            # On success, return True and no error
            return (True, None)
            
        except (StudentNotFoundException,
                SubjectNotFoundException,
                AlreadyEnrolledException,
                MaxSubjectsExceededException) as e:
            # If the service raises a known enrolment error,
            # catch it and return the error message.
            return (False, str(e))
        except Exception as e:
            # Catch any other unexpected errors
            return (False, "An unexpected error occurred: {err}".format(err=e))

    def unenrol_student(self, student_id, subject_code):
        """
        Attempts to unenrol a student from a subject.

        It calls the EnrolmentService and catches potential
        errors, returning a (success, error) tuple.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The code of the subject.

        Returns:
            tuple: A tuple containing (True, None) on success,
                   or (False, error_message) on failure.
        """
        try:
            # Delegate the actual logic to the service layer
            self._enrolment_service.unenrol(student_id, subject_code)
            
            # On success, return True and no error
            return (True, None)
            
        except (StudentNotFoundException, NotEnrolledException) as e:
            # Catch known errors
            return (False, str(e))
        except Exception as e:
            # Catch any other unexpected errors
            return (False, "An unexpected error occurred: {err}".format(err=e))

    def set_student_mark(self, student_id, subject_code, mark):
        """
        Attempts to set a mark for a student's enrolment.

        It calls the EnrolmentService and catches potential
        errors, returning a (success, error) tuple.

        Args:
            student_id (str): The ID of the student.
            subject_code (str): The code of the subject.
            mark (int): The mark to set.

        Returns:
            tuple: A tuple containing (True, None) on success,
                   or (False, error_message) on failure.
        """
        try:
            # Delegate the actual logic to the service layer
            self._enrolment_service.set_mark(student_id,
                                             subject_code,
                                             mark)
            
            # On success, return True and no error
            return (True, None)
            
        except (StudentNotFoundException,
                NotEnrolledException,
                InvalidMarkException) as e:
            # Catch known errors
            return (False, str(e))
        except Exception as e:
            # Catch any other unexpected errors
            return (False, "An unexpected error occurred: {err}".format(err=e))

    def change_student_password(self, student_id, new_password):
        """
        Attempts to change a student's password.

        It calls the EnrolmentService and catches potential
        errors, returning a (success, error) tuple.

        Args:
            student_id (str): The ID of the student.
            new_password (str): The new plain-text password.

        Returns:
            tuple: A tuple containing (True, None) on success,
                   or (False, error_message) on failure.
        """
        try:
            # Delegate the actual logic to the service layer
            self._enrolment_service.change_password(student_id,
                                                    new_password)
            
            # On success, return True and no error
            return (True, None)
            
        except (StudentNotFoundException, InvalidPasswordException) as e:
            # Catch known errors
            return (False, str(e))
        except Exception as e:
            # Catch any other unexpected errors
            return (False, "An unexpected error occurred: {err}".format(err=e))
