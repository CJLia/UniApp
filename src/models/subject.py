"""
Contains the Subject class, representing a single subject offered
by the university.
"""

class Subject:
    """
    Represents a university subject.
    
    This class is a simple data structure (or 'model') that holds 
    information about a subject. It encapsulates the subject's data,
    following the Encapsulation principle of OOP. It's designed to
    be associated with an Enrolment object, as per the design schema.
    """

    def __init__(self, id, name):
        """
        Initialises a new Subject object.
        
        Args:
            id (str): The subject's unique code (e.g., 'ICT101').
            name (str): The full name of the subject (e.g., 'Programming Foundations').
        """
        # Public attributes as defined in the design schema's UML diagram.
        self.id = id
        self.name = name

    def __repr__(self):
        """
        Provides an unambiguous string representation of the Subject object.
        
        This is useful for debugging, as it gives a clear view of the
        object's state.
        
        Returns:
            str: A string in the format Subject(id='...', name='...').
        """
        return f"Subject(id='{self.id}', name='{self.name}')"
