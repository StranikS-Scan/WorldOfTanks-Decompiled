# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_album_page_view_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearAlbumPageViewModel(ViewModel):
    __slots__ = ('onChangeData', 'onFadeOnFinish', 'onBackBtnClick', 'onCloseBtnClick', 'onToyClick', 'onPreChangeTypeName', 'onPreChangeIndex', 'onPreChangeRank')

    @property
    def toysList(self):
        return self._getViewModel(0)

    def getCurrentType(self):
        return self._getString(1)

    def setCurrentType(self, value):
        self._setString(1, value)

    def getCurrentRank(self):
        return self._getNumber(2)

    def setCurrentRank(self, value):
        self._setNumber(2, value)

    def getCurrentIndex(self):
        return self._getNumber(3)

    def setCurrentIndex(self, value):
        self._setNumber(3, value)

    def getTotalIndexes(self):
        return self._getNumber(4)

    def setTotalIndexes(self, value):
        self._setNumber(4, value)

    def getTypesList(self):
        return self._getArray(5)

    def setTypesList(self, value):
        self._setArray(5, value)

    def getHasStamp(self):
        return self._getBool(6)

    def setHasStamp(self, value):
        self._setBool(6, value)

    def getIsGetStamp(self):
        return self._getBool(7)

    def setIsGetStamp(self, value):
        self._setBool(7, value)

    def getFadeOut(self):
        return self._getBool(8)

    def setFadeOut(self, value):
        self._setBool(8, value)

    def getFadeOutList(self):
        return self._getBool(9)

    def setFadeOutList(self, value):
        self._setBool(9, value)

    def getCurrentRomanRank(self):
        return self._getString(10)

    def setCurrentRomanRank(self, value):
        self._setString(10, value)

    def getCanChange(self):
        return self._getBool(11)

    def setCanChange(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(NewYearAlbumPageViewModel, self)._initialize()
        self._addViewModelProperty('toysList', UserListModel())
        self._addStringProperty('currentType', '')
        self._addNumberProperty('currentRank', 0)
        self._addNumberProperty('currentIndex', 0)
        self._addNumberProperty('totalIndexes', 0)
        self._addArrayProperty('typesList', Array())
        self._addBoolProperty('hasStamp', False)
        self._addBoolProperty('isGetStamp', False)
        self._addBoolProperty('fadeOut', False)
        self._addBoolProperty('fadeOutList', False)
        self._addStringProperty('currentRomanRank', '')
        self._addBoolProperty('canChange', True)
        self.onChangeData = self._addCommand('onChangeData')
        self.onFadeOnFinish = self._addCommand('onFadeOnFinish')
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onToyClick = self._addCommand('onToyClick')
        self.onPreChangeTypeName = self._addCommand('onPreChangeTypeName')
        self.onPreChangeIndex = self._addCommand('onPreChangeIndex')
        self.onPreChangeRank = self._addCommand('onPreChangeRank')
