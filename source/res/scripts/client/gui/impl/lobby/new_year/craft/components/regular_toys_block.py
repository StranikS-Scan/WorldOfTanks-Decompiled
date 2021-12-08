# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/regular_toys_block.py
from gui.impl.new_year.sounds import RANDOM_STYLE_BOX, NewYearSoundsManager, NewYearSoundEvents
from items.components.ny_constants import ToySettings, TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA, RANDOM_TYPE
from shared_utils import getSafeFromCollection
from .data_nodes import ViewModelDataNode
from .shared_stuff import MegaDeviceState, mapToyParamsFromCraftUiToSrv

class RegularToysBlock(ViewModelDataNode):

    def getToyConfig(self):
        toyIndex = TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA.index(self._viewModel.getSelectedType())
        toySetting = self._viewModel.getCurrentSettingIndex()
        toyRank = self._viewModel.getCurrentLevelIndex()
        category = self._viewModel.getCurrentCategory()
        return (toyIndex,
         toySetting,
         toyRank,
         category)

    def updateData(self):
        self.__updateMegaDeviceState()

    def _onInit(self):
        super(RegularToysBlock, self)._onInit()
        self._viewModel.onSettingChanged += self.__onSettingChanged
        self._viewModel.onTypeChanged += self.__onTypeChanged

    def _onDestroy(self):
        self._viewModel.onSettingChanged -= self.__onSettingChanged
        self._viewModel.onTypeChanged -= self.__onTypeChanged
        super(RegularToysBlock, self)._onDestroy()

    def _initData(self, ctrl):
        self._viewModel.setSelectedType(ctrl.getRegularSelectedToyType())
        self._viewModel.setCurrentSettingIndex(ctrl.selectedToySettingIdx)
        self._viewModel.setCurrentLevelIndex(ctrl.selectedToyRankIdx)
        self._viewModel.setFillerShardsCost(ctrl.fillerShardsCost)
        self._viewModel.setCurrentCategory(ctrl.getToyCategoryType())

    def _saveData(self, ctrl):
        ctrl.selectedToyTypeIdx = TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA.index(self._viewModel.getSelectedType())
        ctrl.selectedToySettingIdx = self._viewModel.getCurrentSettingIndex()
        ctrl.selectedToyRankIdx = self._viewModel.getCurrentLevelIndex()

    def __onSettingChanged(self, settingData):
        if not self.__isBlockActive():
            return
        settingData = int(settingData.get('setting', RANDOM_TYPE))
        self._viewModel.setCurrentSettingIndex(settingData)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CRAFT_CHANGE_TOYS_SETTING)
        self.__setSoundStyles()
        self._raiseOnDataChanged()

    def __onTypeChanged(self, typeData):
        if not self.__isBlockActive():
            return
        else:
            selectedType = typeData.get('type', RANDOM_TYPE)
            groupName = typeData.get('groupName', None)
            self._viewModel.setSelectedType(selectedType)
            self._viewModel.setCurrentCategory(groupName)
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CRAFT_CHANGE_TOY_TYPE)
            self._raiseOnDataChanged()
            return

    def __updateMegaDeviceState(self):
        state = self._nodesHolder.megaDevice.getState()
        self._viewModel.setEnabled(state == MegaDeviceState.INACTIVE)

    def __setSoundStyles(self):
        toySettingIdx = self._viewModel.getCurrentSettingIndex()
        _, toySettingIdx, _ = mapToyParamsFromCraftUiToSrv(0, toySettingIdx, 0)
        toySetting = getSafeFromCollection(ToySettings.NEW, toySettingIdx, default=RANDOM_STYLE_BOX)
        NewYearSoundsManager.setStylesSwitchBox(toySetting)

    def __isBlockActive(self):
        return self._nodesHolder.megaDevice.getState() not in MegaDeviceState.ACTIVATED
