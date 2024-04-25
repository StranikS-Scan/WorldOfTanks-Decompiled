# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBAccountComponent.py
import HBAccountSettings
from AccountCommands import REQUEST_ID_NO_RESPONSE, CMD_DEQUEUE_FROM_BATTLE_QUEUE, CMD_ENQUEUE_IN_BATTLE_QUEUE
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from account_helpers import AccountSettings
from debug_utils import LOG_DEBUG
from helpers import dependency, time_utils
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import AccountSettingsKeys, ACCOUNT_DEFAULT_SETTINGS, DEFAULT_NOTIFICATIONS
from skeletons.gui.shared import IItemsCache

class HBAccountComponent(BaseAccountExtensionComponent):
    _gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        global g_accountHistoricalBattlesRepository
        LOG_DEBUG('HBAccountComponent__init__')
        BaseAccountExtensionComponent.__init__(self)
        className = self.__class__.__name__
        if g_accountHistoricalBattlesRepository is not None and g_accountHistoricalBattlesRepository.className != className:
            self.account.connectionMgr.onDisconnected -= _delRepository
            _delRepository()
        if g_accountHistoricalBattlesRepository is None:
            g_accountHistoricalBattlesRepository = _AccountHistoricalBattlesRepository(className)
            self.account.connectionMgr.onDisconnected += _delRepository
        self.frontmenLock = g_accountHistoricalBattlesRepository.frontmenLock
        events.onClientUpdated += self._update
        events.onAccountBecomeNonPlayer += self._onAccountBecomeNonPlayer
        events.onAccountBecomePlayer += self.__migrateAccountSettings
        return

    def enqueueBattle(self, queueType, frontmanID, vehTypeCD):
        vehicle = self.itemsCache.items.getVehicleCopyByCD(vehTypeCD)
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(REQUEST_ID_NO_RESPONSE, CMD_ENQUEUE_IN_BATTLE_QUEUE, (queueType,
             frontmanID,
             vehTypeCD,
             vehicle.invID))

    def dequeueBattle(self, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(REQUEST_ID_NO_RESPONSE, CMD_DEQUEUE_FROM_BATTLE_QUEUE, queueType)

    def _update(self, diff, *args, **kwargs):
        self.account._synchronizeCacheDict(self.frontmenLock, diff.get('cache', None), 'frontmenIDsLock', 'replace', self._gameEventController.onFrontmanLockChanged)
        return

    def _onAccountBecomeNonPlayer(self):
        events.onAccountBecomeNonPlayer -= self._onAccountBecomeNonPlayer
        events.onClientUpdated -= self._update
        LOG_DEBUG('HBAccountComponent_onAccountBecomeNonPlayer')

    def __migrateAccountSettings(self):
        events.onAccountBecomePlayer -= self.__migrateAccountSettings
        expireDate = HBAccountSettings.getSettings(AccountSettingsKeys.EXPIRE_DATE_ACCOUNT_SETTINGS)
        finishDate = self._gameEventController.getEventFinishTime()
        currentTime = time_utils.getServerUTCTime()
        if expireDate and expireDate < currentTime:
            for key, value in ACCOUNT_DEFAULT_SETTINGS.iteritems():
                AccountSettings.setSettings(key, value)

            for key, value in DEFAULT_NOTIFICATIONS.iteritems():
                AccountSettings.setNotifications(key, value)

        if self._gameEventController.isEnabled() and finishDate > currentTime and not expireDate:
            HBAccountSettings.setSettings(AccountSettingsKeys.EXPIRE_DATE_ACCOUNT_SETTINGS, finishDate)


class _AccountHistoricalBattlesRepository(object):

    def __init__(self, className):
        self.className = className
        self.frontmenLock = {}

    def clear(self):
        self.frontmenLock.clear()


def _delRepository():
    global g_accountHistoricalBattlesRepository
    LOG_DEBUG('_delRepository', __name__)
    if g_accountHistoricalBattlesRepository is None:
        return
    else:
        g_accountHistoricalBattlesRepository.clear()
        g_accountHistoricalBattlesRepository = None
        return


g_accountHistoricalBattlesRepository = None
