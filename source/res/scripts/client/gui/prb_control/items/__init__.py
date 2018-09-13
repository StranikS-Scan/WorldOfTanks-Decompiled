# Embedded file name: scripts/client/gui/prb_control/items/__init__.py
from constants import PREBATTLE_TYPE
from gui.prb_control.items.prb_items import PlayerPrbInfo
from gui.prb_control.items.unit_items import PlayerUnitInfo
from gui.prb_control.settings import CTRL_ENTITY_TYPE

class FunctionalState(object):
    __slots__ = ('ctrlTypeID', 'entityTypeID', 'hasModalEntity', 'isIntroMode')

    def __init__(self, ctrlTypeID = 0, entityTypeID = 0, hasModalEntity = False, isIntroMode = False):
        super(FunctionalState, self).__init__()
        self.ctrlTypeID = ctrlTypeID
        self.entityTypeID = entityTypeID
        self.hasModalEntity = hasModalEntity
        self.isIntroMode = isIntroMode

    def __repr__(self):
        return 'FunctionalState(ctrlTypeID = {0!r:s}, entityTypeID = {1!r:s}, hasModalEntity = {2!r:s}, isIntroMode = {3!r:s})'.format(self.ctrlTypeID, self.entityTypeID, self.hasModalEntity, self.isIntroMode)

    def isInPrebattle(self, prbType = 0):
        result = False
        if self.ctrlTypeID == CTRL_ENTITY_TYPE.PREBATTLE:
            if prbType:
                result = prbType == self.entityTypeID
            else:
                result = self.entityTypeID != 0
        return result

    def isInSpecialPrebattle(self):
        return self.ctrlTypeID == CTRL_ENTITY_TYPE.PREBATTLE and self.entityTypeID in [PREBATTLE_TYPE.CLAN, PREBATTLE_TYPE.TOURNAMENT]

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

    def doLeaveToAcceptInvite(self, prbType = 0):
        result = False
        if self.hasModalEntity:
            if prbType and self.isIntroMode:
                result = prbType != self.entityTypeID
            else:
                result = True
        return result


class PlayerDecorator(object):
    __slots__ = ('isCreator', 'isReady')

    def __init__(self, isCreator = False, isReady = False):
        self.isCreator = isCreator
        self.isReady = isReady

    def __repr__(self):
        return 'PlayerDecorator(isCreator = {0!r:s}, isReady = {1!r:s})'.format(self.isCreator, self.isReady)
