# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/players_panel_items.py
import logging
from enum import Enum
import BigWorld
_logger = logging.getLogger(__name__)

class PlayersPanelItems(Enum):
    DEFAULT = 0
    CAMP = 1
    CAPTURED_BOMB = 3
    FREE_BOMB = 4


class IComponent(object):
    __slots__ = ()

    def getType(self):
        raise NotImplementedError

    def setValuesOnCreate(self, entity):
        raise NotImplementedError

    def setValuesOnDestroy(self, entity):
        raise NotImplementedError


class Camp(IComponent):
    __slots__ = ('__campUdo', '__isAlive', '__campId')

    def __init__(self, *args, **kwargs):
        self.__campUdo = ''
        self.__isAlive = True
        self.__campId = 0

    @property
    def campUdo(self):
        return self.__campUdo

    @property
    def isAlive(self):
        return self.__isAlive

    @property
    def campId(self):
        return self.__campId

    def getType(self):
        return PlayersPanelItems.CAMP.name

    def setValuesOnCreate(self, entity):
        udoOccupier = entity.dynamicComponents.get('udoOccupier')
        indexPool = entity.dynamicComponents.get('indexPool')
        if udoOccupier is None or indexPool is None:
            _logger.error('Some component is not found to get camp properties')
            return False
        else:
            self.__campUdo = udoOccupier.guid
            self.__isAlive = True
            self.__campId = indexPool.index
            return True

    def setValuesOnDestroy(self, entity):
        self.__isAlive = False
        return True


class _BaseTimer(IComponent):
    __slots__ = ('_subtype', '_timerID', '_endTime', '_leftTime', '_totalTime')

    def __init__(self, subtype, *args, **kwargs):
        self._subtype = subtype
        self._timerID = 0
        self._endTime = 0
        self._leftTime = 0
        self._totalTime = 0

    def getType(self):
        return self._subtype

    @property
    def timerID(self):
        return self._timerID

    @property
    def endTime(self):
        return self._endTime

    @property
    def leftTime(self):
        return self._leftTime

    @property
    def totalTime(self):
        return self._totalTime

    def setValuesOnCreate(self, entity):
        return False

    def setValuesOnDestroy(self, entity):
        self._timerID = entity.id
        self._endTime = BigWorld.serverTime()
        self._leftTime = 0
        return True


class BombTimer(_BaseTimer):
    __slots__ = ('_isPaused', '_factor', '_timerGUID')

    def __init__(self, subtype, *args, **kwargs):
        super(BombTimer, self).__init__(subtype, *args, **kwargs)
        self._factor = 1.0
        self._isPaused = False
        self._timerGUID = 0

    @property
    def isPaused(self):
        return self._isPaused

    @property
    def timerGUID(self):
        return self._timerGUID

    @property
    def factor(self):
        return self._factor

    def setValuesOnCreate(self, entity):
        stressTimer = entity.dynamicComponents.get('stressTimer')
        if stressTimer is None:
            return False
        else:
            self._timerID = entity.id
            self._endTime = stressTimer.timerInfo.endTime
            self._leftTime = int(round(stressTimer.timeToDelete))
            self._factor = stressTimer.factor
            self._totalTime = stressTimer.lifetime
            self._isPaused = stressTimer.isPaused
            self._timerGUID = stressTimer.getGuiID
            return True

    def setValuesOnDestroy(self, entity):
        super(BombTimer, self).setValuesOnDestroy(entity)
        return True


_ITEMS_BY_TYPE = {PlayersPanelItems.CAMP.name: Camp,
 PlayersPanelItems.CAPTURED_BOMB.name: BombTimer,
 PlayersPanelItems.FREE_BOMB.name: BombTimer}
_PROCESS_REPLAY_TYPES = (PlayersPanelItems.CAPTURED_BOMB.name,)

def getGuiItemType(itemSubtype):
    itemType = _ITEMS_BY_TYPE.get(itemSubtype)
    if itemType is None:
        _logger.error('Unknown type of the item for the players panel')
        return
    else:
        return itemType(itemSubtype)


def isProcessReplayNeeded(itemSubtype):
    return itemSubtype in _PROCESS_REPLAY_TYPES
