"""
Contains the Student class, which is a concrete implementation of the 
abstract User class.
"""

# Import the parent class User and other required models/exceptions
from .user import User
from .enrolment import Enrolment, Grade
from .subject import Subject
from ..utils.exceptions import MaxSubjectsExceededException, EnrolmentException

class Student(User):
    """
    Represents a Student user in the system.
    
    This class demonstrates Inheritance, as it 'is-a' User and inherits
    all the attributes (id, name, email, etc.) and methods from the
    User class. It then extends this functionality with attributes and
    methods specific to a Student, such as managing enrolments.
    """

    # Class constant.
    # This is a good OOP practice as it's easily configurable and
    # makes the code's intent clearer than a 'magic number'.
    MAX_ENROLMENTS = 4

    def __init__(self, id, name, email, password_hash):
        """
        Initialises a new Student object.
        
        It calls the parent class's (User) constructor using 'super()'
        to handle the common attributes.
        
        Args:
            id (str): The student's unique ID (e.g., 's12345').
            name (str): The full name of the student.
            email (str): The student's email address.
            password_hash (str): The hashed password for the student.
        """
        # Call the __init__ method of the parent class (User)
        # This is a fundamental part of Inheritance, ensuring the
        # parent object is initialised correctly.
        super().__init__(id, name, email, password_hash)
        
        # This attribute is specific to the Student class.
        # It holds a list of Enrolment objects, demonstrating
        # 'Composition' (a Student 'has-a' list of Enrolments).
        self.enrolments = []

    def change_password(self, new_password_hash):
        """
        Updates the student's password hash.
        
        This method is the concrete implementation of the abstract
        'change_password' method defined in the User base class.
        This is a requirement of the Inheritance contract.
        
        Args:
            new_password_hash (str): The new hashed password.
        
        Returns:
            None
        """
        self.password_hash = new_password_hash

    def enrol(self, enrolment):
        """
        Adds a new enrolment to the student's list of enrolments.
        
        It also enforces the business rule that a student cannot be
        enrolled in more than MAX_ENROLMENTS.
        
        Args:
            enrolment (Enrolment): The Enrolment object to be added.
            
        Raises:
            MaxSubjectsExceededException: If the student is already
                                         enrolled in the maximum
                                         number of subjects.
            EnrolmentException: If the student is already enrolled
                                in this specific subject.
                                
        Returns:
            None
        """
        # Rule 1: Check if student is already at max enrolments.
        if len(self.enrolments) >= self.MAX_ENROLMENTS:
            raise MaxSubjectsExceededException(
                f"Cannot enrol. Student {self.id} has reached the "
                f"maximum of {self.MAX_ENROLMENTS} subjects."
            )
            
        # Rule 2: Check if student is already enrolled in this subject.
        # This loop demonstrates iterating over the composite objects.
        for existing_enrolment in self.enrolments:
            if existing_enrolment.subject.id == enrolment.subject.id:
                raise EnrolmentException(
                    f"Student {self.id} is already enrolled in "
                    f"subject {enrolment.subject.id}."
                )
                
        # If all checks pass, add the enrolment to the list.
        self.enrolments.append(enrolment)

    def drop_subject(self, subject_id):
        """
        Removes an enrolment from the student's list by subject ID.
        
        Args:
            subject_id (str): The ID of the subject to drop.
            
        Raises:
            EnrolmentException: If the student is not enrolled in
                                 the specified subject.
                                 
        Returns:
            None
        """
        # Find the enrolment object to remove.
        enrolment_to_remove = None
        for enrolment in self.enrolments:
            if enrolment.subject.id == subject_id:
                enrolment_to_remove = enrolment
                break # Exit loop once found

        # If we found the enrolment, remove it.
        if enrolment_to_remove:
            self.enrolments.remove(enrolment_to_remove)
        else:
            # If the loop finishes and we didn't find the subject.
            raise EnrolmentException(
                f"Student {self.id} is not enrolled in "
                f"subject {subject_id}."
            )

    def get_enrolments(self):
        """
        An 'accessor' (or 'getter') method that returns the list
        of enrolments.
        
        This is part of Encapsulation, providing read-only access
        to the internal 'enrolments' list without allowing direct
        modification from outside the class (unless the caller
        mutates the returned list, which is why services are used
        to manage this).
        
        Returns:
            list: A list of Enrolment objects.
        """
        return self.enrolments
    
    def get_enrolment(self, subject_code):
        """
        Returns the specific Enrolment object for a given subject code.

        Args:
            subject_code (str): The ID/code of the subject (e.g., '101')

        Returns:
            Enrolment | None: The matching Enrolment object, or None if not found.
        """
        for enrolment in self.enrolments:
            if enrolment.subject.id.lower() == subject_code.lower():
                return enrolment
        return None

    def __repr__(self):
        """
        Provides a detailed string representation of the Student object.
        
        Returns:
            str: A string showing the student's key attributes.
        """
        # Calls super().__repr__() to get the parent's representation
        # but this is less common. We'll create a full one here
        # for clarity.
        return (f"Student(id='{self.id}', "
                f"name='{self.name}', "
                f"email='{self.email}', "
                f"enrolments={len(self.enrolments)})")