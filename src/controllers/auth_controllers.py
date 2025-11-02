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

from src.services.interfaces import IAuthService

# Import custom exceptions that it needs to catch
from src.utils.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
    EmailAlreadyExistsException,
    InvalidEmailException,
    InvalidPasswordException
)

class AuthController:
    """
    Handles authentication-related requests from the view.

    This class is 'injected' with an IAuthService implementation,
    decoupling it from the concrete service logic. This follows
    the Dependency Inversion Principle.
    
    Attributes:
        _auth_service (IAuthService): A reference to the authentication
                                      service.
    """

    def __init__(self, auth_service):
        """
        Initializes the AuthController.

        This constructor uses Dependency Injection. The specific
        implementation of 'auth_service' is 'injected' from
        the outside (e.g., from cli_app.py).

        Args:
            auth_service (IAuthService): An object that implements the
                                         IAuthService interface.
        """
        self._auth_service = auth_service

    def login(self, user_id, password):
        """
        Attempts to log in a user.

        It calls the AuthService and catches potential authentication
        errors, returning them as a (result, error) tuple.
        The view layer will then be responsible for displaying the
        error message.

        Args:
            user_id (str): The user ID to log in.
            password (str): The plain-text password.

        Returns:
            tuple: A tuple containing (user_object, None) on success,
                   or (None, error_message) on failure.
        """
        try:
            # Delegate the actual logic to the service layer
            user = self._auth_service.login(user_id, password)
            
            # On success, return the user object and no error
            return (user, None)
            
        except (InvalidCredentialsException, UserNotFoundException) as e:
            # If the service raises a known login error,
            # catch it and return the error message.
            return (None, str(e))
        except Exception as e:
            # Catch any other unexpected errors
            return (None, "An unexpected error occurred: {err}".format(err=e))

    def register_student(self, name, email, password):
        """
        Attempts to register a new student.

        It calls the AuthService and catches potential registration
        errors, returning them as a (result, error) tuple.

        Args:
            name (str): The student's full name.
            email (str): The student's email.
            password (str): The student's plain-text password.

        Returns:
            tuple: A tuple containing (student_object, None) on success,
                   or (None, error_message) on failure.
        """
        try:
            # Delegate the registration logic to the service layer
            new_student = self._auth_service.register_student(
                name, email, password
            )
            
            # On success, return the new student object
            return (new_student, None)
            
        except (EmailAlreadyExistsException,
                InvalidEmailException,
                InvalidPasswordException) as e:
            # If the service raises a known registration error,
            # catch it and return the error message.
            return (None, str(e))
        except Exception as e:
            # Catch any other unexpected errors
            return (None, "An unexpected error occurred: {err}".format(err=e))