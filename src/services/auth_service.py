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

import hashlib

from src.services.interfaces import IAuthService, IDataStore

# Import the model this service will create
from src.models.student import Student

# Import utility classes
from src.utils.id_generator import IdGenerator
from src.utils.validator import Validator

# Import custom exceptions
from src.utils.exceptions import (
    InvalidCredentialsException,
    UserNotFoundException,
    EmailAlreadyExistsException,
    InvalidEmailException,
    InvalidPasswordException
)

class AuthService(IAuthService):
    """
    Implements the IAuthService interface for user authentication.

    This class orchestrates multiple dependencies (IDataStore,
    IdGenerator, Validator) to perform its tasks. This is an
    example of the 'Service' layer in a multi-tier architecture.
    
    Attributes:
        _data_store (IDataStore): A reference to the data persistence
                                  layer.
        _id_generator (IdGenerator): A reference to the utility for
                                     creating new IDs.
    """

    def __init__(self, data_store, id_generator):
        """
        Initializes the AuthService.

        This constructor uses Dependency Injection. The specific
        implementations of 'data_store' and 'id_generator' are
        'injected' from the outside, decoupling this service
        from any concrete implementation.

        Args:
            data_store (IDataStore): An object that implements the
                                     IDataStore interface.
            id_generator (IdGenerator): An object of the IdGenerator
                                        class.
        """
        # Store the injected dependencies as private attributes
        self._data_store = data_store
        self._id_generator = id_generator

    def _hash_password(self, password):
        """
        Hashes a plain-text password using SHA-256.

        This is a private helper method. It also 'salts' the
        password before hashing for added security, although a
        fixed salt is used here for simplicity. In a real-world
        app, a unique salt per user would be generated and stored.

        Args:
            password (str): The plain-text password to hash.

        Returns:
            str: The hexadecimal string representation of the hash.
        """
        # A simple, fixed salt.
        salt = "cli_uni_app_salt"
        
        # Combine the salt and password, then encode to bytes
        salted_password = (password + salt).encode('utf-8')
        
        # Hash the salted password using SHA-256
        hash_object = hashlib.sha256(salted_password)
        
        # Return the hexadecimal representation of the hash
        return hash_object.hexdigest()

    def _verify_password(self, password, hashed_password):
        """
        Verifies a plain-text password against a stored hash.

        Args:
            password (str): The plain-text password from the user.
            hashed_password (str): The hash stored in the data store.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        # Hash the incoming password using the *exact same*
        # method (salting + hashing)
        incoming_hash = self._hash_password(password)
        
        # Compare the newly generated hash with the stored hash
        return incoming_hash == hashed_password

    def login(self, user_id, password):
        """
        Authenticates a user based on their ID and password.
        This method implements the 'login' function from the
        IAuthService contract.

        Args:
            user_id (str): The ID of the user trying to log in.
            password (str): The plain-text password to check.

        Returns:
            User: The authenticated User object (e.g., Student or Admin).

        Raises:
            UserNotFoundException: If the user ID does not exist.
            InvalidCredentialsException: If the password is incorrect.
        """
        # Use the injected data store to get all users
        users = self._data_store.get_all_users()
        
        # Find the user by their ID
        user_to_check = None
        for user in users:
            if user.id == user_id:
                user_to_check = user
                break
        
        # If no user was found with that ID, raise an exception
        if user_to_check is None:
            raise UserNotFoundException(
                "User with ID '{id}' not found.".format(id=user_id)
            )
        
        # If the user was found, verify their password
        if self._verify_password(password, user_to_check.password_hash):
            # If successful, return the entire User object
            return user_to_check
        else:
            # If passwords do not match, raise an exception
            raise InvalidCredentialsException("Invalid user ID or password.")

    def register_student(self, name, email, password):
        """
        Creates a new student account.
        This method implements the 'register_student' function
        from the IAuthService contract.

        Args:
            name (str): The student's full name.
            email (str): The student's email address.
            password (str): The student's plain-text password.

        Returns:
            Student: The newly created Student object.

        Raises:
            InvalidEmailException: If the email format is not valid.
            EmailAlreadyExistsException: If a user with this email
                                         is already registered.
            InvalidPasswordException: If the password is not strong enough.
        """
        # --- Validation Step 1: Validate Email Format ---
        # Use the Validator utility class
        if not Validator.is_valid_email(email):
            raise InvalidEmailException(
                "Email format is invalid: {email}".format(email=email)
            )

        # --- Validation Step 2: Check for Existing Email ---
        users = self._data_store.get_all_users()
        for user in users:
            if user.email.lower() == email.lower():
                raise EmailAlreadyExistsException(
                    "Email already in use: {email}".format(email=email)
                )

        # --- Validation Step 3: Validate Password Strength ---
        if not Validator.is_strong_password(password):
            raise InvalidPasswordException(
                "Password does not meet strength requirements."
            )

        # --- Creation Step 1: Generate New ID ---
        # Use the injected ID generator
        new_id = self._id_generator.generate_unique_id()

        # --- Creation Step 2: Hash Password ---
        new_password_hash = self._hash_password(password)

        # --- Creation Step 3: Create Student Object ---
        # Create a new instance of the Student model
        new_student = Student(
            id=new_id,
            name=name,
            email=email,
            password_hash=new_password_hash
        )

        # --- Persistence Step: Save New Student ---
        # Use the injected data store to add the new user
        self._data_store.add_user(new_student)

        # Return the new object to the caller
        return new_student