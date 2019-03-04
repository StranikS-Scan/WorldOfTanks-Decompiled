# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/dialog_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from frameworks.wulf import View

class DialogWindowModel(ViewModel):
    __slots__ = ('onClosed', 'onBtnClicked')

    @property
    def buttons(self):
        return self._getViewModel(0)

    def getContent(self):
        return self._getView(1)

    def setContent(self, value):
        self._setView(1, value)

    def getBottomContent(self):
        return self._getView(2)

    def setBottomContent(self, value):
        self._setView(2, value)

    def getBalanceContent(self):
        return self._getView(3)

    def setBalanceContent(self, value):
        self._setView(3, value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getIconHighlight(self):
        return self._getResource(5)

    def setIconHighlight(self, value):
        self._setResource(5, value)

    def getAnimationHighlight(self):
        return self._getResource(6)

    def setAnimationHighlight(self, value):
        self._setResource(6, value)

    def getTitle(self):
        return self._getResource(7)

    def setTitle(self, value):
        self._setResource(7, value)

    def getTitleArgs(self):
        return self._getArray(8)

    def setTitleArgs(self, value):
        self._setArray(8, value)

    def getTitleFmtArgs(self):
        return self._getArray(9)

    def setTitleFmtArgs(self, value):
        self._setArray(9, value)

    def getIsTitleFmtArgsNamed(self):
        return self._getBool(10)

    def setIsTitleFmtArgsNamed(self, value):
        self._setBool(10, value)

    def getBackgroundImage(self):
        return self._getResource(11)

    def setBackgroundImage(self, value):
        self._setResource(11, value)

    def getShowSoundId(self):
        return self._getResource(12)

    def setShowSoundId(self, value):
        self._setResource(12, value)

    def getPreset(self):
        return self._getString(13)

    def setPreset(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(DialogWindowModel, self)._initialize()
        self._addViewModelProperty('buttons', UserListModel())
        self._addViewProperty('content')
        self._addViewProperty('bottomContent')
        self._addViewProperty('balanceContent')
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('iconHighlight', R.invalid())
        self._addResourceProperty('animationHighlight', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addArrayProperty('titleArgs', Array())
        self._addArrayProperty('titleFmtArgs', Array())
        self._addBoolProperty('isTitleFmtArgsNamed', True)
        self._addResourceProperty('backgroundImage', R.invalid())
        self._addResourceProperty('showSoundId', R.invalid())
        self._addStringProperty('preset', 'default')
        self.onClosed = self._addCommand('onClosed')
        self.onBtnClicked = self._addCommand('onBtnClicked')
