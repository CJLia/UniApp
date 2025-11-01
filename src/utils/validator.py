"""
A utility class for performing common data validation tasks.

This class uses static methods, which are methods that belong
to the class itself rather than an instance of the class.
This is a good practice for utility functions that don't
need to store any internal state (i.e., they don't need 'self').
"""

# Import the 're' module for regular expression operations
import re

class Validator:
    """
    Provides static methods for validating various data formats,
    such as emails and passwords.
    """

    @staticmethod
    def is_valid_email(email):
        """
        Checks if a given string is a valid email format.

        This method uses a regular expression (regex) to check if the
        email string conforms to a standard email structure.

        Args:
            email (str): The email string to validate.

        Returns:
            bool: True if the email format is valid, False otherwise.
        """
        # A standard regular expression pattern for basic email validation
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        # The re.match() function checks if the pattern matches at the
        # beginning of the string.
        # Also check if 'email' is not None or an empty string first.
        if email and re.match(pattern, email):
            return True
        else:
            return False

    @staticmethod
    def is_strong_password(password):
        """
        Checks if a given password meets minimum strength requirements.

        Password strength is a critical rule. Here, 'strong' is defined as:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit

        Args:
            password (str): The password string to check.

        Returns:
            bool: True if the password meets all criteria, False otherwise.
        """
        # The password must be checked if it is a string first.
        if not password or not isinstance(password, str):
            return False
            
        # Example rules: At least 8 characters
        if len(password) < 8:
            return False
        
        # Contains at least one uppercase letter (A-Z)
        if not re.search(r"[A-Z]", password):
            return False
            
        # Contains at least one lowercase letter (a-z)
        if not re.search(r"[a-z]", password):
            return False
            
        # Contains at least one digit (0-9)
        if not re.search(r"[0-9]", password):
            return False
        
        # If all checks pass, the password is strong
        return True
