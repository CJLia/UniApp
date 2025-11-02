"""
Contains the implementation of the IReportingService interface.

This service is responsible for aggregating and processing data
to generate reports for administrators.
"""

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

from src.services.interfaces import IReportingService

# Import models
from src.models.student import Student
from src.models.enrolment import Grade

# Import exceptions
from src.utils.exceptions import StudentNotFoundException


class ReportingService(IReportingService):
    """
    Implements the IReportingService interface.
    
    This service provides reporting functionality for student data,
    including grouping and partitioning operations.
    
    Attributes:
        _data_store (IDataStore): A reference to the data store.
    """
    
    def __init__(self, data_store):
        """
        Initializes the ReportingService.
        
        Args:
            data_store (IDataStore): An object that implements IDataStore.
        """
        self._data_store = data_store
    
    def _get_all_students(self):
        """Helper method to get only student users."""
        all_users = self._data_store.get_all_users()
        # Filter for Student instances
        return [user for user in all_users if isinstance(user, Student)]
    
    def get_student_enrolments(self, student_id):
        """
        Gets a detailed list of a single student's enrolments.
        
        Args:
            student_id (str): The ID of the student.
            
        Returns:
            list: A list of Enrolment objects for the student.
            
        Raises:
            StudentNotFoundException: If the student ID is not found.
        """
        users = self._data_store.get_all_users()
        
        for user in users:
            if isinstance(user, Student) and user.id == student_id:
                return user.get_enrolments()
        
        raise StudentNotFoundException(
            f"Student with ID '{student_id}' not found."
        )
    
    def get_pass_fail_partition(self):
        """
        Partitions all students into two groups: PASS and FAIL.
        A student is in FAIL if they have failed one or more subjects.
        A student is in PASS if they have no failed subjects.
        
        Returns:
            dict: A dictionary with 'PASS' and 'FAIL' keys,
                  each containing a list of Student objects.
        """
        students = self._get_all_students()
        partitions = {'PASS': [], 'FAIL': []}
        
        for student in students:
            has_failed = False
            
            # Check if student has any failed subjects
            for enrolment in student.get_enrolments():
                # Check by grade (Grade.F represents Fail)
                if enrolment.grade == Grade.F:
                    has_failed = True
                    break
                # Also check by mark if grade is not set but mark is
                elif enrolment.mark is not None and enrolment.mark < 50:
                    has_failed = True
                    break
            
            if has_failed:
                partitions['FAIL'].append(student)
            else:
                partitions['PASS'].append(student)
        
        return partitions
    
    def get_grade_grouping(self):
        """
        Groups all students based on their average grade.
        
        Students are grouped by their overall average grade:
        - HD: Average >= 85
        - DN: Average >= 75 and < 85
        - CR: Average >= 65 and < 75
        - PS: Average >= 50 and < 65
        - F: Average < 50 or no marks
        
        Returns:
            dict: A dictionary with grade names as keys,
                  each containing a list of Student objects.
        """
        students = self._get_all_students()
        
        groups = {
            'HD': [],
            'DN': [],
            'CR': [],
            'PS': [],
            'F': []
        }
        
        for student in students:
            # Calculate average mark
            enrolments = student.get_enrolments()
            marks = [e.mark for e in enrolments if e.mark is not None]
            
            if not marks:
                # No marks available, default to F
                groups['F'].append(student)
            else:
                average = sum(marks) / len(marks)
                
                # Determine grade group based on average
                if average >= 85:
                    groups['HD'].append(student)
                elif average >= 75:
                    groups['DN'].append(student)
                elif average >= 65:
                    groups['CR'].append(student)
                elif average >= 50:
                    groups['PS'].append(student)
                else:
                    groups['F'].append(student)
        
        return groups
    
    def get_all_students(self):
        """
        Gets a list of all registered students.
        
        Returns:
            list: A list of Student objects.
        """
        return self._get_all_students()
