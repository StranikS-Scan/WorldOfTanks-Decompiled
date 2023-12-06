# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/monitor.py
from helpers import dependency
from items import new_year
from items.components.ny_constants import FillerState, YEARS_INFO
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from gui.impl.gen.view_models.views.lobby.new_year.views.craft.ny_craft_monitor_model import MonitorState
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from .data_nodes import ViewModelDataNode
from .shared_stuff import RANDOM_TOY_CONFIG_INDEX
from .texts import TOY_TYPE_STRINGS, TOY_RANKS_STRINGS, TOY_SETTING_STRINGS, TOY_PLACES_STRINGS

class CraftMonitor(ViewModelDataNode):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel):
        super(CraftMonitor, self).__init__(viewModel)
        self.__cleanAnimationFlags()
        self.__printingSoundEnabled = False
        self.__valueChanged = False
        self.__stateChanged = False

    def updateData(self):
        with self._viewModel.transaction() as tx:
            self.__cleanAnimationFlags()
            prevState = tx.getMonitorState()
            shardsCount = self._nodesHolder.shardsStorage.getShardsCount()
            shardsChanged = tx.getShardsCount() != shardsCount
            tx.setShardsCount(shardsCount)
            prevAntiDublicatorState = tx.getIsAntiDuplicatorEnabled()
            antiDuplicatorChanged = False
            antiDuplicatorState = self._nodesHolder.antiduplicator.getAntiDuplicatorState()
            isAntiDuplicatorErrorState = antiDuplicatorState == FillerState.ERROR
            isAntiDuplicatorActiveState = antiDuplicatorState.isActive
            isAntiDuplicatorInactiveState = antiDuplicatorState == FillerState.INACTIVE
            fillersCount = self._nodesHolder.fillersStorage.getFillersCount()
            hasNoFillers = antiDuplicatorState == FillerState.USE_CHARGES and fillersCount == 0
            hasRandomRegularToyParam = self.__hasRandomRegularToyParam()
            if isAntiDuplicatorActiveState:
                tx.setIsAntiDuplicatorEnabled(True)
                antiDuplicatorChanged = not prevAntiDublicatorState
            elif isAntiDuplicatorInactiveState:
                tx.setIsAntiDuplicatorEnabled(False)
                antiDuplicatorChanged = prevAntiDublicatorState
            if not isAntiDuplicatorInactiveState:
                if self.__isRegularToysCollected():
                    self.__printingSoundEnabled = prevState != MonitorState.FULL_REGULAR or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != MonitorState.FULL_REGULAR
                    tx.setMonitorState(MonitorState.FULL_REGULAR)
                    return
                if hasRandomRegularToyParam:
                    self.__printingSoundEnabled = prevState != MonitorState.HAS_RANDOM_PARAM or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != MonitorState.HAS_RANDOM_PARAM
                    tx.setMonitorState(MonitorState.HAS_RANDOM_PARAM)
                    return
                if self.__isFullRegularToysGroup():
                    self.__printingSoundEnabled = prevState != MonitorState.FULL_REGULAR_SUBGROUP or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != MonitorState.FULL_REGULAR_SUBGROUP
                    tx.setMonitorState(MonitorState.FULL_REGULAR_SUBGROUP)
                    return
                if isAntiDuplicatorErrorState or hasNoFillers:
                    self.__printingSoundEnabled = prevState != MonitorState.HAS_NO_FILLERS or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != MonitorState.HAS_NO_FILLERS
                    tx.setMonitorState(MonitorState.HAS_NO_FILLERS)
                    return
            if shardsCount == 0:
                self.__printingSoundEnabled = prevState != MonitorState.SHARDS_NOT_AVAILABLE
                self.__stateChanged = prevState != MonitorState.SHARDS_NOT_AVAILABLE
                tx.setMonitorState(MonitorState.SHARDS_NOT_AVAILABLE)
                return
            craftCost = self._nodesHolder.craftCostBlock.getCraftCost()
            hasChange, toyType, toySetting, toyRank, toyPlace = self.__checkForUpdateRegularToysVisuals(tx)
            someValuesChanged = hasChange or antiDuplicatorChanged or shardsChanged
            nextState = MonitorState.NOT_ENOUGH_SHARDS_FOR_REGULAR if craftCost > shardsCount else MonitorState.PARAMS_REGULAR
            enablePrint = prevState != nextState if craftCost > shardsCount else prevState != nextState or someValuesChanged
            self.__printingSoundEnabled = enablePrint
            self.__valueChanged = False if craftCost > shardsCount else someValuesChanged
            self.__stateChanged = prevState != nextState
            self.__updateRegularToysVisuals(tx, toyType, toySetting, toyRank, toyPlace)
            tx.setMonitorState(nextState)

    def _onInit(self):
        super(CraftMonitor, self)._onInit()
        self._viewModel.onPlaySound += self.__onPlayPrintSound
        self._viewModel.onStopSound += self.__onStopPrintSound
        self.updateData()

    def _initData(self, ctrl):
        self._viewModel.setMonitorState(MonitorState.INITIAL)

    def _onDestroy(self):
        self._viewModel.onPlaySound -= self.__onPlayPrintSound
        self._viewModel.onStopSound -= self.__onStopPrintSound

    def __hasRandomRegularToyParam(self):
        toyType, toySetting, toyRank, _ = self._nodesHolder.regularToysBlock.getToyConfig()
        return RANDOM_TOY_CONFIG_INDEX in (toyType, toySetting, toyRank)

    def __checkForUpdateRegularToysVisuals(self, model):
        toyType, toySetting, toyRank, toyPlace = self._nodesHolder.regularToysBlock.getToyConfig()
        prevToyType = model.getType()
        prevToySetting = model.getSetting()
        prevToyRank = model.getLevel()
        prevToyPlace = model.getObjectType()
        hasChange = prevToyType != TOY_TYPE_STRINGS[toyType] or prevToySetting != TOY_SETTING_STRINGS[toySetting] or prevToyRank != TOY_RANKS_STRINGS[toyRank] or prevToyPlace != TOY_PLACES_STRINGS[toyPlace]
        return (hasChange,
         toyType,
         toySetting,
         toyRank,
         toyPlace)

    def __updateRegularToysVisuals(self, model, toyType, toySetting, toyRank, toyPlace):
        model.setType(TOY_TYPE_STRINGS[toyType])
        model.setLevel(TOY_RANKS_STRINGS[toyRank])
        model.setSetting(TOY_SETTING_STRINGS[toySetting])
        model.setObjectType(TOY_PLACES_STRINGS[toyPlace])

    def __isFullRegularToysGroup(self):
        toyType, toySetting, toyRank = self._nodesHolder.craftCostBlock.getCraftParams()
        return self._nyController.isFullRegularToysGroup(toyType, toySetting, toyRank)

    def __isRegularToysCollected(self):
        collectionDistribution = self._itemsCache.items.festivity.getCollectionDistributions()
        for collectionName in YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR_STR, useMega=False):
            collectionID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[collectionName]
            expectedToyCount = new_year.g_cache.toyCountByCollectionID[collectionID]
            collectedToyCount = sum(collectionDistribution[collectionID])
            if expectedToyCount != collectedToyCount:
                return False

        return True

    def __onPlayPrintSound(self):
        if self.__printingSoundEnabled:
            self.__stopped = False
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CRAFT_MONITOR_PRINING_START)

    def __onStopPrintSound(self):
        self.__stopCounter = self.__stopCounter + 1
        eventCounter = self.__getEventCounter()
        if not self.__stopped and self.__stopCounter >= eventCounter:
            self.__stopped = True
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CRAFT_MONITOR_PRINTING_STOP)

    def __getEventCounter(self):
        return (1 if self.__stateChanged else 0) + (1 if self.__valueChanged else 0)

    def __cleanAnimationFlags(self):
        self.__printingSoundEnabled = False
        self.__stopCounter = 0
        self.__valueChanged = False
        self.__stateChanged = False
        self.__stopped = False
