import zope.interface as interface

class IStorageProvider(interface.Interface):
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