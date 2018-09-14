# Embedded file name: scripts/client/gui/prb_control/items/__init__.py
from collections import namedtuple
from constants import PREBATTLE_TYPE, QUEUE_TYPE, FALLOUT_BATTLE_TYPE
from gui.prb_control.items.prb_items import PlayerPrbInfo
from gui.prb_control.items.unit_items import PlayerUnitInfo
from gui.prb_control.settings import CTRL_ENTITY_TYPE
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.simple('ctrlTypeID', 'entityTypeID', 'hasModalEntity', 'hasLockedState', 'isIntroMode')

class FunctionalState(object):
    __slots__ = ('ctrlTypeID', 'entityTypeID', 'hasModalEntity', 'hasLockedState', 'isIntroMode', 'funcState', 'extra')

    def __init__(self, ctrlTypeID = 0, entityTypeID = 0, hasModalEntity = False, hasLockedState = False, isIntroMode = False, funcState = None, extra = None):
        super(FunctionalState, self).__init__()
        self.ctrlTypeID = ctrlTypeID
        self.entityTypeID = entityTypeID
        self.hasModalEntity = hasModalEntity
        self.hasLockedState = hasLockedState
        self.isIntroMode = isIntroMode
        self.funcState = funcState
        self.extra = extra

    def isInPrebattle(self, prbType = 0):
        result = False
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.PREBATTLE:
            if prbType:
                result = prbType == self.entityTypeID
            else:
                result = self.entityTypeID != 0
        return result

    def isInClubsPreArena(self):
        if self.isInUnit(PREBATTLE_TYPE.CLUBS) and self.funcState is not None:
            return self.funcState.isInPreArena()
        else:
            return False

    def isInSpecialPrebattle(self):
        return self.ctrlTypeID == CTRL_ENTITY_TYPE.PREBATTLE and self.entityTypeID in (PREBATTLE_TYPE.CLAN, PREBATTLE_TYPE.TOURNAMENT)

    def isInUnit(self, prbType = 0):
        result = False
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.UNIT:
            if prbType:
                result = prbType == self.entityTypeID
            else:
                result = self.entityTypeID != 0
        return result

    def isInPreQueue(self, queueType = 0):
        result = False
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.PREQUEUE:
            if queueType:
                result = queueType == self.entityTypeID
            else:
                result = self.entityTypeID != 0
        return result

    def isInFallout(self):
        if self.isInUnit(PREBATTLE_TYPE.SQUAD) and self.extra is not None and self.extra.eventType:
            return True
        else:
            return False

    def isQueueSelected(self, queueType):
        if self.isInPreQueue(queueType):
            return True
        else:
            if self.isInUnit(PREBATTLE_TYPE.SQUAD):
                if queueType == QUEUE_TYPE.EVENT_BATTLES:
                    if self.extra is not None and self.extra.eventType != FALLOUT_BATTLE_TYPE.UNDEFINED:
                        return True
                elif queueType == QUEUE_TYPE.RANDOMS:
                    return True
            return False

    def doLeaveToAcceptInvite(self, prbType = 0):
        result = False
        if self.hasModalEntity:
            if prbType and self.isIntroMode:
                result = prbType != self.entityTypeID
            else:
                result = True
        return result

    def isReadyActionSupported(self):
        return self.hasModalEntity and not self.isIntroMode and (self.isInPrebattle() or self.isInUnit())

    def isNavigationDisabled(self):
        return self.hasLockedState and (self.isInPreQueue() or self.isInPrebattle(PREBATTLE_TYPE.COMPANY) or self.isInUnit(PREBATTLE_TYPE.SQUAD) or self.isInClubsPreArena())


@ReprInjector.simple('isCreator', 'isReady')

class PlayerDecorator(object):
    __slots__ = ('isCreator', 'isReady')

    def __init__(self, isCreator = False, isReady = False):
        self.isCreator = isCreator
        self.isReady = isReady


SelectResult = namedtuple('SelectResult', ('isProcessed', 'newEntry'))
SelectResult.__new__.__defaults__ = (False, None)
CreationResult = namedtuple('SelectResult', ('creationFlags', 'initFlags'))
