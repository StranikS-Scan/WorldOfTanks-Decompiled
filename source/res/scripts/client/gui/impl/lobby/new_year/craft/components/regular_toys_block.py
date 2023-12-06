# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/craft/components/regular_toys_block.py
from gui.impl.new_year.sounds import RANDOM_STYLE_BOX, NewYearSoundsManager
from items.components.ny_constants import ToySettings, TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA, RANDOM_TYPE
from shared_utils import getSafeFromCollection
from .data_nodes import ViewModelDataNode
from .shared_stuff import mapToyParamsFromCraftUiToSrv

class RegularToysBlock(ViewModelDataNode):

    def getToyConfig(self):
        toyIndex = TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA.index(self._viewModel.getSelectedToyType())
        toySetting = self._viewModel.getSelectedCollectionIndex()
        toyRank = self._viewModel.getCurrentToyLevelIndex()
        category = self._viewModel.getCurrentToyCategory()
        return (toyIndex,
         toySetting,
         toyRank,
         category)

    def updateData(self):
        pass

    def _onInit(self):
        super(RegularToysBlock, self)._onInit()
        self._viewModel.onSettingChanged += self.__onSettingChanged
        self._viewModel.onLevelChanged += self.__onLevelChanged
        self._viewModel.onTypeChanged += self.__onTypeChanged

    def _onDestroy(self):
        self._viewModel.onSettingChanged -= self.__onSettingChanged
        self._viewModel.onLevelChanged -= self.__onLevelChanged
        self._viewModel.onTypeChanged -= self.__onTypeChanged
        super(RegularToysBlock, self)._onDestroy()

    def _initData(self, ctrl):
        self._viewModel.setSelectedToyType(ctrl.getRegularSelectedToyType())
        self._viewModel.setSelectedCollectionIndex(ctrl.selectedToySettingIdx)
        self._viewModel.setCurrentToyLevelIndex(ctrl.selectedToyRankIdx)
        self._viewModel.setFillerShardsCost(ctrl.fillerShardsCost)
        self._viewModel.setCurrentToyCategory(ctrl.getToyCategoryType())

    def _saveData(self, ctrl):
        ctrl.selectedToyTypeIdx = TOY_TYPES_FOR_OBJECTS_WITH_RANDOM_WITHOUT_MEGA.index(self._viewModel.getSelectedToyType())
        ctrl.selectedToySettingIdx = self._viewModel.getSelectedCollectionIndex()
        ctrl.selectedToyRankIdx = self._viewModel.getCurrentToyLevelIndex()

    def __onSettingChanged(self, settingData):
        settingData = int(settingData.get('setting', RANDOM_TYPE))
        self._viewModel.setSelectedCollectionIndex(settingData)
        self.__setSoundStyles()
        self._raiseOnDataChanged()

    def __onLevelChanged(self, levelData):
        level = int(levelData.get('level', 0))
        self._viewModel.setCurrentToyLevelIndex(level)
        self._raiseOnDataChanged()

    def __onTypeChanged(self, typeData):
        selectedToyType = typeData.get('type', RANDOM_TYPE)
        groupName = typeData.get('groupName', None)
        self._viewModel.setSelectedToyType(selectedToyType)
        self._viewModel.setCurrentToyCategory(groupName)
        self._raiseOnDataChanged()
        return

    def __setSoundStyles(self):
        toySettingIdx = self._viewModel.getSelectedCollectionIndex()
        _, toySettingIdx, _ = mapToyParamsFromCraftUiToSrv(0, toySettingIdx, 0)
        toySetting = getSafeFromCollection(ToySettings.NEW, toySettingIdx, default=RANDOM_STYLE_BOX)
        NewYearSoundsManager.setStylesSwitchBox(toySetting)
