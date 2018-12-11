# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_main_view_model.py
import typing
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.new_year.components.ny_widget_model import NyWidgetModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class NewYearMainViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onSideBarBtnClick', 'onCraftBtnClick', 'onAlbumBtnClick', 'onGetPartsBtnClick', 'onRewardsBtnClick')

    @property
    def sideBar(self):
        return self._getViewModel(0)

    @property
    def widget(self):
        return self._getViewModel(1)

    def getPartsCount(self):
        return self._getNumber(2)

    def setPartsCount(self, value):
        self._setNumber(2, value)

    def getLootBoxEntryPoint(self):
        return self._getView(3)

    def setLootBoxEntryPoint(self, value):
        self._setView(3, value)

    def getIsDragging(self):
        return self._getBool(4)

    def setIsDragging(self, value):
        self._setBool(4, value)

    def getIsVisible(self):
        return self._getBool(5)

    def setIsVisible(self, value):
        self._setBool(5, value)

    def getAnchor0(self):
        return self._getView(6)

    def setAnchor0(self, value):
        self._setView(6, value)

    def getAnchor1(self):
        return self._getView(7)

    def setAnchor1(self, value):
        self._setView(7, value)

    def getAnchor2(self):
        return self._getView(8)

    def setAnchor2(self, value):
        self._setView(8, value)

    def getAnchor3(self):
        return self._getView(9)

    def setAnchor3(self, value):
        self._setView(9, value)

    def getAnchor4(self):
        return self._getView(10)

    def setAnchor4(self, value):
        self._setView(10, value)

    def getAnchor5(self):
        return self._getView(11)

    def setAnchor5(self, value):
        self._setView(11, value)

    def getAnchor6(self):
        return self._getView(12)

    def setAnchor6(self, value):
        self._setView(12, value)

    def getAnchor7(self):
        return self._getView(13)

    def setAnchor7(self, value):
        self._setView(13, value)

    def getAnchor8(self):
        return self._getView(14)

    def setAnchor8(self, value):
        self._setView(14, value)

    def _initialize(self):
        super(NewYearMainViewModel, self)._initialize()
        self._addViewModelProperty('sideBar', ListModel())
        self._addViewModelProperty('widget', NyWidgetModel())
        self._addNumberProperty('partsCount', 0)
        self._addViewProperty('lootBoxEntryPoint')
        self._addBoolProperty('isDragging', False)
        self._addBoolProperty('isVisible', True)
        self._addViewProperty('anchor0')
        self._addViewProperty('anchor1')
        self._addViewProperty('anchor2')
        self._addViewProperty('anchor3')
        self._addViewProperty('anchor4')
        self._addViewProperty('anchor5')
        self._addViewProperty('anchor6')
        self._addViewProperty('anchor7')
        self._addViewProperty('anchor8')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onSideBarBtnClick = self._addCommand('onSideBarBtnClick')
        self.onCraftBtnClick = self._addCommand('onCraftBtnClick')
        self.onAlbumBtnClick = self._addCommand('onAlbumBtnClick')
        self.onGetPartsBtnClick = self._addCommand('onGetPartsBtnClick')
        self.onRewardsBtnClick = self._addCommand('onRewardsBtnClick')
