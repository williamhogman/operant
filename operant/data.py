import zope.interface as interface

class IStorageProvider(Interface.Interface):
    """ Storage provider for operant"""

    def add_badge(self, user, badge, callback):
        """Adds a badge to a user if appropriate.
        
        The success of the operation should be indicated using the
        callback.
        """

    def track_event(self, event, subject=None, ext={}):
        """Tracks the occurance of an event.

        Takes three arguments, the first one is a string indicating the
        kind of event. Dots may be used to indicate assoiciation
        between parts. If the tracking system does not treat dots this
        way by default implementors may split the string by the dot
        character ("."). The second argument is optional and should
        contain a subject usually a user that caused the event.
        """

    def add_balance(self, user, currency, amount, callback):
        """Adds the passed in amount of a currency to the user's balance.
        
        The callback should be called with two-tuple consisting of a
        boolean indicating success and the balance post-incrementaion.
        """

    def deduct_balance(self, user, currency, amount, callback):
        """Decucts the passed in amount of the given currency from the user's balance.

        The callback should be called with a two-tuple of consisting
        of a boolean indicating success and the balance
        post-decrementation.
        """

    def get_balance(self, user, currency, callback):
        """Gets the balance of the passed in currency

        The callback should be called with a a numeric value giving
        the amount of a the currency that is availiable to the player.
        If the player doesn't have any of the given currency indicate
        this by using 0. If the currency doesn't exist or the command
        None is used.
        """
        
    def add_point(self, user, point_system, amount, callback):
        """Adds the given amoun of points in the given system to the user. 

        Once a point has been awarded, it cannot under normal
        circumstances be removed. The callback should be called with
        the number of points a player has post-increment or None on
        failure.
        """

    
        

class ISetOps(interface.Interface):
    """Interface with set operations needed by operant"""

    def has_attribute(self, pair):
        """Returns true if the user has the named attribute

        The argument is a two-tuple or any other indexable collection
        with a length of two. The first member of the collection is
        the kind, such as operant.badge. The second member is
        either a string or an int representing the attribute.


        This method should return true if the user's set of attributes
        contains the passed in attribute.
        """

    def add_attribute(self, pair):
        """Gives the user the passed in attribute

        The argument is a two-tuple or any other indexable collection
        with a length of two. The first member of the collection is
        the kind, such as operant.badge. The second member is either a
        string or an int representing the attribute.

        This method should add the passed in attribute to the user's
        set of attributes. If the user already has the attribute it
        should be treated as if a successfully addition was performed.

        This corresponds to adding an item to a set, which may be
        implemented using the SADD command if you're using Redis. If
        your data-store doesn't support sets, they can be emulated by
        checking if the collection contains the item before it is
        added.
        """

    def remove_attribute(self, pair):
        """Removes the passed in attribute from the user

        The argument is a two-tuple or any other indexable collection
        with a length of two. The first member of the collection is
        the kind, such as operant.badge. The second member is an
        either a string or an int representing the attribute.

        This method should remove the passed in attribute from the
        user's set of attributes. If the set of attribute doesn't
        contain the attribute the operation should be deemed
        sucessful.
        """

    def attributes_in(self, name):
        """Gets all attributes in the named bucket (e.g. operant.badge)

        This method should return all the attributes of the kind that
        are present. The returned object should supply (contains, x in
        y) and iteration (for x in y). Python built-in lists and sets
        statisfies both these requirements, so if you're unsure you
        can use those.
        """


class ICounterOps(interface.Interface):
    """Interface for abstract numerical operations"""

    def ctr_incr(self, key, by):
        """Increments the value stored in the named key.

        This method should increment the named key by the passed in
        amount. The method should also return the value of the counter
        post-increment.

        If the named key does not exist the key should be crated,
        and assigned to the value the by argument.
        """

    def ctr_decr(self, key, by):
        """Decrements the value stored in the named key.

        This method should have the exact opposite effect
        of ctr_incr. Unless overridden operant
        uses by as a negative value (i.e. 0 - by) and performs
        a normal incrementation operation with this negative
        value.

        If the named key does not exist the key should be created,
        and assigned to the negative value of the by argument.
        """
        self.ctr_incr(key, -by)

    def ctr_set(self, key, to):
        """Sets the value stored in the named key.

        This method should set the named key to the exact value passed
        in. The method should also return the value of the counter
        after modification.

        If the named key does not exist the key should be created and
        assigned to the value of the to argument
        """

    def ctr_get(self, key):
        """Gets the value stored in the named key.

        This method should return the numeric value stored in the
        counter named by the key. If the value is non-existant the
        function should return 0 (zero). If getting a non-existant
        results it being created it should be assigned to 0
        """


class ILogOps(interface.Interface):
    """Interface with log operations for the user facing activity log"""
    def log(self, event, subject):
        """Logs an event with a time stamp to the log"""


class IUserDatastore(ISetOps, ICounterOps, ILogOps):
    """Class with all data operations"""
