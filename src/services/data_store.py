import pickle
import os
import sys
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

from src.services.interfaces import IDataStore

from src.models.user import User
from src.models.student import Student
from src.models.admin import Admin
from src.models.subject import Subject
from src.models.enrolment import Enrolment, Grade

from src.utils.exceptions import DataPersistenceException

class FileDataStore(IDataStore):

    def __init__(self, file_path):
        self._file_path = file_path
        self._data = self.load_data()

    def load_data(self):
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, 'rb') as f:
                    data = pickle.load(f)
                    return data
            except (pickle.UnpicklingError, EOFError, IOError) as e:
                raise DataPersistenceException(
                    f"Error loading data file: {e}"
                )
        else:
            return {'users': [], 'subjects': []}

    def save_data(self, data=None):
        try:
            with open(self._file_path, 'wb') as f:
                pickle.dump(self._data, f)
        except (IOError, pickle.PicklingError) as e:
            raise DataPersistenceException(
                f"Error saving data file: {e}"
            )

    def get_all_users(self):
        return self._data.get('users', [])

    def get_all_subjects(self):
        """Return all Subject objects."""
        return self._data.get("subjects", [])
    
    def subject_exists(self, code: str) -> bool:
        """Check if a subject ID already exists."""
        return any(getattr(s, "id", None) == code for s in self.get_all_subjects())
    
    def add_subject(self, subject):
        """Add a new subject and save."""
        subs = self._data.get("subjects", [])
        if any(getattr(s, "id", None) == subject.id for s in subs):
            raise ValueError(f"Subject '{subject.id}' already exists.")
        subs.append(subject)
        self._data["subjects"] = subs
        self.save_data()

    def remove_subject(self, code: str):
        """Remove a subject by code and save."""
        subs = self._data.get("subjects", [])
        new_subs = [s for s in subs if getattr(s, "id", None) != code]
        if len(new_subs) == len(subs):
            raise ValueError(f"Subject '{code}' not found.")
        self._data["subjects"] = new_subs
        self.save_data()

    def add_user(self, user):
        self.get_all_users().append(user)
        self.save_data()

    def update_user(self, updated_user):
        users = self.get_all_users()
        for i, user in enumerate(users):
            if user.id == updated_user.id:
                users[i] = updated_user
                self.save_data()
                return

    def delete_user(self, user_id):
        users = self.get_all_users()
        
        user_to_delete = None
        for user in users:
            if user.id == user_id:
                user_to_delete = user
                break
        
        if user_to_delete:
            users.remove(user_to_delete)
            self.save_data()


    def clear_all_data(self):
        all_users = self.get_all_users()
        admin_users = [user for user in all_users if isinstance(user, Admin)]
        self._data['users'] = admin_users
        self.save_data()
