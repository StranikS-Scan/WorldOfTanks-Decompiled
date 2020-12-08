# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/craft_machine/regular_toys_block.py
from gui.impl.new_year.sounds import RANDOM_STYLE_BOX, NewYearSoundsManager, NewYearSoundEvents
from items.components.ny_constants import ToySettings
from .data_nodes import ViewModelDataNode
from .shared_stuff import MegaDeviceState, mapToyParamsFromCraftUiToSrv

class RegularToysBlock(ViewModelDataNode):

    def getToyConfig(self):
        toyType = self._viewModel.getCurrentTypeIndex()
        toySetting = self._viewModel.getCurrentSettingIndex()
        toyRank = self._viewModel.getCurrentLevelIndex()
        tabTypes = self._viewModel.getTabTypes()
        toyItem = tabTypes[toyType]
        toyPlace = toyItem.getGroupName()
        return (toyType,
         toySetting,
         toyRank,
         toyPlace)

    def updateData(self):
        self.__checkMegaDeviceState()

    def _onInit(self):
        super(RegularToysBlock, self)._onInit()
        self._viewModel.onConfigChanged += self.__onRegularConfigChanged

    def _onDestroy(self):
        self._viewModel.onConfigChanged -= self.__onRegularConfigChanged
        super(RegularToysBlock, self)._onDestroy()

    def _initData(self, ctrl):
        self._viewModel.setCurrentTypeIndex(ctrl.selectedToyTypeIdx)
        self._viewModel.setCurrentSettingIndex(ctrl.selectedToySettingIdx)
        self._viewModel.setCurrentLevelIndex(ctrl.selectedToyRankIdx)

    def _saveData(self, ctrl):
        ctrl.selectedToyTypeIdx = self._viewModel.getCurrentTypeIndex()
        ctrl.selectedToySettingIdx = self._viewModel.getCurrentSettingIndex()
        ctrl.selectedToyRankIdx = self._viewModel.getCurrentLevelIndex()

    def __onRegularConfigChanged(self, typeChangedData):
        typeChangedData = int(typeChangedData.get('type', -1))
        if typeChangedData == self._viewModel.SETTING:
            self.__setSoundStyles()
        if typeChangedData in (self._viewModel.SETTING, self._viewModel.LEVEL):
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CHOICE_TOYS)
        self._raiseOnDataChanged()

    def __checkMegaDeviceState(self):
        megaDeviceState = self._nodesHolder.megaDevice.getState()
        if megaDeviceState == MegaDeviceState.INACTIVE:
            self._viewModel.setEnabled(True)
        else:
            self._viewModel.setEnabled(False)

    def __setSoundStyles(self):
        toySettingIdx = self._viewModel.getCurrentSettingIndex()
        _, toySettingIdx, _ = mapToyParamsFromCraftUiToSrv(0, toySettingIdx, 0)
        toySetting = ToySettings.NEW[toySettingIdx] if toySettingIdx >= 0 and toySettingIdx < len(ToySettings.NEW) else RANDOM_STYLE_BOX
        NewYearSoundsManager.setStylesSwitchBox(toySetting)
