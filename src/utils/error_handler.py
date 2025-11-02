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

from typing import Optional, Callable, Any
from src.utils.exceptions import (
    DataPersistenceException,
    InvalidCredentialsException,
    UserNotFoundException,
    EmailAlreadyExistsException,
    InvalidEmailException,
    InvalidPasswordException,
    StudentNotFoundException,
    SubjectNotFoundException,
    AlreadyEnrolledException,
    MaxSubjectsExceededException,
    NotEnrolledException,
    InvalidMarkException
)


def handle_error(error: Exception, context: Optional[str] = None) -> str:
    error_type = type(error).__name__
    
    error_messages = {
        'DataPersistenceException': "A data storage error occurred. Please check file permissions.",
        'InvalidCredentialsException': "Invalid username or password. Please try again.",
        'UserNotFoundException': "User not found. Please check your user ID.",
        'EmailAlreadyExistsException': "This email address is already registered.",
        'InvalidEmailException': "Invalid email format. Please enter a valid email address.",
        'InvalidPasswordException': "Invalid password. Password must meet security requirements.",
        'StudentNotFoundException': "Student not found. Please check the student ID.",
        'SubjectNotFoundException': "Subject not found. Please check the subject code.",
        'AlreadyEnrolledException': "Student is already enrolled in this subject.",
        'MaxSubjectsExceededException': "Maximum number of enrolments reached (4 subjects).",
        'NotEnrolledException': "Student is not enrolled in this subject.",
        'InvalidMarkException': "Invalid mark. Mark must be between 0 and 100.",
        'ValueError': "Invalid input value. Please check your entry.",
        'TypeError': "Invalid input type. Please check your entry.",
        'KeyError': "Required data missing. Please check your input.",
        'IOError': "File operation failed. Please check file permissions.",
        'PermissionError': "Permission denied. Please check file access rights."
    }
    
    if error_type in error_messages:
        message = error_messages[error_type]
        if str(error):
            message += f" Details: {str(error)}"
    else:
        message = f"An unexpected error occurred: {str(error)}"
    
    if context:
        message = f"[{context}] {message}"
    
    return message


def safe_execute(func: Callable, *args, context: Optional[str] = None, 
                 error_callback: Optional[Callable[[Exception], Any]] = None, **kwargs) -> tuple[Any, Optional[str]]:
    try:
        result = func(*args, **kwargs)
        return (result, None)
    except Exception as e:
        if error_callback:
            return error_callback(e)
        
        error_message = handle_error(e, context)
        return (None, error_message)


def log_error(error: Exception, context: Optional[str] = None, 
              log_to_file: bool = False, log_file: str = "error.log") -> None:
    error_message = handle_error(error, context)
    timestamp = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = f"[{timestamp}] {error_message}\n"
    
    print(f"Error: {error_message}", file=sys.stderr)
    
    if log_to_file:
        try:
            with open(log_file, 'a') as f:
                f.write(log_entry)
        except IOError:
            print(f"Warning: Could not write to log file {log_file}", file=sys.stderr)


def validate_input(value: Any, validator: Callable[[Any], bool], 
                   error_message: str = "Invalid input") -> tuple[bool, Optional[str]]:
    try:
        if validator(value):
            return (True, None)
        else:
            return (False, error_message)
    except Exception as e:
        return (False, f"{error_message}: {str(e)}")
