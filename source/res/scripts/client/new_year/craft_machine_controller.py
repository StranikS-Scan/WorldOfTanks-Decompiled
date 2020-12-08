# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine_controller.py
from helpers import dependency
from items.components.ny_constants import ToyTypes, RANDOM_VALUE
from new_year.craft_machine import RANDOM_TOY_PARAM, mapToyParamsFromCraftUiToSrv, MegaDeviceState
from new_year.craft_machine.shared_stuff import RANDOM_TOY_CONFIG_INDEX
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.new_year import INewYearCraftMachineController, INewYearController

class NewYearCraftMachineController(INewYearCraftMachineController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(NewYearCraftMachineController, self).__init__()
        self.__settings = {}
        self.__isConnected = False
        self.setDefaultSettings()

    def onDisconnected(self):
        super(NewYearCraftMachineController, self).onDisconnected()
        self.setDefaultSettings()

    def setDefaultSettings(self):
        self.selectedToyRankIdx = RANDOM_TOY_CONFIG_INDEX
        self.selectedToySettingIdx = RANDOM_TOY_CONFIG_INDEX
        self.selectedToyTypeIdx = RANDOM_TOY_CONFIG_INDEX
        self.isAntiDuplicatorOn = False
        self.isMegaDeviceTurnedOn = False

    def calculateSelectedToyCraftCost(self):
        return self.calculateToyCraftCost(self.isMegaDeviceTurnedOn, self.selectedToyTypeIdx, self.selectedToySettingIdx, self.selectedToyRankIdx)

    def calculateToyCraftCost(self, isMegaToy, toyTypeIdx, toySettingIdx, toyRankIdx):
        return self.calculateMegaToyCraftCost() if isMegaToy else self.calculateRegularToyCraftCost(toyTypeIdx, toySettingIdx, toyRankIdx)

    def calculateMegaToyCraftCost(self):
        config = self.__lobbyContext.getServerSettings().getNewYearCraftCostConfig()
        megaToysCount = self.__nyController.getUniqueMegaToysCount()
        return config.calculateMegaCraftCost(megaToysCount)

    def calculateRegularToyCraftCost(self, toyTypeIdx, toySettingIdx, toyRankIdx):
        config = self.__lobbyContext.getServerSettings().getNewYearCraftCostConfig()
        toyTypeId, toySettingId, toyRankId = mapToyParamsFromCraftUiToSrv(toyTypeIdx, toySettingIdx, toyRankIdx)
        return config.calculateCraftCost(toyTypeId, toySettingId, toyRankId)

    def getSelectedToyType(self):
        if self.isMegaDeviceTurnedOn:
            return ToyTypes.MEGA_COMMON
        elif self.selectedToyTypeIdx is None:
            return RANDOM_TOY_PARAM
        else:
            desiredRegularToyTypeID, _, _ = mapToyParamsFromCraftUiToSrv(toyTypeIdx=self.selectedToyTypeIdx)
            return RANDOM_TOY_PARAM if desiredRegularToyTypeID == RANDOM_VALUE else ToyTypes.ALL[desiredRegularToyTypeID]

    def getActualMegaDeviceState(self):
        return self.getDesiredMegaDeviceState(self.isMegaDeviceTurnedOn)

    def getDesiredMegaDeviceState(self, isMegaDeviceTurnedOn):
        if isMegaDeviceTurnedOn:
            uniqueMegaToysCount = self.__nyController.getUniqueMegaToysCount()
            if uniqueMegaToysCount < len(ToyTypes.MEGA):
                return MegaDeviceState.ACTIVE
            return MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR
        return MegaDeviceState.INACTIVE
