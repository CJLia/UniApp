"""
Contains the Admin class, which is another concrete implementation 
of the abstract User class.
"""

# Import the parent class User
from .user import User

class Admin(User):
    """
    Represents an Administrator user in the system.
    
    Like Student, this class demonstrates Inheritance by extending
    the User class. It represents an 'Admin' user type which 'is-a' User.
    """

    def __init__(self, id, name, email, password_hash):
        """
        Initialises a new Admin object.
        
        It calls the parent class's (User) constructor using 'super()'
        to handle the common attributes.
        
        Args:
            id (str): The admin's unique ID (e.g., 'a1').
            name (str): The full name of the admin.
            email (str): The admin's email address.
            password_hash (str): The hashed password for the admin.
        """
        # Call the __init__ method of the parent class (User)
        # to set up the id, name, email, and password_hash.
        super().__init__(id, name, email, password_hash)

    def change_password(self, new_password_hash):
        """
        Updates the admin's password hash.
        
        This is the Admin's concrete implementation of the abstract
        'change_password' method from the User base class.
        
        Args:
            new_password_hash (str): The new hashed password.
        
        Returns:
            None
        """
        # This implementation is simple, but it could be different
        # from the Student's (e.g., it might log an audit event),
        # which is an example of Polymorphism.
        self.password_hash = new_password_hash

    def __repr__(self):
        """
        Provides a detailed string representation of the Admin object.
        
        Returns:
            str: A string showing the admin's key attributes.
        """
        return (f"Admin(id='{self.id}', "
                f"name='{self.name}', "
                f"email='{self.email}')")
