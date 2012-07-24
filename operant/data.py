import zope.interface as interface


class ISetOps(interface.Interface):
    """Interface with set operations needed by operant"""

    def has_attribute(self,name):
        """Returns true if the user has the named attribute
        
        This method should return true if the user's set of attributes
        contains the passed in attribute.
        """

    def add_attribute(self,name):
        """Gives the user the passed in attribute

        This method should add the passed in attribute to the user's
        set of attributes. If the user already has the attribute it
        should be treated as if a successfully addition was performed.

        This corresponds to adding an item to a set, which may be
        implemented using the SADD command if you're using Redis. If
        your data-store doesn't support sets, they can be emulated by
        checking if the collection contains the item before it is
        added.
        """

    def remove_attribute(self,name):
        """Removes the passed in attribute from the user

        This method should remove the passed in attribute from the
        user's set of attributes. If the set of attribute doesn't
        contain the attribute the operation should be deemed
        sucessful.
        """


class ICounterOps(interface.Interface):
    """Interface for abstract numerical operations"""

    def ctr_incr(self,key,by):
        """Increments the value stored in the named key.

        This method should increment the named key by the passed in
        amount. The method should also return the value of the counter
        post-increment.

        If the named key does not exist the key should be crated,
        and assigned to the value the by argument.
        """

    def ctr_decr(self,key,by):
        """Decrements the value stored in the named key.

        This method should have the exact opposite effect 
        of ctr_incr. Unless overridden operant
        uses by as a negative value (i.e. 0 - by) and performs
        a normal incrementation operation with this negative
        value.
        
        If the named key does not exist the key should be created,
        and assigned to the negative value of the by argument.
        """
        self.ctr_incr(key,-by)

    def ctr_get(self,key):
        """Gets the value stored in the named key.

        This method should return the numeric value stored in the
        counter named by the key. If the value is non-existant the
        function should return 0 (zero). If getting a non-existant
        results it being created it should be assigned to 0
        """

class ILogOps(interface.Interface):
    """Interface with log operations for the user facing activity log"""
    def log(self,event,subject):
        """Logs an event with a time stamp to the log"""

    

class IUserDatastore(ISetOps,ICounterOps,ILogOps):
    """Class with all data operations"""
