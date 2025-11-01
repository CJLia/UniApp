"""
This file contains the implementation of the IDataStore interface.

This class is responsible for all persistence logic, specifically
reading from and writing to a binary file using the 'pickle' module.
It abstracts all file I/O operations from the rest of the application.
This is an example of the 'Repository' or 'Data Access Object' (DAO)
pattern.
"""

# Import 'pickle' for serializing/deserializing Python objects
import pickle
# Import 'os' for checking file existence
import os

# Import the interface this class implements
from src.services.interfaces import IDataStore

# Import all models. This is necessary for the pickle module
# to correctly deserialize the objects.
from src.models.user import User
from src.models.student import Student
from src.models.admin import Admin
from src.models.subject import Subject
from src.models.enrolment import Enrolment, Grade

# Import custom exceptions
from src.utils.exceptions import DataPersistenceException

class FileDataStore(IDataStore):
    """
    Implements the IDataStore interface using a local pickle file.

    This class serializes a single dictionary containing all
    application data (users, subjects) into a file.
    
    Attributes:
        _file_path (str): The name of the file to store data.
        _data (dict): A cache of the data, held in memory.
    """

    def __init__(self, file_path):
        """
        Initializes the FileDataStore.

        Args:
            file_path (str): The path to the data file (e.g., 'students.data').
        """
        # Private attribute for the file path
        self._file_path = file_path
        
        # Private attribute to hold the application state in memory.
        # It is initialized by calling the load_data method.
        self._data = self.load_data()

    def load_data(self):
        """
        Loads all application data from the persistent pickle file.

        If the file does not exist (e.g., first time running the
        app), it initializes an empty data structure.

        Returns:
            dict: A dictionary containing all data (e.g., {'users': [...],
                  'subjects': [...]}).
                  
        Raises:
            DataPersistenceException: If an error occurs during
                                      deserialization.
        """
        # Check if the file exists using os.path.exists
        if os.path.exists(self._file_path):
            try:
                # 'rb' mode means 'read binary'
                # The 'with' statement ensures the file is
                # automatically closed.
                with open(self._file_path, 'rb') as f:
                    # pickle.load deserializes the file stream
                    # back into a Python object
                    data = pickle.load(f)
                    return data
            except (pickle.UnpicklingError, EOFError, IOError) as e:
                # If the file is corrupted or unreadable, raise a
                # custom exception
                raise DataPersistenceException(
                    "Error loading data file: {e}".format(e=e)
                )
        else:
            # If no file exists, return the default empty
            # data structure.
            return {'users': [], 'subjects': []}

    def save_data(self):
        """
        Saves the current in-memory data cache to the
        persistent pickle file.

        Note: This is an internal helper method. The public
        interface methods like 'add_user' will call this
        to ensure data is saved after every change.
        
        Raises:
            DataPersistenceException: If an error occurs during
                                      serialization.
        """
        try:
            # 'wb' mode means 'write binary'. This will
            # overwrite the file.
            with open(self._file_path, 'wb') as f:
                # pickle.dump serializes the self._data object
                # into the file
                pickle.dump(self._data, f)
        except (IOError, pickle.PicklingError) as e:
            # If the file cannot be written to, raise a custom exception
            raise DataPersistenceException(
                "Error saving data file: {e}".format(e=e)
            )

    def get_all_users(self):
        """
        Retrieves all user objects from the in-memory data cache.

        Returns:
            list: A list of all User objects (Students and Admins).
        """
        # The 'users' list is retrieved from the data dictionary.
        # .get() is used to safely get the key, returning an
        # empty list if 'users' doesn't exist.
        return self._data.get('users', [])

    def get_all_subjects(self):
        """
        Retrieves all subject objects from the in-memory data cache.

        Returns:
            list: A list of all Subject objects.
        """
        return self._data.get('subjects', [])

    def add_user(self, user):
        """
        Adds a new user to the data store and saves to file.

        Args:
            user (User): The User object to add.
        """
        # Append the new user to the 'users' list in memory
        self.get_all_users().append(user)
        
        # Persist the change to the file
        self.save_data()

    def update_user(self, updated_user):
        """
        Updates an existing user in the data store and saves to file.

        This method finds the user by their ID and replaces the
        old user object with the new one.

        Args:
            updated_user (User): The User object with updated information.
        """
        # A list comprehension is used to find the index
        # of the user to be updated.
        users = self.get_all_users()
        for i, user in enumerate(users):
            if user.id == updated_user.id:
                # Replace the old object at this index
                users[i] = updated_user
                
                # Persist the change
                self.save_data()
                
                # Exit the method
                return
        
        # If the loop finishes, the user was not found
        # (This should ideally not be reachable if called
        # from services that validate first)

    def delete_user(self, user_id):
        """
        Deletes a user from the data store by their ID and saves to file.

        Args:
            user_id (str): The ID of the user to delete.
        """
        users = self.get_all_users()
        
        # Find the user object to remove
        user_to_delete = None
        for user in users:
            if user.id == user_id:
                user_to_delete = user
                break
        
        # If the user was found, remove it from the list
        if user_to_delete:
            users.remove(user_to_delete)
            
            # Persist the change
            self.save_data()

    def get_all_subjects(self):
        """
        Retrieves all subject objects from the in-memory cache.

        Returns:
            list[Subject]: A list of all Subject objects.
        """
        return self._data.get('subjects', [])

    def clear_all_data(self):
        """
        Completely clears all student data from the data store.
        This is an administrative function.
        
        It resets the 'users' list to only contain Admins.
        """
        # Get the current list of all users
        all_users = self.get_all_users()
        
        # Create a new list containing ONLY Admin objects
        # This uses a list comprehension
        admin_users = [user for user in all_users if isinstance(user, Admin)]
        
        # Reset the 'users' list in the cache to the new list
        self._data['users'] = admin_users
        
        # Persist this change to the file
        self._save_data()


    # --- Private Helper Methods ---
    # This method is not part of the IDataStore 'contract'.
    # It's a private utility method for this class only.
    # The underscore '_' prefix indicates it is 'private'.

    def _save_data(self):
        """
        Saves the current in-memory cache ('self._data')
        to the pickle file.
        
        This is called by any method that modifies the
        data (e.g., add_user, update_user).
        """
        try:
            # Open the file in 'write binary' ('wb') mode
            # This will create the file if it doesn't exist
            # or overwrite it if it does.
            with open(self._file_path, 'wb') as f:
                # 'pickle.dump' serializes the 'self._data'
                # object and writes it to the file 'f'.
                pickle.dump(self._data, f)
        except IOError as e:
            # If the file cannot be written (e.g., permissions)
            print(f"Error saving data to file: {e}")