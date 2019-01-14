# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/dialog_window_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from frameworks.wulf import View

class DialogWindowModel(ViewModel):
    __slots__ = ('onClosed', 'onBtnClicked')

    @property
    def buttons(self):
        return self._getViewModel(0)

    @property
    def currency(self):
        return self._getViewModel(1)

    def getContent(self):
        return self._getView(2)

    def setContent(self, value):
        self._setView(2, value)

    def getBottomContent(self):
        return self._getView(3)

    def setBottomContent(self, value):
        self._setView(3, value)

    def getHasCloseBtn(self):
        return self._getBool(4)

    def setHasCloseBtn(self, value):
        self._setBool(4, value)

    def getHasCurrencyBlock(self):
        return self._getBool(5)

    def setHasCurrencyBlock(self, value):
        self._setBool(5, value)

    def getBackgroundShineImage(self):
        return self._getResource(6)

    def setBackgroundShineImage(self, value):
        self._setResource(6, value)

    def getBackgroundImage(self):
        return self._getResource(7)

    def setBackgroundImage(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(DialogWindowModel, self)._initialize()
        self._addViewModelProperty('buttons', UserListModel())
        self._addViewModelProperty('currency', ListModel())
        self._addViewProperty('content')
        self._addViewProperty('bottomContent')
        self._addBoolProperty('hasCloseBtn', True)
        self._addBoolProperty('hasCurrencyBlock', False)
        self._addResourceProperty('backgroundShineImage', R.invalid())
        self._addResourceProperty('backgroundImage', R.invalid())
        self.onClosed = self._addCommand('onClosed')
        self.onBtnClicked = self._addCommand('onBtnClicked')
