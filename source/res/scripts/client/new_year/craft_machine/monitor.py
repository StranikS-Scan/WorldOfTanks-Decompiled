# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/monitor.py
from helpers import dependency
from skeletons.new_year import INewYearController
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from .data_nodes import ViewModelDataNode
from .shared_stuff import AntiduplicatorState, MegaDeviceState, RANDOM_TOY_CONFIG_INDEX
from .texts import TOY_TYPE_STRINGS, TOY_RANKS_STRINGS, TOY_SETTING_STRINGS, TOY_PLACES_STRINGS

class CraftMonitor(ViewModelDataNode):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, viewModel):
        super(CraftMonitor, self).__init__(viewModel)
        self.__cleanAnimationFlags()

    def updateData(self):
        with self._viewModel.transaction() as tx:
            self.__cleanAnimationFlags()
            prevState = tx.getState()
            shardsCount = self._nodesHolder.shardsStorage.getShards()
            shardsChanged = tx.getShardsCount() != shardsCount
            tx.setShardsCount(shardsCount)
            uniqueMegaToysCount = self._nodesHolder.megaToysStorage.getUniqueMegaToysCount()
            megaToysChanged = tx.getCountMegaToys() != uniqueMegaToysCount
            tx.setCountMegaToys(uniqueMegaToysCount)
            prevAntidublicatorState = tx.getAntiduplicateEnabled()
            antiduplicatorChanged = False
            antiduplicatorState = self._nodesHolder.antiduplicator.getState()
            isAntiduplicatorErrorState = antiduplicatorState == AntiduplicatorState.ERROR
            isAntiduplicatorActiveState = antiduplicatorState == AntiduplicatorState.ACTIVE
            isAntiduplicatorInactiveState = antiduplicatorState == AntiduplicatorState.INACTIVE
            megaDeviceState = self._nodesHolder.megaDevice.getState()
            if megaDeviceState == MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR:
                self.__printingSoundEnabled = prevState != tx.FULL_MEGA or shardsChanged
                self.__valueChanged = shardsChanged
                self.__stateChanged = prevState != tx.FULL_MEGA
                tx.setState(tx.FULL_MEGA)
                return
            hasRandomRegularToyParam = self.__hasRandomRegularToyParam()
            if isAntiduplicatorActiveState:
                tx.setAntiduplicateEnabled(True)
                antiduplicatorChanged = not prevAntidublicatorState
            elif isAntiduplicatorInactiveState:
                tx.setAntiduplicateEnabled(False)
                antiduplicatorChanged = prevAntidublicatorState
            if not isAntiduplicatorInactiveState:
                if self.__isRegularToysCollected():
                    self.__printingSoundEnabled = prevState != tx.FULL_REGULAR or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != tx.FULL_REGULAR
                    tx.setState(tx.FULL_REGULAR)
                    return
                if hasRandomRegularToyParam:
                    self.__printingSoundEnabled = prevState != tx.HAS_RANDOM_PARAM or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != tx.HAS_RANDOM_PARAM
                    tx.setState(tx.HAS_RANDOM_PARAM)
                    return
                if self.__isFullRegularToysGroup():
                    self.__printingSoundEnabled = prevState != tx.FULL_REGULAR_SUBGROUP or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != tx.FULL_REGULAR_SUBGROUP
                    tx.setState(tx.FULL_REGULAR_SUBGROUP)
                    return
                if isAntiduplicatorErrorState:
                    self.__printingSoundEnabled = prevState != tx.HAS_NOT_FILLERS or shardsChanged
                    self.__valueChanged = shardsChanged
                    self.__stateChanged = prevState != tx.HAS_NOT_FILLERS
                    tx.setState(tx.HAS_NOT_FILLERS)
                    return
            if shardsCount == 0:
                self.__printingSoundEnabled = prevState != tx.SHARDS_NOT_AVAILABLE
                self.__stateChanged = prevState != tx.SHARDS_NOT_AVAILABLE
                tx.setState(tx.SHARDS_NOT_AVAILABLE)
                return
            craftCost = self._nodesHolder.craftCostBlock.getCraftCost()
            if megaDeviceState == MegaDeviceState.ACTIVE:
                if craftCost > shardsCount:
                    self.__printingSoundEnabled = prevState != tx.NOT_ENOUGH_SHARDS_FOR_MEGA
                    self.__stateChanged = prevState != tx.NOT_ENOUGH_SHARDS_FOR_MEGA
                    tx.setState(tx.NOT_ENOUGH_SHARDS_FOR_MEGA)
                else:
                    self.__printingSoundEnabled = prevState != tx.PARAMS_MEGA or shardsChanged or megaToysChanged
                    self.__valueChanged = shardsChanged or megaToysChanged
                    self.__stateChanged = prevState != tx.PARAMS_MEGA
                    tx.setState(tx.PARAMS_MEGA)
                return
            hasChange, toyType, toySetting, toyRank, toyPlace = self.__checkForUpdateRegularToysVisuals(tx)
            someValuesChanged = hasChange or antiduplicatorChanged or shardsChanged
            nextState = tx.NOT_ENOUGH_SHARDS_FOR_REGULAR if craftCost > shardsCount else tx.PARAMS_REGULAR
            enablePrint = prevState != nextState if craftCost > shardsCount else prevState != nextState or someValuesChanged
            self.__printingSoundEnabled = enablePrint
            self.__valueChanged = False if craftCost > shardsCount else someValuesChanged
            self.__stateChanged = prevState != nextState
            self.__updateRegularToysVisuals(tx, toyType, toySetting, toyRank, toyPlace)
            tx.setState(nextState)

    def _onInit(self):
        super(CraftMonitor, self)._onInit()
        self._viewModel.onPlaySound += self.__onPlayPrintSound
        self._viewModel.onStopSound += self.__onStopPrintSound
        self.updateData()

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
        return self._nyController.isRegularToysCollected()

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
