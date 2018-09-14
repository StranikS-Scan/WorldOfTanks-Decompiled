# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/ControlFactory.py
from debug_utils import LOG_DEBUG
from gui.prb_control.items import PlayerDecorator
from gui.prb_control.settings import FUNCTIONAL_FLAG

class ControlFactory(object):
    """
    Abstract class of factory that creates entries, entities for given
    control type (legacy, unit, etc.)
    """

    def __del__(self):
        """
        Log for debug purposes.
        """
        LOG_DEBUG('ControlFactory is deleted', self)

    def createEntry(self, ctx):
        """
        Creates entry point to entity.
        Args:
            ctx: creation request context
        
        Returns:
            entry point instance
        """
        raise NotImplementedError()

    def createEntryByAction(self, action):
        """
        Creates entry point to entity.
        Args:
            action: user's action
        
        Returns:
            entry point instance
        """
        raise NotImplementedError()

    def createEntity(self, ctx):
        """
        Creates prebattle entity.
        Args:
            ctx: creation request context
        
        Returns:
            new prebattle entity
        """
        raise NotImplementedError()

    def createPlayerInfo(self, entity):
        """
        Creates information about player in specified entity.
        Args:
            entity: prebattle entity
        
        Returns:
            player info
        """
        return PlayerDecorator()

    def createStateEntity(self, entity):
        """
        Creates state of specified entity.
        Args:
            entity: given prebattle entity
        
        Returns:
            functional state
        """
        raise NotImplementedError()

    def createLeaveCtx(self, flags=FUNCTIONAL_FLAG.UNDEFINED, entityType=0):
        """
        Creates context to leave for specified entity.
        Args:
            flags: functional flags
            entityType: entity type
        
        Returns:
            prebattle leave request context
        """
        raise NotImplementedError()

    @classmethod
    def _createEntryByAction(cls, action, available):
        """
        Creates entry by action name from given available types.
        Args:
            action: player's action
            available: available dictionary
        
        Returns:
            prebattle entry point
        """
        if action.actionName in available:
            clazz = available[action.actionName]
            result = clazz()
            result.setAccountsToInvite(action.accountsToInvite)
            return result
        else:
            return None

    @classmethod
    def _createEntryByType(cls, entryType, available):
        """
        Creates entry by type from given available types.
        Args:
            entryType: entry type identifier
            available: available dictionary
        
        Returns:
            prebattle entry point
        """
        if entryType in available:
            clazz = available[entryType]
            return clazz()
        else:
            return None

    @classmethod
    def _createEntityByType(cls, entityType, available, **kwargs):
        """
        Creates entity by type from given available types with keywords.
        Args:
            entryType: entry type identifier
            available: available dictionary
            kwargs: entity constructor's arguments
        
        Returns:
            prebattle entity
        """
        if entityType in available:
            clazz = available[entityType]
            return clazz(**kwargs)
        else:
            return None
