# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_books_lack_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class CrewBooksLackViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBuyBtnClick', 'onHangarBtnClick')

    def __init__(self, properties=8, commands=3):
        super(CrewBooksLackViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def noBooksList(self):
        return self._getViewModel(0)

    def getFlagIcon(self):
        return self._getResource(1)

    def setFlagIcon(self, value):
        self._setResource(1, value)

    def getScreenDescription(self):
        return self._getResource(2)

    def setScreenDescription(self, value):
        self._setResource(2, value)

    def getFooterDescription(self):
        return self._getResource(3)

    def setFooterDescription(self, value):
        self._setResource(3, value)

    def getFooterDescriptionFmtArgs(self):
        return self._getArray(4)

    def setFooterDescriptionFmtArgs(self, value):
        self._setArray(4, value)

    def getNoBooksOnStock(self):
        return self._getBool(5)

    def setNoBooksOnStock(self, value):
        self._setBool(5, value)

    def getIsDialogOpen(self):
        return self._getBool(6)

    def setIsDialogOpen(self, value):
        self._setBool(6, value)

    def getIsCrewBooksPurchaseEnabled(self):
        return self._getBool(7)

    def setIsCrewBooksPurchaseEnabled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(CrewBooksLackViewModel, self)._initialize()
        self._addViewModelProperty('noBooksList', ListModel())
        self._addResourceProperty('flagIcon', R.invalid())
        self._addResourceProperty('screenDescription', R.invalid())
        self._addResourceProperty('footerDescription', R.invalid())
        self._addArrayProperty('footerDescriptionFmtArgs', Array())
        self._addBoolProperty('noBooksOnStock', False)
        self._addBoolProperty('isDialogOpen', False)
        self._addBoolProperty('isCrewBooksPurchaseEnabled', True)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onHangarBtnClick = self._addCommand('onHangarBtnClick')
