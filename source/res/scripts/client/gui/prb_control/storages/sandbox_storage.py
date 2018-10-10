# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/sandbox_storage.py
from account_helpers.AccountSettings import AccountSettings, DEFAULT_QUEUE
from constants import QUEUE_TYPE
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.prb_control.storages.local_storage import LocalStorage
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class SandboxStorage(LocalStorage):
    __slots__ = ('_isSelected',)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(SandboxStorage, self).__init__()
        self._isSelected = False

    def clear(self):
        self._isSelected = False

    def swap(self):
        defaultQueue = AccountSettings.getSettings(DEFAULT_QUEUE)
        if self.lobbyContext.getServerSettings().isBootcampEnabled():
            defaultQueue = QUEUE_TYPE.RANDOMS
        if defaultQueue == QUEUE_TYPE.SANDBOX:
            isSelected = True
            dossier = self.itemsCache.items.getAccountDossier()
            criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(range(3, 10)) | ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
            vehicles = sorted(self.itemsCache.items.getVehicles(criteria=criteria).values(), key=lambda item: item.level)
            vehicle = findFirst(None, vehicles)
            if vehicle is not None:
                AccountSettings.setSettings(DEFAULT_QUEUE, QUEUE_TYPE.RANDOMS)
                isSelected = False
            if dossier is not None and isSelected:
                count = dossier.getRandomStats().getBattlesCount()
                if count >= BATTLES_TO_SELECT_RANDOM_MIN_LIMIT:
                    AccountSettings.setSettings(DEFAULT_QUEUE, QUEUE_TYPE.RANDOMS)
                    isSelected = False
        else:
            isSelected = False
        self._isSelected = isSelected
        return

    def release(self):
        self._isSelected = True

    def suspend(self):
        AccountSettings.setSettings(DEFAULT_QUEUE, QUEUE_TYPE.RANDOMS)
        self.clear()

    def isModeSelected(self):
        return self._isSelected and self.lobbyContext.getServerSettings().isSandboxEnabled()
