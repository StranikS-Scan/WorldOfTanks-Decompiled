# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/craftmachine_controller.py
import logging
from adisp import adisp_process
from constants import EnhancementsConfig as config
from constants import MAX_VEHICLE_LEVEL, BATTLE_MODE_VEH_TAGS_EXCEPT_CLAN
from helpers import dependency
from gui.wgcg.craftmachine.contexts import CraftmachineModulesInfoCtx
from gui.wgcg.states import WebControllerStates
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import ICraftmachineController
from skeletons.gui.web import IWebController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(craftMachineController=ICraftmachineController)
def getCraftMachineEntryPointIsActive(craftMachineController=None):
    return craftMachineController.isCraftMachineEntryPointAvailable()


class CraftmachineController(ICraftmachineController):
    __webController = dependency.descriptor(IWebController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(CraftmachineController, self).__init__()
        self.__modules = {}
        self.__enabledSync = True
        self.__enabled = False

    def onConnected(self):
        self.__lobbyCtx.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def onDisconnected(self):
        self.__lobbyCtx.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def onAccountBecomePlayer(self):
        if self.__webController.getStateID() == WebControllerStates.STATE_NOT_DEFINED:
            self.__webController.invalidate()
        self.__onServerSettingsChange(self.__lobbyCtx.getServerSettings().getSettings())

    def getModuleName(self, module):
        return self.__modules.get(str(module), '')

    def __onServerSettingsChange(self, diff):
        clansDiff = diff.get(config.SECTION_NAME, {})
        if config.ENABLED in clansDiff:
            self.__enabled = clansDiff[config.ENABLED]
            self.__updateModulesInfo()

    @adisp_process
    def __updateModulesInfo(self):
        if not (self.__enabled and self.__enabledSync):
            return
        response = yield self.__webController.sendRequest(ctx=CraftmachineModulesInfoCtx())
        if response.isSuccess():
            self.__enabledSync = False
            data = response.getData() or {}
            for key, element in data.iteritems():
                self.__modules[key] = element.get('localizations', {}).get('name', '')

        else:
            _logger.warning('Failed to update modules data for craftmachine. Code: %s.', response.getCode())

    @staticmethod
    def __filterEnabledVehiclesCriteria(criteria):
        criteria = criteria | REQ_CRITERIA.VEHICLE.LEVEL(MAX_VEHICLE_LEVEL)
        criteria |= ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(BATTLE_MODE_VEH_TAGS_EXCEPT_CLAN)
        criteria |= ~REQ_CRITERIA.VEHICLE.MAPS_TRAINING
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        return criteria

    def __vehicleIsAvailableForRestore(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE)
        vResorePossible = self.__itemsCache.items.getVehicles(criteria)
        return len(vResorePossible) > 0

    def __vehicleIsAvailableForBuy(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.UNLOCKED)
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.HIDDEN
        vUnlocked = self.__itemsCache.items.getVehicles(criteria)
        return len(vUnlocked) > 0

    def __suitableVehicleIsAvailable(self):
        return self.__vehicleIsAvailableForBuy() or self.__vehicleIsAvailableForRestore()

    def __hasSuitableVehicles(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.INVENTORY)
        return len(self.__itemsCache.items.getVehicles(criteria)) > 0

    def isCraftMachineEntryPointAvailable(self):
        vehicleIsAvailable = self.__hasSuitableVehicles() or self.__suitableVehicleIsAvailable()
        return vehicleIsAvailable
