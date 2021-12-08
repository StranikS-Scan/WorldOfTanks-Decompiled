# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine_controller.py
from gui.impl.lobby.new_year.craft.components import RANDOM_TOY_PARAM, mapToyParamsFromCraftUiToSrv, MegaDeviceState
from gui.impl.lobby.new_year.craft.components.shared_stuff import RANDOM_TOY_CONFIG_INDEX, mapToyParamsFromSrvToCraftUi, DEFAULT_TOY_RANK_INDEX
from helpers import dependency
from items.components.ny_constants import ToyTypes, RANDOM_VALUE, FillerState, MIN_TOY_RANK, RANDOM_TYPE, TOY_TYPES_WITH_RANDOM
from items.new_year import getObjectByToyType
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

    @property
    def fillerShardsCost(self):
        return self.__getConfig().getFillerShardsCost()

    @property
    def isConnected(self):
        return self.__isConnected

    def onConnected(self):
        self.__isConnected = True

    def onDisconnected(self):
        super(NewYearCraftMachineController, self).onDisconnected()
        self.__isConnected = False
        self.setDefaultSettings()

    def setSettings(self, toyTypeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=MIN_TOY_RANK, isMegaOn=False):
        self.isMegaDeviceTurnedOn = isMegaOn
        if not isMegaOn:
            toyTypeID, settingID, rank = mapToyParamsFromSrvToCraftUi(toyTypeID, settingID, rank)
            self.selectedToyTypeIdx = toyTypeID
            self.selectedToySettingIdx = settingID
            self.selectedToyRankIdx = rank

    def setDefaultSettings(self):
        self.selectedToyRankIdx = DEFAULT_TOY_RANK_INDEX
        self.selectedToySettingIdx = RANDOM_TOY_CONFIG_INDEX
        self.selectedToyTypeIdx = RANDOM_TOY_CONFIG_INDEX
        self.fillerState = FillerState.INACTIVE
        self.isMegaDeviceTurnedOn = False

    def calculateSelectedToyCraftCost(self):
        return self.calculateToyCraftCost(self.isMegaDeviceTurnedOn, self.selectedToyTypeIdx, self.selectedToySettingIdx, self.selectedToyRankIdx, self.fillerState)

    def calculateToyCraftCost(self, isMegaToy, toyTypeIdx, toySettingIdx, toyRankIdx, fillerState):
        return self.calculateMegaToyCraftCost() if isMegaToy else self.calculateRegularToyCraftCost(toyTypeIdx, toySettingIdx, toyRankIdx, fillerState)

    def calculateMegaToyCraftCost(self):
        megaToysCount = self.__nyController.getUniqueMegaToysCount()
        return self.__getConfig().calculateMegaCraftCost(megaToysCount)

    def calculateRegularToyCraftCost(self, toyTypeIdx, toySettingIdx, toyRankIdx, fillerState):
        toyTypeId, toySettingId, _ = mapToyParamsFromCraftUiToSrv(toyTypeIdx, toySettingIdx, toyRankIdx)
        return self.__getConfig().calculateCraftCost(toyTypeId, toySettingId, fillerState)

    def getSelectedToyType(self):
        return ToyTypes.MEGA_COMMON if self.isMegaDeviceTurnedOn else self.getRegularSelectedToyType()

    def getToyCategoryType(self):
        if self.selectedToyTypeIdx is None:
            return RANDOM_TYPE
        else:
            toyType = TOY_TYPES_WITH_RANDOM[self.selectedToyTypeIdx]
            categoryType = getObjectByToyType(toyType)
            return categoryType if categoryType else RANDOM_TYPE

    def getRegularSelectedToyType(self):
        if self.selectedToyTypeIdx is None:
            return RANDOM_TOY_PARAM
        else:
            desiredRegularToyTypeID, _, _ = mapToyParamsFromCraftUiToSrv(toyTypeIdx=self.selectedToyTypeIdx)
            return RANDOM_TOY_PARAM if desiredRegularToyTypeID == RANDOM_VALUE else ToyTypes.ALL[desiredRegularToyTypeID]

    def getActualMegaDeviceState(self):
        return self.getDesiredMegaDeviceState(self.isMegaDeviceTurnedOn)

    def getDesiredMegaDeviceState(self, isMegaDeviceTurnedOn):
        if not isMegaDeviceTurnedOn:
            return MegaDeviceState.INACTIVE
        return MegaDeviceState.ACTIVE if self.__nyController.getUniqueMegaToysCount() < len(ToyTypes.MEGA) else MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getNewYearCraftCostConfig()
