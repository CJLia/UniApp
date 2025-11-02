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

import random

from src.services.interfaces import IDataStore

class IdGenerator:
    """
    A service utility for generating unique IDs.

    This class depends on the IDataStore interface to
    fetch all existing users and check for ID collisions,
    ensuring that all new IDs are unique.
    """

    # Define constants for ID formatting
    ID_LENGTH = 6
    ID_MIN = 1
    # '999999' is the max 6-digit number
    ID_MAX = 999999 

    def __init__(self, data_store):
        """
        Initializes the IdGenerator.

        This uses Dependency Injection. The generator
        is "given" the data store, which it will
        use to check for existing IDs.

        Args:
            data_store (IDataStore): An object that
                follows the IDataStore contract.
        """
        self._data_store = data_store
        
        # --- Caching Existing IDs ---
        # To be efficient, we load all existing IDs
        # into a 'set' once, during initialization.
        # A 'set' provides very fast lookups (O(1)).
        self._existing_ids = self._load_existing_ids()

    def _load_existing_ids(self):
        """
        Private helper to load all IDs from the data store.
        
        Returns:
            set: A set of all existing user and enrolment IDs.
        """
        # Create an empty set to store the IDs
        ids = set()
        
        # Get all users from the data store
        all_users = self._data_store.get_all_users()
        
        # Loop through users and their enrolments
        for user in all_users:
            ids.add(user.id)
            # Check if the user is a Student (Admins
            # don't have enrolments)
            if hasattr(user, 'enrolments'):
                for enrolment in user.enrolments:
                    ids.add(enrolment.id)
        
        return ids

    def generate_unique_id(self):
        """
        Generates a new, unique, six-digit ID string.

        It will keep generating random IDs until it
        finds one that is not in the 'self._existing_ids' set.

        Returns:
            str: A unique, zero-padded, six-digit ID
                 (e.g., "000123").
        """
        while True:
            # Generate a random integer
            new_id_int = random.randint(self.ID_MIN, self.ID_MAX)
            
            # Format the integer as a 6-digit, zero-padded string
            # e.g., 123 -> "000123"
            # The 'zfill' method pads the string with leading zeros.
            new_id_str = str(new_id_int).zfill(self.ID_LENGTH)

            # --- Check for Uniqueness ---
            # Check if the new ID is already in our set
            if new_id_str not in self._existing_ids:
                
                # --- Success ---
                # The ID is unique.
                # Add it to our set so we don't use it again
                self._existing_ids.add(new_id_str)
                # Return the new ID
                return new_id_str
            
            # If the ID was already in the set, the
            # 'while True' loop repeats, and it
            # tries again with a new random number.

