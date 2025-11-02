"""
Contains the implementation of the IReportingService interface.

This service is responsible for aggregating and processing data
to generate reports for administrators.
"""

from src.services.interfaces import IReportingService, IDataStore, IGradePolicy
from src.models.student import Student
from src.models.enrolment import Grade

class ReportingService(IReportingService):
    """
    Implements the IReportingService for generating admin reports.
    
    Attributes:
        _data_store (IDataStore): A reference to the data store.
        _grade_policy (IGradePolicy): A reference to the grade policy logic.
    """
    def __init__(self, data_store: IDataStore, grade_policy: IGradePolicy):
        """
        Initializes the ReportingService.

        Args:
            data_store: An object implementing the IDataStore interface.
            grade_policy: An object implementing the IGradePolicy interface.
        """
        self._data_store = data_store
        self._grade_policy = grade_policy

    def _get_all_students(self) -> list[Student]:
        """Helper method to get only student users."""
        all_users = self._data_store.get_all_users()
        # Filter for Student instances
        return [user for user in all_users if isinstance(user, Student)]

    def get_pass_fail_partition(self) -> dict[str, list[Student]]:
        """
        Partitions all students into PASS and FAIL groups.
        A student is 'FAIL' if they have one or more 'FL' grades.
        A student is 'PASS' if they have no 'FL' grades.

        Returns:
            A dictionary: {'PASS': [Student, ...], 'FAIL': [Student, ...]}
        """
        students = self._get_all_students()
        partitions = {'PASS': [], 'FAIL': []}

        for student in students:
            has_failed = False
            for enrolment in student.get_enrolments():
                if enrolment.grade == Grade.F: # Check against the Grade Enum
                    has_failed = True
                    break
            
            if has_failed:
                partitions['FAIL'].append(student)
            else:
                partitions['PASS'].append(student)
        
        return partitions

    def get_grade_grouping(self) -> dict[str, list[Student]]:
        """
        Groups students by their average grade.
        
        Calculates the average numerical mark for each student and
        assigns them to a grade bracket (HD, D, C, P, F, N/A).

        Returns:
            A dictionary: {'HD': [Student, ...], 'D': [Student, ...], ...}
        """
        students = self._get_all_students()
        # Use Grade enum values for keys for consistency
        groups = {grade.name: [] for grade in Grade}
        # Add 'N/A' for students with no marks
        groups['N/A'] = []


        for student in students:
            marks = []
            for enrolment in student.get_enrolments():
                if enrolment.mark is not None:
                    marks.append(enrolment.mark)
            
            if not marks:
                # Student has no marks yet
                groups['N/A'].append(student)
            else:
                # Calculate average mark
                avg_mark = sum(marks) / len(marks)
                # Get the grade for that average
                grade_enum = self._grade_policy.get_grade_for_mark(avg_mark)
                
                # Use the grade's *name* (e.g., 'HD') as the key
                if grade_enum.name in groups:
                    groups[grade_enum.name].append(student)
                else:
                    # Fallback for any unexpected grade
                    groups['N/A'].append(student)
        
        # Filter out empty groups for a cleaner report
        final_groups = {key: val for key, val in groups.items() if val}
        return final_groups