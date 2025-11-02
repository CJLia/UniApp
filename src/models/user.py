"""
Contains the abstract base class for all user types in the system.
"""

from abc import ABC, abstractmethod

class User(ABC):
    """
    An abstract base class representing a generic user in the university system.
    
    This class establishes a common interface (contract) for all user types,
    such as Student and Admin, ensuring they all have core attributes 
    and functionalities. This use of an ABC is a key part of the system's
    polymorphic design, as specified in the design report.
    """

    def __init__(self, id, name, email, password_hash):
        """
        Initialises the base attributes for a User. This constructor is
        intended to be called by subclasses.
        
        Args:
            id (str): The user's unique identifier (e.g., '000001').
            name (str): The user's full name.
            email (str): The user's email address (e.g., 'name@university.com').
            password_hash (str): The securely hashed representation of the user's password.
        """
        # These attributes are defined as public, matching the FSD's
        # UML class diagram conventions.
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

    @abstractmethod
    def change_password(self, new_password_hash):
        """
        An abstract method to change the user's password.
        
        Subclasses (like Student) MUST implement this method, providing
        their own logic for updating the password. This enforces the
        Liskov Substitution Principle, as any object treated as a 'User'
        can be expected to have this method.
        
        Args:
            new_password_hash (str): The new, already-hashed password to be set.
            
        Returns:
            None
        """
        # A pass statement is used in an abstract method to indicate
        # that it has no implementation in the base class.
        pass

    def __repr__(self):
        """
        Provides an unambiguous string representation of the User object.
        
        This is primarily used for debugging and logging purposes, allowing
        developers to see the state of a User object.
        
        Returns:
            str: A string in the format ClassName(id='...', name='...').
        """
        # Uses self.__class__.__name__ to dynamically get the name of
        # the subclass (e.g., 'Student' or 'Admin')
        return f"{self.__class__.__name__}(id='{self.id}', name='{self.name}', email='{self.email}')"
