# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine_controller.py
from gui.impl.lobby.new_year.craft.components import RANDOM_TOY_PARAM, mapToyParamsFromCraftUiToSrv
from gui.impl.lobby.new_year.craft.components.shared_stuff import RANDOM_TOY_CONFIG_INDEX, mapToyParamsFromSrvToCraftUi, DEFAULT_TOY_RANK_INDEX
from helpers import dependency
from items.components.ny_constants import ToyTypes, RANDOM_VALUE, FillerState, RANDOM_TYPE, TOY_TYPES_WITH_RANDOM
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

    def setSettings(self, toyTypeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=RANDOM_VALUE, fillerState=FillerState.INACTIVE):
        toyTypeID, settingID, rank = mapToyParamsFromSrvToCraftUi(toyTypeID, settingID, rank)
        self.selectedToyTypeIdx = toyTypeID
        self.selectedToySettingIdx = settingID
        self.selectedToyRankIdx = rank
        self.fillerState = fillerState

    def setDefaultSettings(self):
        self.selectedToyRankIdx = DEFAULT_TOY_RANK_INDEX
        self.selectedToySettingIdx = RANDOM_TOY_CONFIG_INDEX
        self.selectedToyTypeIdx = RANDOM_TOY_CONFIG_INDEX
        self.fillerState = FillerState.INACTIVE

    def calculateSelectedToyCraftCost(self):
        return self.calculateToyCraftCost(self.selectedToyTypeIdx, self.selectedToySettingIdx, self.selectedToyRankIdx, self.fillerState)

    def calculateToyCraftCost(self, toyTypeIdx, toySettingIdx, toyRankIdx, fillerState):
        return self.calculateRegularToyCraftCost(toyTypeIdx, toySettingIdx, toyRankIdx, fillerState)

    def calculateRegularToyCraftCost(self, toyTypeIdx, toySettingIdx, toyRankIdx, fillerState):
        toyTypeId, toySettingId, toyRankId = mapToyParamsFromCraftUiToSrv(toyTypeIdx, toySettingIdx, toyRankIdx)
        return self.__getConfig().calculateCraftCost(toyTypeId, toySettingId, toyRankId, fillerState)

    def getSelectedToyType(self):
        return self.getRegularSelectedToyType()

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

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getNewYearCraftCostConfig()
