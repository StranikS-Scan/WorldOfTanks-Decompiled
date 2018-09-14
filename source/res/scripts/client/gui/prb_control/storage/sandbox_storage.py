# Embedded file name: scripts/client/gui/prb_control/storage/sandbox_storage.py
from account_helpers.AccountSettings import AccountSettings, DEFAULT_QUEUE
from constants import QUEUE_TYPE
from gui.LobbyContext import g_lobbyContext
from gui.prb_control.settings import BATTLES_TO_SELECT_RANDOM_MIN_LIMIT
from gui.prb_control.storage.local_storage import LocalStorage
from gui.shared import g_itemsCache

class SandboxStorage(LocalStorage):
    __slots__ = ('_isSelected',)

    def __init__(self):
        super(SandboxStorage, self).__init__()
        self._isSelected = False

    def clear(self):
        self._isSelected = False

    def swap(self):
        if AccountSettings.getSettings(DEFAULT_QUEUE) == QUEUE_TYPE.SANDBOX:
            isSelected = True
            dossier = g_itemsCache.items.getAccountDossier()
            if dossier is not None:
                isSelected = True
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
        return self._isSelected and g_lobbyContext.getServerSettings().isSandboxEnabled()
