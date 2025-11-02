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

class ReportingController:
    """
    Handles reporting-related requests from the view.

    This class is 'injected' with an IReportingService implementation,
    decoupling it from the concrete service logic.
    
    Attributes:
        _reporting_service (IReportingService): A reference to the
                                                reporting service.
    """

    def __init__(self, reporting_service):
        """
        Initializes the ReportingController.

        This constructor uses Dependency Injection. The specific
        implementation of 'reporting_service' is 'injected' from
        the outside (e.g., from cli_app.py).

        Args:
            reporting_service (IReportingService): An object that
                                  implements the IReportingService
                                  interface.
        """
        self._reporting_service = reporting_service

    def get_status_partitions(self):
        """
        Requests the pass/fail partition report from the service.

        It calls the ReportingService and returns the resulting
        data structure directly to the view.

        Returns:
            dict: A dictionary with 'PASS' and 'FAIL' keys,
            
                  each containing a list of Student objects.
        """
        try:
            # Delegate the report generation to the service layer
            partitions = self._reporting_service.get_pass_fail_partition()
            return (partitions, None)
            
        except Exception as e:
            # Catch any unexpected errors
            err_msg = "An unexpected error occurred: {err}".format(err=e)
            return (None, err_msg)

    def get_grade_groups(self):
        """
        Requests the grade grouping report from the service.

        It calls the ReportingService and returns the resulting
        data structure directly to the view.

        Returns:
            dict: A dictionary with grade names (e.g., "HD") as keys,
                  each containing a list of Student objects.
        """
        try:
            # Delegate the report generation to the service layer
            groups = self._reporting_service.get_grade_grouping()
            return (groups, None)
            
        except Exception as e:
            # Catch any other unexpected errors
            err_msg = "An unexpected error occurred: {err}".format(err=e)
            return (None, err_msg)