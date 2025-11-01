"""
Contains all custom exceptions used throughout the application.

Defining custom exceptions is a core part of robust software design.
It allows the program to 'throw' specific, named errors when
something goes wrong (e.g., 'InvalidCredentialsException') instead
of using a generic error (like 'ValueError').

This allows the higher-level code (like the UI) to 'catch' these
specific exceptions and show a user-friendly error message.

The 'pass' keyword means the class is empty; it inherits all its
behaviour from the parent 'Exception' class.
"""

# Base exception for all enrolment-related errors
class EnrolmentException(Exception):
    """Base class for exceptions raised during the enrolment process."""
    pass

# Specific enrolment error
class MaxSubjectsExceededException(EnrolmentException):
    """
    Raised when a student attempts to enrol in more than the
    allowed maximum number of subjects.
    """
    pass

# Base exception for all authentication-related errors
class AuthenticationException(Exception):
    """Base class for exceptions raised during authentication."""
    pass

# Specific authentication errors
class InvalidCredentialsException(AuthenticationException):
    """
    Raised when a user provides an incorrect ID or password.
    """
    pass

class UserNotFoundException(AuthenticationException):
    """
    Raised when a user ID cannot be found in the data store.
    """
    pass

# Base exception for all data validation errors
class ValidationException(Exception):
    """
    Base class for exceptions raised during data validation.
    e.g., invalid email format, weak password.
    """
    pass

# General data store or business rule exception
class DuplicateDataException(Exception):
    """
    Raised when attempting to add data that already exists.
    e.g., registering a user with an email that is already in use.
    """
    pass
