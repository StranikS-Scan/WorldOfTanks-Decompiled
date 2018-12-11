# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_decorations_popover_model.py
import typing
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearDecorationsPopoverModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onGetShardsBtnClick', 'onDecorationPlusClick', 'onQuestsBtnClick', 'onSlotStatusIsNewChanged')

    @property
    def slotsList(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def getSetting(self):
        return self._getString(3)

    def setSetting(self, value):
        self._setString(3, value)

    def getDecorationImage(self):
        return self._getResource(4)

    def setDecorationImage(self, value):
        self._setResource(4, value)

    def getRankImage(self):
        return self._getResource(5)

    def setRankImage(self, value):
        self._setResource(5, value)

    def getIsEmpty(self):
        return self._getBool(6)

    def setIsEmpty(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NewYearDecorationsPopoverModel, self)._initialize()
        self._addViewModelProperty('slotsList', UserListModel())
        self._addResourceProperty('title', Resource.INVALID)
        self._addResourceProperty('description', Resource.INVALID)
        self._addStringProperty('setting', '')
        self._addResourceProperty('decorationImage', Resource.INVALID)
        self._addResourceProperty('rankImage', Resource.INVALID)
        self._addBoolProperty('isEmpty', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onGetShardsBtnClick = self._addCommand('onGetShardsBtnClick')
        self.onDecorationPlusClick = self._addCommand('onDecorationPlusClick')
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
