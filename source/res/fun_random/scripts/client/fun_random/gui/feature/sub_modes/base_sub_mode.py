# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/base_sub_mode.py
import typing
from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
from constants import BATTLE_MODE_VEH_TAGS_EXCEPT_FUN
from Event import Event, EventManager
from fun_random.gui.feature.fun_constants import FunTimersShifts
from fun_random.gui.feature.models.common import FunRandomAlertData, FunRandomSeason
from fun_random.helpers.server_settings import FunSubModeConfig
from fun_random.gui.shared.events import FunEventType
from fun_random.gui.shared.event_dispatcher import showFunRandomInfoPage, showFunRandomPrimeTimeWindow
from functools import partial
from gui.game_control.season_provider import SeasonProvider
from gui.impl.gen import R
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, UNIT_RESTRICTION
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, TimerNotifier
from helpers import dependency
from skeletons.gui.game_control import ISeasonProvider
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.periodic_battles.models import AlertData
    from fun_random.helpers.server_settings import FunSubModeSeasonalityConfig

class IFunSubMode(ISeasonProvider, Notifiable):
    onSubModeEvent = None

    def init(self):
        pass

    def destroy(self):
        pass

    def isEnabled(self):
        raise NotImplementedError

    def isEntryPointAvailable(self):
        raise NotImplementedError

    def isSuitableVehicle(self, vehicle, isSquad=False):
        raise NotImplementedError

    def isSuitableVehicleAvailable(self):
        raise NotImplementedError

    def hasDailyQuestsEntry(self):
        raise NotImplementedError

    def hasHangarHeaderEntry(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def getAlertBlock(self):
        raise NotImplementedError

    def getAssetsPointer(self):
        raise NotImplementedError

    def getLocalsResRoot(self):
        raise NotImplementedError

    def getIconsResRoot(self):
        raise NotImplementedError

    def getModifiersDataProvider(self):
        raise NotImplementedError

    def getPriority(self):
        raise NotImplementedError

    def getSettings(self):
        raise NotImplementedError

    def getSubModeID(self):
        raise NotImplementedError

    def updateSettings(self, subModeSettings):
        raise NotImplementedError


class FunBaseSubMode(IFunSubMode, SeasonProvider):
    __slots__ = ('_em', '_settings', '_modifiersDataProvider')
    _ALERT_DATA_CLASS = FunRandomAlertData
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, subModeSettings):
        super(FunBaseSubMode, self).__init__()
        self._em = EventManager()
        self.onSubModeEvent = Event(self._em)
        self._settings = subModeSettings
        self._modifiersDataProvider = ModifiersDataProvider(subModeSettings.client.battleModifiersDescr)
        self.addNotificator(SimpleNotifier(self.getTimer, self._subModeStatusUpdate))
        self.addNotificator(TimerNotifier(self.getTimer, self._subModeStatusTick))

    def init(self):
        self.startNotification()

    def destroy(self):
        self.clearNotification()
        self._settings = FunSubModeConfig(eventID=self.getSubModeID())
        self._modifiersDataProvider = ModifiersDataProvider()
        self._em.clear()

    def isAvailable(self):
        return self.isBattlesPossible() and not self.isFrozen()

    def isBattlesPossible(self):
        return self.isEnabled() and self.getCurrentSeason() is not None

    def isEnabled(self):
        return self._settings.isEnabled

    def isEntryPointAvailable(self):
        return self.hasSuitableVehicles() or self.isSuitableVehicleAvailable()

    def isSuitableVehicle(self, vehicle, isSquad=False):
        ctx, restriction = {}, ''
        settings = self._settings.filtration
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

    def hasDailyQuestsEntry(self):
        return False

    def hasHangarHeaderEntry(self):
        return True

    def hasSuitableVehicles(self):
        criteria = self.__getSuitableVehiclesCriteria(REQ_CRITERIA.INVENTORY)
        criteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        return len(self.__itemsCache.items.getVehicles(criteria)) > 0

    def getAlertBlock(self):
        if self.hasSuitableVehicles():
            alertData = self._getAlertBlockData()
            buttonCallback = partial(showFunRandomPrimeTimeWindow, self.getSubModeID())
        else:
            alertData = self._ALERT_DATA_CLASS.constructNoVehicles()
            buttonCallback = partial(showFunRandomInfoPage, self._settings.client.infoPageUrl)
        return (buttonCallback, alertData or self._ALERT_DATA_CLASS(), alertData is not None)

    def getAssetsPointer(self):
        return self._settings.client.assetsPointer

    def getEventEndTimestamp(self):
        currentSeason = self.getCurrentSeason()
        return currentSeason.getEndDate() if currentSeason is not None else 0

    def getIconsResRoot(self):
        assetsPointer = self._settings.client.assetsPointer
        return R.images.fun_random.gui.maps.icons.feature.subModes.dyn(assetsPointer, R.images.fun_random.gui.maps.icons.feature.subModes.undefined)

    def getLocalsResRoot(self):
        assetsPointer = self._settings.client.assetsPointer
        return R.strings.fun_random.subModes.dyn(assetsPointer, R.strings.fun_random.subModes.undefined)

    def getModeSettings(self):
        return self._settings.seasonality

    def getModifiersDataProvider(self):
        return self._modifiersDataProvider

    def getPriority(self):
        return self._settings.client.priority

    def getSettings(self):
        return self._settings

    def getSubModeID(self):
        return self._settings.eventID

    def getTimer(self, now=None, peripheryID=None):
        timer = super(FunBaseSubMode, self).getTimer(now, peripheryID)
        return timer + FunTimersShifts.SUB_MODE if timer > 0 else timer

    def updateSettings(self, subModeSettings):
        return False if self._settings == subModeSettings else self._updateSettings(subModeSettings)

    def _createSeason(self, cycleInfo, seasonData):
        return FunRandomSeason(cycleInfo, seasonData, self._settings.client.assetsPointer)

    def _updateSettings(self, subModeSettings):
        self._settings = subModeSettings
        self._modifiersDataProvider = ModifiersDataProvider(subModeSettings.client.battleModifiersDescr)
        return True

    def _subModeStatusTick(self):
        self.onSubModeEvent(FunEventType.SUB_STATUS_TICK, self.getSubModeID())

    def _subModeStatusUpdate(self):
        self.onSubModeEvent(FunEventType.SUB_STATUS_UPDATE, self.getSubModeID())

    def __getSuitableVehiclesCriteria(self, criteria):
        settings = self._settings.filtration
        criteria = criteria | REQ_CRITERIA.VEHICLE.LEVELS(settings.levels)
        criteria |= ~REQ_CRITERIA.VEHICLE.CLASSES(settings.forbiddenClassTags)
        criteria |= ~REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(settings.forbiddenVehTypes)
        criteria |= ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(BATTLE_MODE_VEH_TAGS_EXCEPT_FUN)
        return criteria
