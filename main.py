import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.data_store import FileDataStore
from src.services.auth_service import AuthService
from src.services.enrolment_service import EnrolmentService
from src.services.reporting_service import ReportingService
from src.services.grade_policy import DefaultGradePolicy

from src.controllers.auth_controllers import AuthController
from src.controllers.enrolment_controller import EnrolmentController
from src.controllers.admin_controller import AdminController
from src.controllers.main_controller import MainController

from src.utils.id_generator import IdGenerator


def main():
    try:
        data_file_path = "students.data"
        data_store = FileDataStore(data_file_path)
        print(f"Database initialized: {data_file_path}")
        
        id_generator = IdGenerator(data_store)
        grade_policy = DefaultGradePolicy()
        
        auth_service = AuthService(data_store, id_generator)
        enrolment_service = EnrolmentService(data_store, grade_policy, id_generator)
        reporting_service = ReportingService(data_store, grade_policy)        
        auth_controller = AuthController(auth_service)
        enrolment_controller = EnrolmentController(enrolment_service)
        admin_controller = AdminController(data_store, reporting_service)
        
        main_controller = MainController(
            auth_controller,
            enrolment_controller,
            admin_controller
        )
        
        print("\n" + "=" * 50)
        print("Welcome to University System")
        print("=" * 50)
        main_controller.run()
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        print("Please check your configuration and try again.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
