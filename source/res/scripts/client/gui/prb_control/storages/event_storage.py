# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/event_storage.py
from account_helpers.AccountSettings import AccountSettings, DEFAULT_QUEUE
from constants import QUEUE_TYPE
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.prb_control.storages.local_storage import LocalStorage
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from debug_utils import LOG_DEBUG

class EventBattlesStorage(LocalStorage):
    __slots__ = ('_isSelected', '_battleType')
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(EventBattlesStorage, self).__init__()
        self._isSelected = False
        self._battleType = QUEUE_TYPE.EVENT_BATTLES

    def clear(self):
        self._isSelected = False

    def swap(self):
        if AccountSettings.getSettings(DEFAULT_QUEUE) in QUEUE_TYPE.EVENT:
            isSelected = True
            vehicles = sorted(self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.EVENT_BATTLE))
            vehicle = findFirst(None, vehicles)
            if vehicle is not None:
                AccountSettings.setSettings(DEFAULT_QUEUE, QUEUE_TYPE.RANDOMS)
                isSelected = False
        else:
            isSelected = False
        self._isSelected = isSelected
        return

    def getBattleType(self):
        LOG_DEBUG('STORAGE GETTING BATTLE TYPE', self._battleType)
        return self._battleType

    def setBattleType(self, value):
        assert value in QUEUE_TYPE.EVENT, 'Unsupported battle type {} given!'.format(value)
        LOG_DEBUG('STORAGE EVENT TYPE:', value)
        self._battleType = value

    def validateSelectedVehicle(self):
        vehicles = sorted(self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.EVENT_BATTLE))
        vehicle = findFirst(None, vehicles)
        return True if vehicle is not None else False

    def isEnabled(self):
        return self.eventsCache.isEventEnabled()

    def release(self):
        self._isSelected = True

    def suspend(self):
        AccountSettings.setSettings(DEFAULT_QUEUE, QUEUE_TYPE.RANDOMS)
        self.clear()
