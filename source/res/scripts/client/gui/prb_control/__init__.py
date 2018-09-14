# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/__init__.py


class prbDispatcherProperty(property):
    """
    Prebattle dispatcher access property.
    """

    def __get__(self, obj, objType=None):
        """
        Getter for property.
        Args:
            obj: decorated object
            objType: decorated object's class
        
        Returns:
            prebattle dispatcher
        """
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getDispatcher()


class prbEntityProperty(property):
    """
    Prebattle entity access property.
    """

    def __get__(self, obj, objType=None):
        """
        Getter for property.
        Args:
            obj: decorated object
            objType: decorated object's class
        
        Returns:
            prebattle entity
        """
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        entity = None
        if dispatcher is not None:
            entity = dispatcher.getEntity()
        return entity


class prbPeripheriesHandlerProperty(property):
    """
    Peripheries handler access property.
    """

    def __get__(self, obj, objType=None):
        """
        Getter for property.
        Args:
            obj: decorated object
            objType: decorated object's class
        
        Returns:
            peripheries handler
        """
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getPeripheriesHandler()


class prbInvitesProperty(property):
    """
    Prebattle invites access property.
    """

    def __get__(self, obj, objType=None):
        """
        Getter for property.
        Args:
            obj: decorated object
            objType: decorated object's class
        
        Returns:
            prebattle invites
        """
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getInvitesManager()


class prbAutoInvitesProperty(property):
    """
    Prebattle autoinvites access property.
    """

    def __get__(self, obj, objType=None):
        """
        Getter for property.
        Args:
            obj: decorated object
            objType: decorated object's class
        
        Returns:
            prebattle autoinvites
        """
        from gui.prb_control.dispatcher import g_prbLoader
        return g_prbLoader.getAutoInvitesNotifier()
