# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/veh_post_progression_controller.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import getDiffID, REQ_CRITERIA
from gui.veh_post_progression.messages import showWelcomeUnlockMsg
from helpers import dependency
from helpers.server_settings import VehiclePostProgressionConfig
from items import vehicles
from post_progression_common import VehiclesPostProgression, SERVER_SETTINGS_KEY, EXT_DATA_SLOT_KEY, EXT_DATA_PROGRESSION_KEY
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IVehiclePostProgressionController
from skeletons.gui.lobby_context import ILobbyContext
from shared_utils import makeTupleByDict, findFirst
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from helpers.server_settings import ServerSettings
    from items.vehicles import VehicleType
_INVENTORY_ROOT = 'inventory'
_INVENTORY_KEYS = (VehiclesPostProgression.ROOT_KEY, 'customRoleSlots')
_SETTIGS_ROOT = 'serverSettings'

class VehiclePostProgressionController(IVehiclePostProgressionController):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__serverSettings = None
        self.__postProgressionSettings = None
        return

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAvatarBecomePlayer(self):
        if self.__serverSettings is None:
            self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        return

    def onDisconnected(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onProgressionSettingsUpdate
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__postProgressionSettings = None
        self.__serverSettings = None
        return

    def onLobbyInited(self, _):
        self.__tryShowWelcomeUnlockMsg()

    def isDisabledFor(self, veh, settings=None):
        settings = settings or self.__postProgressionSettings
        inEnabledRented = veh.intCD in settings.enabledRentedVehicles
        return veh.isRented and not inEnabledRented or veh.rentalIsOver and inEnabledRented

    def isEnabled(self):
        return self.__postProgressionSettings.isPostProgressionEnabled

    def isExistsFor(self, vehType, settings=None):
        settings = settings or self.__postProgressionSettings
        vehicleIsNotForbidden = vehType.compactDescr not in settings.forbiddenVehicles
        return settings.isEnabled and vehicleIsNotForbidden and vehType.postProgressionTree is not None

    def getSettings(self):
        return self.__postProgressionSettings

    def getInvalidProgressions(self, diff, existingIDs):
        invalidate = set()
        settingsDiff = diff.get(_SETTIGS_ROOT, {}).get(SERVER_SETTINGS_KEY, {})
        invalidate.update(self.__getInvalidBySettings(settingsDiff, existingIDs) if settingsDiff else ())
        inventoryVehDiff = diff.get(_INVENTORY_ROOT, {}).get(GUI_ITEM_TYPE.VEHICLE, {})
        for inventoryKey in _INVENTORY_KEYS:
            invalidate.update(map(getDiffID, inventoryVehDiff.get(inventoryKey, {}).keys()))

        return invalidate

    def processVehExtData(self, vehType, extData):
        if extData is None:
            return
        else:
            settings = self.__postProgressionSettings
            if not self.isExistsFor(vehType, settings):
                extData.clear()
                return
            if extData[EXT_DATA_SLOT_KEY] and not settings.isRoleSlotEnabled:
                extData.pop(EXT_DATA_SLOT_KEY)
            tree = vehicles.g_cache.postProgression().trees[vehType.postProgressionTree]
            extData[EXT_DATA_PROGRESSION_KEY] = extData[EXT_DATA_PROGRESSION_KEY].toActionCDs(tree)
            return

    def __onProgressionSettingsUpdate(self, diff):
        if SERVER_SETTINGS_KEY in diff:
            self.__postProgressionSettings = self.__getPostProgressionSettings()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onProgressionSettingsUpdate
        self.__serverSettings = serverSettings
        self.__postProgressionSettings = self.__getPostProgressionSettings()
        self.__serverSettings.onServerSettingsChange += self.__onProgressionSettingsUpdate
        return

    def __getPostProgressionSettings(self):
        return self.__serverSettings.vehiclePostProgression

    def __getInvalidBySettings(self, settingsDiff, existingIDs):
        prevSettings = self.__postProgressionSettings
        currentSettings = self.__postProgressionSettings = makeTupleByDict(VehiclePostProgressionConfig, settingsDiff)
        enabledChange = currentSettings.isEnabled != prevSettings.isEnabled
        enabledFeaturesChange = currentSettings.enabledFeatures != prevSettings.enabledFeatures
        return set(existingIDs) if enabledChange or enabledFeaturesChange else set(currentSettings.forbiddenVehicles - prevSettings.forbiddenVehicles | currentSettings.enabledRentedVehicles - prevSettings.enabledRentedVehicles | prevSettings.forbiddenVehicles - currentSettings.forbiddenVehicles | prevSettings.enabledRentedVehicles - currentSettings.enabledRentedVehicles)

    def __tryShowWelcomeUnlockMsg(self):
        if not self.isEnabled():
            return
        else:
            defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
            settings = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
            if not settings[GuiSettingsBehavior.VEH_POST_PROGRESSION_UNLOCK_MSG_NEED_SHOW]:
                return
            criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.ELITE
            suitVehs = self.__itemsCache.items.getVehicles(criteria=criteria)
            progressionSettings = self.__postProgressionSettings
            if findFirst(lambda v: self.isExistsFor(v.typeDescr, progressionSettings), suitVehs.itervalues()) is not None:
                showWelcomeUnlockMsg()
            settings[GuiSettingsBehavior.VEH_POST_PROGRESSION_UNLOCK_MSG_NEED_SHOW] = False
            self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, settings)
            return
