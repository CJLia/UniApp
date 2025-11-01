"""
This file defines the grading policy for the university.

It implements the IGradePolicy interface, ensuring that the
application's business logic for grading is separated from other
services. This is a good example of the 'Strategy' design pattern,
where the specific algorithm (how to grade) can be swapped out.
"""

# Import the interface being implemented
from src.services.interfaces import IGradePolicy
# Import the Grade enum from the models
from src.models.enrolment import Grade

# A concrete class 'DefaultGradePolicy' is created that
# inherits from the abstract 'IGradePolicy'
class DefaultGradePolicy(IGradePolicy):
    """
    Implements the default grading policy for the university.

    This class provides concrete implementations for the abstract
    methods defined in the IGradePolicy interface.
    """

    def get_grade_for_mark(self, mark):
        """
        Calculates and returns the Grade enum corresponding to a
        numerical mark.

        This method contains the core business logic for grading.
        It handles invalid marks by returning a specific 'INVALID'
        grade, which is cleaner than raising an exception here.

        Args:
            mark (int): The numerical mark, expected to be between 0-100.

        Returns:
            Grade: The corresponding Grade enum (e.g., Grade.HD, Grade.DN).
                   Returns Grade.INVALID if the mark is not valid.
        """
        # First, handle the case of a 'None' or non-integer mark
        if mark is None or not isinstance(mark, (int, float)):
            return Grade.INVALID
        
        # This 'if/elif/else' chain implements the grading scale
        if mark >= 85:
            return Grade.HD
        elif mark >= 75:
            return Grade.DN
        elif mark >= 65:
            return Grade.CR
        elif mark >= 50:
            return Grade.PS
        elif mark >= 0:
            # Any mark from 0-49 is considered a Fail
            return Grade.FL
        else:
            # Any negative mark is also invalid
            return Grade.INVALID

    def is_pass_mark(self, mark):
        """
        Determines if a numerical mark is a passing mark.

        This is a helper method that relies on the get_grade_for_mark
        logic to avoid duplicating the grading rules.

        Args:
            mark (int): The numerical mark.

        Returns:
            bool: True if the mark results in a passing grade, False otherwise.
        """
        # Get the grade for the mark
        grade = self.get_grade_for_mark(mark)
        
        # Check if the grade is one of the 'passing' grades.
        # This is a clean way to check for multiple conditions.
        passing_grades = [Grade.HD, Grade.DN, Grade.CR, Grade.PS]
        
        if grade in passing_grades:
            return True
        else:
            return False