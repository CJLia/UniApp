"""
Contains the Enrolment class and Grade enum, modelling the link
between a Student and a Subject.
"""

from enum import Enum
from .subject import Subject

class Grade(Enum):
    """
    An Enumeration (Enum) to represent the possible grades a student
    can achieve.
    
    Using an Enum is a powerful OOP technique to ensure type safety 
    and prevent invalid grade values. It restricts the 'grade' 
    attribute to a predefined set of constants, making the code 
    more robust and readable.
    """
    HD = "High Distinction"
    D = "Distinction"
    C = "Credit"
    P = "Pass"
    F = "Fail"
    NONE = "N/A" # Represents a subject that is enrolled but not yet graded

class Enrolment:
    """
    Represents a student's enrolment in a single subject.
    
    This class is a key part of the 'Domain Model' from the design schema. It
    acts as an 'association class', linking a Student (which will be
    added later) to a Subject and storing the data related to that 
    specific link, such as the mark and grade.
    
    This design correctly separates the 'Subject' (the general course)
    from the 'Enrolment' (a specific student's instance of that course),
    which is a more advanced and correct design than storing marks
    inside the Subject class.
    """

    def __init__(self, id, subject, mark=None, grade=None):
        """
        Initialises a new Enrolment object.
        
        The mark and grade are optional (default to None) because a
        student can be enrolled in a subject before they have 
        received a grade.
        
        Args:
            id (str): The unique ID for this specific enrolment.
            subject (Subject): An instance of the Subject class. This
                               demonstrates 'Composition' or 
                               'Aggregation' from OOP, as the Enrolment
                               'has-a' Subject.
            mark (int, optional): The numerical mark (e.g., 75). Defaults to None.
            grade (Grade, optional): The calculated grade (e.g., Grade.C). Defaults to None.
        """
        self.id = id
        self.subject = subject # Stores the actual Subject object
        self.mark = mark
        
        # If no grade is provided, default to Grade.NONE.
        # This prevents the attribute from being uninitialised.
        self.grade = grade if grade is not None else Grade.NONE

    def set_grade(self, mark, grade):
        """
        Sets or updates the mark and grade for this enrolment.
        
        This method is a 'mutator' (or 'setter'), which provides
        a controlled way to modify the object's internal state.
        In our design, this method will be called by the 
        'EnrolmentService' after the grade has been calculated
        by the 'IGradePolicy'.
        
        Args:
            mark (int): The numerical mark.
            grade (Grade): The corresponding Grade enum value.
            
        Returns:
            None
        """
        self.mark = mark
        self.grade = grade

    def __repr__(self):
        """
        Provides a detailed string representation of the Enrolment object.
        
        Returns:
            str: A string showing the enrolment's key attributes.
        """
        # Accesses the associated subject's name using self.subject.name
        return (f"Enrolment(id='{self.id}', "
                f"subject='{self.subject.name}', "
                f"mark={self.mark}, grade='{self.grade.value}')")