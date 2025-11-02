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

# --- ADDED TO FIX IMPORT ERROR ---
class DataPersistenceException(Exception):
    """
    Base class for exceptions raised during data loading or saving.
    This fixes the ImportError in data_store.py
    """
    pass

# --- ADDED FROM YOUR REPO'S auth_service.py ---
class EmailAlreadyExistsException(DuplicateDataException):
    """
    Raised when a user tries to register with an email that
    is already in use.
    """
    pass

class InvalidEmailException(ValidationException):
    """
    Raised when the email format is invalid.
    """
    pass

class InvalidPasswordException(ValidationException):
    """
    Raised when the password does not meet strength requirements.
    """
    pass

# --- ADDED FROM YOUR REPO'S enrolment_service.py ---
class StudentNotFoundException(UserNotFoundException):
    """
    Raised when a student ID is not found.
    """
    pass

class SubjectNotFoundException(Exception):
    """
    Raised when a subject code is not found.
    """
    pass

class AlreadyEnrolledException(EnrolmentException):
    """
    Raised when a student is already enrolled in a subject.
    """
    pass

class NotEnrolledException(EnrolmentException):
    """
    Raised when attempting to modify an enrolment that doesn't exist.
    """
    pass

class InvalidMarkException(ValidationException):
    """
    Raised when a mark is outside the valid range (e.g., 0-100).
    """
    pass
