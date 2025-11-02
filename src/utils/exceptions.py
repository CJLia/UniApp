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

# Data persistence exceptions
class DataPersistenceException(Exception):
    """
    Raised when an error occurs during file I/O operations
    (e.g., reading from or writing to a data file).
    """
    pass

# Specific validation errors
class EmailAlreadyExistsException(ValidationException):
    """
    Raised when attempting to register with an email that already exists.
    """
    pass

class InvalidEmailException(ValidationException):
    """
    Raised when an email format is invalid.
    """
    pass

class InvalidPasswordException(ValidationException):
    """
    Raised when a password does not meet the required strength criteria.
    """
    pass

# Student and subject related exceptions
class StudentNotFoundException(EnrolmentException):
    """
    Raised when a student ID cannot be found in the data store.
    """
    pass

class SubjectNotFoundException(EnrolmentException):
    """
    Raised when a subject code cannot be found in the data store.
    """
    pass

class AlreadyEnrolledException(EnrolmentException):
    """
    Raised when a student attempts to enrol in a subject they are already enrolled in.
    """
    pass

class NotEnrolledException(EnrolmentException):
    """
    Raised when a student attempts to perform an operation on a subject
    they are not enrolled in.
    """
    pass

class InvalidMarkException(EnrolmentException):
    """
    Raised when a mark is outside the valid range (typically 0-100).
    """
    pass
