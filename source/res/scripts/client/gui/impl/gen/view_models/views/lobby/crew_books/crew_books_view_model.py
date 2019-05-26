# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_books_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class CrewBooksViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onTankmanClick', 'onCrewBookClick', 'onBookUse', 'onBuyBtnClick')

    @property
    def crewBookTankmenList(self):
        return self._getViewModel(0)

    def getFlagIcon(self):
        return self._getResource(1)

    def setFlagIcon(self, value):
        self._setResource(1, value)

    def getFooterIcon(self):
        return self._getResource(2)

    def setFooterIcon(self, value):
        self._setResource(2, value)

    def getScreenDesc(self):
        return self._getResource(3)

    def setScreenDesc(self, value):
        self._setResource(3, value)

    def getFooterTitle(self):
        return self._getResource(4)

    def setFooterTitle(self, value):
        self._setResource(4, value)

    def getIsFooterAlert(self):
        return self._getBool(5)

    def setIsFooterAlert(self, value):
        self._setBool(5, value)

    def getIsInvalidTooltipEnable(self):
        return self._getBool(6)

    def setIsInvalidTooltipEnable(self, value):
        self._setBool(6, value)

    def getIsSimpleInvalidTooltip(self):
        return self._getBool(7)

    def setIsSimpleInvalidTooltip(self, value):
        self._setBool(7, value)

    def getTooltipBody(self):
        return self._getResource(8)

    def setTooltipBody(self, value):
        self._setResource(8, value)

    def getFooterTitleFmtArgs(self):
        return self._getArray(9)

    def setFooterTitleFmtArgs(self, value):
        self._setArray(9, value)

    def getIsFooterDescriptionVisible(self):
        return self._getBool(10)

    def setIsFooterDescriptionVisible(self, value):
        self._setBool(10, value)

    def getIsBookUseEnable(self):
        return self._getBool(11)

    def setIsBookUseEnable(self, value):
        self._setBool(11, value)

    def getIsDialogOpen(self):
        return self._getBool(12)

    def setIsDialogOpen(self, value):
        self._setBool(12, value)

    def getIsBookUseSucces(self):
        return self._getBool(13)

    def setIsBookUseSucces(self, value):
        self._setBool(13, value)

    def getCrewBookItemList(self):
        return self._getArray(14)

    def setCrewBookItemList(self, value):
        self._setArray(14, value)

    def _initialize(self):
        super(CrewBooksViewModel, self)._initialize()
        self._addViewModelProperty('crewBookTankmenList', ListModel())
        self._addResourceProperty('flagIcon', R.invalid())
        self._addResourceProperty('footerIcon', R.invalid())
        self._addResourceProperty('screenDesc', R.invalid())
        self._addResourceProperty('footerTitle', R.invalid())
        self._addBoolProperty('isFooterAlert', False)
        self._addBoolProperty('isInvalidTooltipEnable', False)
        self._addBoolProperty('isSimpleInvalidTooltip', False)
        self._addResourceProperty('tooltipBody', R.invalid())
        self._addArrayProperty('footerTitleFmtArgs', Array())
        self._addBoolProperty('isFooterDescriptionVisible', True)
        self._addBoolProperty('isBookUseEnable', False)
        self._addBoolProperty('isDialogOpen', False)
        self._addBoolProperty('isBookUseSucces', False)
        self._addArrayProperty('crewBookItemList', Array())
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onTankmanClick = self._addCommand('onTankmanClick')
        self.onCrewBookClick = self._addCommand('onCrewBookClick')
        self.onBookUse = self._addCommand('onBookUse')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
