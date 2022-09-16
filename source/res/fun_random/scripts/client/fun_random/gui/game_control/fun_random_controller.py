# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/game_control/fun_random_controller.py
import typing
import logging
import adisp
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FUN_RANDOM_LAST_CYCLE_ID
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from constants import Configs, BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
from Event import Event, EventManager
from fun_random.gui.feature.fun_random_models import FunRandomAlertData, FunRandomSeason
from fun_random.gui.prb_control.prb_config import FunctionalFlag, PrebattleActionName, SelectorBattleTypes
from fun_random.gui.shared import event_dispatcher
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, TimerNotifier
from helpers import dependency
from gui.game_control.season_provider import SeasonProvider
from skeletons.gui.game_control import IFunRandomController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared import events
    from gui.periodic_battles.models import AlertData
    from helpers.server_settings import ServerSettings, FunRandomConfig
_logger = logging.getLogger(__name__)

class FunRandomController(IFunRandomController, Notifiable, SeasonProvider, IGlobalListener):
    _ALERT_DATA_CLASS = FunRandomAlertData
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(FunRandomController, self).__init__()
        self.__em = EventManager()
        self.onUpdated = Event(self.__em)
        self.onGameModeStatusTick = Event(self.__em)
        self.onGameModeStatusUpdated = Event(self.__em)
        self.__serverSettings = None
        self.__funRandomSettings = None
        self.__modifiersDataProvider = ModifiersDataProvider()
        return

    def init(self):
        super(FunRandomController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__gameModeStatusUpdate))
        self.addNotificator(TimerNotifier(self.getTimer, self.__gameModeStatusTick))

    def fini(self):
        self.__em.clear()
        self.clearNotification()
        super(FunRandomController, self).fini()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAccountBecomeNonPlayer(self):
        self.stopNotification()
        self.stopGlobalListening()

    def onDisconnected(self):
        self.stopNotification()
        self.stopGlobalListening()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__serverSettings = self.__funRandomSettings = self.__modifiersDataProvider = None
        return

    def onLobbyInited(self, event=None):
        self.startNotification()
        self.startGlobalListening()

    def isAvailable(self):
        return self.isBattlesPossible() and not self.isFrozen()

    def isBattlesPossible(self):
        return self.isEnabled() and self.getCurrentSeason() is not None

    def isEnabled(self):
        return self.__funRandomSettings.isEnabled

    def isFunRandomPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FunctionalFlag.FUN_RANDOM)

    def isSuitableVehicle(self, vehicle, isSquad=False):
        restriction = ''
        ctx = {}
        settings = self.__funRandomSettings
        state, _ = vehicle.getState()
        restrictions = UNIT_RESTRICTION if isSquad else PRE_QUEUE_RESTRICTION
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE or vehicle.compactDescr in settings.forbiddenVehTypes:
            restriction = restrictions.LIMIT_VEHICLE_TYPE
            ctx = {'forbiddenType': vehicle.shortUserName}
        if vehicle.type in settings.forbiddenClassTags:
            restriction = restrictions.LIMIT_VEHICLE_CLASS
            ctx = {'forbiddenClass': vehicle.type}
        if vehicle.level not in settings.levels:
            restriction = restrictions.LIMIT_LEVEL
            ctx = {'levels': settings.levels}
        return ValidationResult(False, restriction, ctx) if restriction else None

    def isSuitableVehicleAvailable(self):
        criteria = self.__getSuitableVehiclesCriteria(REQ_CRITERIA.UNLOCKED)
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.VEHICLE.PREMIUM
        unlockedVehicles = self.__itemsCache.items.getVehicles(criteria)
        return len(unlockedVehicles) > 0

    def hasSuitableVehicles(self):
        criteria = self.__getSuitableVehiclesCriteria(REQ_CRITERIA.INVENTORY)
        criteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        return len(self.__itemsCache.items.getVehicles(criteria)) > 0

    def canGoToMode(self):
        return self.hasSuitableVehicles() or self.isSuitableVehicleAvailable()

    def getAlertBlock(self):
        if self.hasSuitableVehicles():
            alertData = self._getAlertBlockData()
            buttonCallback = event_dispatcher.showFunRandomPrimeTimeWindow
        else:
            alertData = self._ALERT_DATA_CLASS.constructNoVehicles()
            buttonCallback = event_dispatcher.showFunRandomInfoPage
        return (buttonCallback, alertData or self._ALERT_DATA_CLASS(), alertData is not None)

    def getModeSettings(self):
        return self.__funRandomSettings

    def getModifiersDataProvider(self):
        return self.__modifiersDataProvider

    @adisp.adisp_process
    def selectFunRandomBattle(self):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            yield dispatcher.doSelectAction(PrbAction(PrebattleActionName.FUN_RANDOM))
            return

    def _createSeason(self, cycleInfo, seasonData):
        return FunRandomSeason(cycleInfo, seasonData, self.__funRandomSettings.eventID)

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onServerSettingsUpdate
        self.__updateFunRandomSettings()
        return

    def __onServerSettingsUpdate(self, diff):
        if Configs.FUN_RANDOM_CONFIG.value in diff:
            self.__updateFunRandomSettings()

    def __getSuitableVehiclesCriteria(self, criteria):
        criteria = criteria | REQ_CRITERIA.VEHICLE.LEVELS(self.__funRandomSettings.levels)
        criteria |= ~REQ_CRITERIA.VEHICLE.CLASSES(self.__funRandomSettings.forbiddenClassTags)
        criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(self.__funRandomSettings.forbiddenVehTypes)
        criteria |= ~REQ_CRITERIA.VEHICLE.HAS_TAGS(BATTLE_MODE_VEH_TAGS_EXCEPT_FUN)
        return criteria

    def __gameModeStatusTick(self):
        self.onGameModeStatusTick()

    def __gameModeStatusUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onGameModeStatusUpdated(status)

    def __resetGameModeStatusTimers(self):
        self.startNotification()
        self.__gameModeStatusUpdate()
        self.__gameModeStatusTick()

    def __updateFunRandomSettings(self):
        self.__funRandomSettings = self.__serverSettings.funRandomConfig
        self.__modifiersDataProvider = ModifiersDataProvider(self.__funRandomSettings.battleModifiersDescr)
        self.__rememberGameMode()
        self.__resetGameModeStatusTimers()
        self.onUpdated()

    def __rememberGameMode(self):
        currentCycleID = self.getCurrentCycleID()
        rememberedCycleID = AccountSettings.getSettings(FUN_RANDOM_LAST_CYCLE_ID)
        if currentCycleID is not None and currentCycleID != rememberedCycleID:
            AccountSettings.setSettings(FUN_RANDOM_LAST_CYCLE_ID, currentCycleID)
            SelectorBattleTypesUtils.setBattleTypeAsUnknown(SelectorBattleTypes.FUN_RANDOM)
        return
