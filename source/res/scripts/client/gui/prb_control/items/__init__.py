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
    __slots__ = ('ctrlTypeID', 'entityTypeID', 'hasModalEntity', 'hasLockedState', 'isIntroMode', 'funcState', 'funcFlags', 'rosterType')

    def __init__(self, ctrlTypeID=0, entityTypeID=0, hasModalEntity=False, hasLockedState=False, isIntroMode=False, funcState=None, funcFlags=FUNCTIONAL_FLAG.UNDEFINED, rosterType=0):
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
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.LEGACY:
            if prbType:
                return prbType == self.entityTypeID
            return True
        return False

    def isInSpecialPrebattle(self):
        return self.ctrlTypeID == CTRL_ENTITY_TYPE.LEGACY and self.entityTypeID in (PREBATTLE_TYPE.CLAN, PREBATTLE_TYPE.TOURNAMENT)

    def isInUnit(self, prbType=0):
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.UNIT:
            if prbType:
                return prbType == self.entityTypeID
            return True
        return False

    def isInPreQueue(self, queueType=0):
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.PREQUEUE:
            if queueType:
                return queueType == self.entityTypeID
            return True
        return False

    def isQueueSelected(self, queueType):
        if self.isInPreQueue(queueType):
            return True
        if self.isInUnit(PREBATTLE_TYPE.SQUAD) and queueType == QUEUE_TYPE.RANDOMS:
            return True
        if self.isInUnit(PREBATTLE_TYPE.EPIC) and queueType == QUEUE_TYPE.EPIC:
            return True
        if self.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE) and queueType == QUEUE_TYPE.BATTLE_ROYALE:
            return True
        if self.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT) and queueType == QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT:
            return True
        if self.isInUnit(PREBATTLE_TYPE.EVENT) and (queueType == QUEUE_TYPE.EVENT_BATTLES or queueType == QUEUE_TYPE.EVENT_BATTLES_2):
            return True
        if self.isInUnit(PREBATTLE_TYPE.MAPBOX) and queueType == QUEUE_TYPE.MAPBOX:
            return True
        if self.isInUnit(PREBATTLE_TYPE.FUN_RANDOM) and queueType == QUEUE_TYPE.FUN_RANDOM:
            return True
        return True if self.isInUnit(PREBATTLE_TYPE.COMP7) and queueType == QUEUE_TYPE.COMP7 else False

    def doLeaveToAcceptInvite(self, prbType=0):
        if not self.hasModalEntity:
            return False
        if self.isInPreQueue(QUEUE_TYPE.BATTLE_ROYALE) and prbType == PREBATTLE_TYPE.BATTLE_ROYALE:
            return False
        if self.isInPreQueue(QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT) and prbType == PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT:
            return False
        if prbType and self.isIntroMode:
            return prbType != self.entityTypeID
        if not prbType:
            return True
        if self.isIntroMode:
            return prbType != self.entityTypeID
        return True if self.isInLegacy() or self.isInUnit() else self.entityTypeID not in self.__getQueueTypeByPrbType(prbType)

    def isReadyActionSupported(self):
        return self.hasModalEntity and not self.isIntroMode and (self.isInLegacy() or self.isInUnit())

    def isNavigationDisabled(self):
        return self.hasLockedState

    def __getQueueTypeByPrbType(self, prbType):
        prbToQueue = {PREBATTLE_TYPE.SQUAD: [QUEUE_TYPE.RANDOMS],
         PREBATTLE_TYPE.UNIT: [QUEUE_TYPE.UNITS],
         PREBATTLE_TYPE.EVENT: [QUEUE_TYPE.EVENT_BATTLES, QUEUE_TYPE.EVENT_BATTLES_2],
         PREBATTLE_TYPE.STRONGHOLD: [QUEUE_TYPE.STRONGHOLD_UNITS],
         PREBATTLE_TYPE.EPIC: [QUEUE_TYPE.EPIC],
         PREBATTLE_TYPE.MAPBOX: [QUEUE_TYPE.MAPBOX],
         PREBATTLE_TYPE.FUN_RANDOM: [QUEUE_TYPE.FUN_RANDOM],
         PREBATTLE_TYPE.COMP7: [QUEUE_TYPE.COMP7]}
        return prbToQueue.get(prbType, [QUEUE_TYPE.UNKNOWN])


@ReprInjector.simple('isCreator', 'isReady')
class PlayerDecorator(object):
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
