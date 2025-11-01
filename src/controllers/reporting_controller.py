"""
This file contains the Reporting Controller class.

The controller acts as an intermediary between the Admin View layer
(e.g., CLI or GUI) and the Reporting Service. Its primary role
is to handle requests from the view, call the service to
generate report data, and return that data to the view.
"""

# Import the service interface it depends on
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
            partitions = self._reporting_service.partition_by_status()
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
            groups = self._reporting_service.group_by_grade()
            return (groups, None)
            
        except Exception as e:
            # Catch any other unexpected errors
            err_msg = "An unexpected error occurred: {err}".format(err=e)
            return (None, err_msg)