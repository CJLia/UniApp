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

from src.services.interfaces import IDataStore, IReportingService
# Import models
from src.models.student import Student

class AdminController:
    """
    Handles administrative requests from the View.
    
    This controller is slightly different; it needs
    to perform simple CRUD operations (like delete)
    and also call the ReportingService.
    
    It depends on IDataStore for simple operations
    and IReportingService for complex ones.
    """

    def __init__(self, data_store, reporting_service):
        """
        Initializes the AdminController.

        Args:
            data_store (IDataStore): The data store service.
            reporting_service (IReportingService): The reporting service.
        """
        # This controller depends on two services
        self._data_store = data_store
        self._reporting_service = reporting_service

    def get_all_students(self):
        """
        Gets a list of all student objects.

        Returns:
            list[Student]: A list of all Student objects.
        """
        # This is a simple pass-through.
        # It calls the data store directly.
        all_users = self._data_store.get_all_users()
        # Filter the list to only include Students
        students = [user for user in all_users if isinstance(user, Student)]
        return students

    def remove_student(self, student_id):
        """
        Handles a "remove student" request.

        Args:
            student_id (str): The ID of the student to remove.
        
        Returns:
            (str | None): An error message on failure,
                          None on success.
        """
        try:
            # Find the student first to ensure they exist
            all_students = self.get_all_students()
            student_exists = False
            for student in all_students:
                if student.id == student_id:
                    student_exists = True
                    break
            
            if not student_exists:
                return "Error: Student ID not found."

            # If they exist, delegate the deletion
            self._data_store.delete_user(student_id)
            # Success
            return None
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def clear_all_data(self):
        """
        Handles a "clear all student data" request.
        
        Returns:
            (str | None): An error message on failure,
                          None on success.
        """
        try:
            # Delegate the work to the data store
            self._data_store.clear_all_data()
            # Success
            return None
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def get_pass_fail_partition(self):
        """
        Pass-through request to the ReportingController's logic.
        
        (This mirrors the ReportingController to keep
         the AdminCLI simple - it only needs to talk
         to this one AdminController)
        """
        # Delegate to the ReportingService
        try:
            data = self._reporting_service.get_pass_fail_partition()
            return (data, None)
        except Exception as e:
            return (None, f"An unexpected error occurred: {e}")

    def get_grade_grouping(self):
        """
        Pass-through request to the ReportingController's logic.
        """
        # Delegate to the ReportingService
        try:
            data = self._reporting_service.get_grade_grouping()
            return (data, None)
        except Exception as e:
            return (None, f"An unexpected error occurred: {e}")

