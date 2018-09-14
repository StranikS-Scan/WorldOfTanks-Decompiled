# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/__init__.py
from collections import namedtuple
from UnitBase import ROSTER_TYPE
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.items.prb_items import PlayerPrbInfo
from gui.prb_control.items.unit_items import PlayerUnitInfo
from gui.prb_control.settings import CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG, PREBATTLE_RESTRICTION
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.simple('ctrlTypeID', 'entityTypeID', 'hasModalEntity', 'hasLockedState', 'isIntroMode')
class FunctionalState(object):
    """
    Current state of prebattle entity.
    """
    __slots__ = ('ctrlTypeID', 'entityTypeID', 'hasModalEntity', 'hasLockedState', 'isIntroMode', 'funcState', 'funcFlags', 'rosterType')

    def __init__(self, ctrlTypeID=0, entityTypeID=0, hasModalEntity=False, hasLockedState=False, isIntroMode=False, funcState=None, funcFlags=FUNCTIONAL_FLAG.UNDEFINED, rosterType=0):
        """
        Initializes default state of the object.
        """
        super(FunctionalState, self).__init__()
        self.ctrlTypeID = ctrlTypeID
        self.entityTypeID = entityTypeID
        self.hasModalEntity = hasModalEntity
        self.hasLockedState = hasLockedState
        self.isIntroMode = isIntroMode
        self.funcState = funcState
        self.funcFlags = funcFlags
        self.rosterType = rosterType

    def isInLegacy(self, prbType=0):
        """
        Are we in legacy prebattle.
        Args:
            prbType: check defined prebattle type
        
        Returns:
            are we in that legacy
        """
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.LEGACY:
            if prbType:
                return prbType == self.entityTypeID
            return True
        return False

    def isInClubsPreArena(self):
        """
        Are we in clubs pre arena state.
        Returns:
            are we in club and it is in prearena state
        """
        return self.funcState.isInPreArena() if self.isInUnit(PREBATTLE_TYPE.CLUBS) and self.funcState is not None else False

    def isInSpecialPrebattle(self):
        """
        Are we in special battles.
        Returns:
            are we in on of the special legacies
        """
        return self.ctrlTypeID == CTRL_ENTITY_TYPE.LEGACY and self.entityTypeID in (PREBATTLE_TYPE.CLAN, PREBATTLE_TYPE.TOURNAMENT)

    def isInUnit(self, prbType=0):
        """
        Are we in proper unit prebattle.
        Args:
            prbType: check defined prebattle type
        
        Returns:
           are we in that unit
        """
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.UNIT:
            if prbType:
                return prbType == self.entityTypeID
            return True
        return False

    def isInPreQueue(self, queueType=0):
        """
        Are we in proper prequeue prebattle.
        Args:
            queueType: check defined queue type
        
        Returns:
           are we in that prequeue
        """
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.PREQUEUE:
            if queueType:
                return queueType == self.entityTypeID
            return True
        return False

    def isInFallout(self):
        """
        Are we in fallout of any kind.
        Returns:
            are in fallout
        """
        return self.funcFlags & FUNCTIONAL_FLAG.FALLOUT > 0

    def isQueueSelected(self, queueType):
        """
        Are we in checked queue.
        Args:
            queueType: check defined queue type
        
        Returns:
            are we in that queue
        """
        if self.isInPreQueue(queueType):
            return True
        if self.isInUnit(PREBATTLE_TYPE.SQUAD) and queueType == QUEUE_TYPE.RANDOMS:
            return True
        if self.isInUnit(PREBATTLE_TYPE.EVENT) and queueType == QUEUE_TYPE.EVENT_BATTLES:
            return True
        return True if self.isInUnit(PREBATTLE_TYPE.FALLOUT) and (queueType == QUEUE_TYPE.FALLOUT_CLASSIC and self.rosterType == ROSTER_TYPE.FALLOUT_CLASSIC_ROSTER or queueType == QUEUE_TYPE.FALLOUT_MULTITEAM and self.rosterType == ROSTER_TYPE.FALLOUT_MULTITEAM_ROSTER) else False

    def doLeaveToAcceptInvite(self, prbType=0):
        """
        Should we leave current prebattle to join other.
        Args:
            prbType: prebattle type to join
        
        Returns:
            should we leave current
        """
        if self.hasModalEntity:
            if prbType and self.isIntroMode:
                return prbType != self.entityTypeID
            return True
        return False

    def isReadyActionSupported(self):
        """
        Is there ready action supported for current state.
        Returns:
            is it allowed
        """
        return self.hasModalEntity and not self.isIntroMode and (self.isInLegacy() or self.isInUnit())

    def isNavigationDisabled(self):
        """
        Is lobby navigation disabled due to locked state
        """
        return self.hasLockedState


@ReprInjector.simple('isCreator', 'isReady')
class PlayerDecorator(object):
    """
    Player's data decorator.
    """
    __slots__ = ('isCreator', 'isReady')

    def __init__(self, isCreator=False, isReady=False):
        self.isCreator = isCreator
        self.isReady = isReady


SelectResult = namedtuple('SelectResult', ('isProcessed', 'newEntry'))
SelectResult.__new__.__defaults__ = (False, None)
CreationResult = namedtuple('SelectResult', ('creationFlags', 'initFlags'))
CreationResult.__new__.__defaults__ = (FUNCTIONAL_FLAG.UNDEFINED, FUNCTIONAL_FLAG.UNDEFINED)
ValidationResult = namedtuple('ValidationResult', ('isValid', 'restriction', 'ctx'))
ValidationResult.__new__.__defaults__ = (True, PREBATTLE_RESTRICTION.UNDEFINED, None)
