"""
Implements the IReportingService interface for generating
administrative reports such as Pass/Fail partitions and
Grade groupings for students.
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

from src.services.interfaces import IReportingService, IDataStore, IGradePolicy
from src.models.student import Student
from src.utils.exceptions import StudentNotFoundException


class ReportingService(IReportingService):
    """
    Provides reporting logic for the Admin module.
    Aggregates student data for Pass/Fail and Grade distribution reports.
    """

    def __init__(self, data_store: IDataStore, grade_policy: IGradePolicy):
        self._data_store = data_store
        self._grade_policy = grade_policy

    # -------------------------------------------------------------
    # Internal utility methods
    # -------------------------------------------------------------

    def _get_all_students(self):
        """Return only Student-type users."""
        all_users = self._data_store.get_all_users()
        return [u for u in all_users if isinstance(u, Student)]

    def _avg_mark(self, student: Student):
        """Compute average mark for a student (returns None if no marks)."""
        if not getattr(student, "enrolments", None):
            return None
        marks = [e.mark for e in student.enrolments if e.mark is not None]
        if not marks:
            return None
        return round(sum(marks) / len(marks))

    # -------------------------------------------------------------
    # Public methods for the reporting interface
    # -------------------------------------------------------------

    def get_student_enrolments(self, student_id: str):
        """
        Retrieve all enrolments for a given student.
        """
        for u in self._get_all_students():
            if u.id == student_id:
                return u.get_enrolments()
        raise StudentNotFoundException(f"Student with ID '{student_id}' not found.")

    def get_pass_fail_partition(self):
        """
        Partitions students into PASS and FAIL groups based on average mark.
        Uses the same grade policy logic as Grade Report for consistency.
        """
        partitions = {"PASS": [], "FAIL": []}

        for student in self._get_all_students():
            avg = self._avg_mark(student)

            if avg is None:
                # No marks yet — optional: treat as FAIL or make a third group
                partitions["FAIL"].append(student)
                continue

            if self._grade_policy.is_pass_mark(avg):
                partitions["PASS"].append(student)
            else:
                partitions["FAIL"].append(student)

        return partitions

    def get_grade_grouping(self):
        """
        Groups students by their overall average grade (HD/D/C/P/F).
        Uses average mark + the same grade policy.
        """
        groups = {"HD": [], "D": [], "C": [], "P": [], "F": [], "N/A": []}

        for student in self._get_all_students():
            avg = self._avg_mark(student)

            if avg is None:
                groups["N/A"].append(student)
                continue

            grade = self._grade_policy.get_grade_for_mark(avg)
            # Ensure grade is a valid Grade enum
            grade_key = grade.value if hasattr(grade, "value") else str(grade)
            if grade_key not in groups:
                grade_key = "N/A"

            groups[grade_key].append(student)

        return groups

    def get_all_students(self):
        """Return a list of all registered students."""
        return self._get_all_students()