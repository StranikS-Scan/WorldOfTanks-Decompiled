# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/items/__init__.py
from collections import namedtuple
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.items.prb_items import PlayerPrbInfo
from gui.prb_control.items.unit_items import PlayerUnitInfo
from gui.prb_control.settings import CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG, PREBATTLE_RESTRICTION, QUEUE_TYPE_TO_PREBATTLE_TYPE, PREBATTLE_TYPE_TO_QUEUE_TYPE
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
        for qType, prbType in QUEUE_TYPE_TO_PREBATTLE_TYPE.iteritems():
            if queueType == qType and self.isInUnit(prbType):
                return True

        return False

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
        if self.isInLegacy() or self.isInUnit():
            return True
        queueTypes = self.__getQueueTypeByPrbType(prbType)
        return self.entityTypeID not in queueTypes

    def isReadyActionSupported(self):
        return self.hasModalEntity and not self.isIntroMode and (self.isInLegacy() or self.isInUnit())

    def isNavigationDisabled(self):
        return self.hasLockedState

    def __getQueueTypeByPrbType(self, prbType):
        return PREBATTLE_TYPE_TO_QUEUE_TYPE.get(prbType, [QUEUE_TYPE.UNKNOWN])


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
