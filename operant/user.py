"""Module for actions that the user class should implement
"""
    

class OperantUserBase(object):
    """Class containing abstract operations for users""" 

    def operant_id(self):
        """Returns a value that uniquely identifies the user

        The object can be of any type as long as it is constant over
        the life time of the user.

        You may use a username or auto incrementing id for this.
        However, keep in mind that you it should _never_ change. This
        means that more often than not you should just use your
        primary key (relational db) or your object id (MongoDB).
        """
        raise NotImplementedError()

    def operant_ds(self):
        """ Returns a valid UserDatastore"""
        raise NotImplementedError()

class UserMixin(OperantUserBase):
    """Class to mixin with your user class to gamify it"""

