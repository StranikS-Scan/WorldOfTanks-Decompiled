# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/dialog_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.windows.dialog_window_adaptive_settings_model import DialogWindowAdaptiveSettingsModel

class DialogWindowModel(ViewModel):
    __slots__ = ('onClosed', 'onBtnClicked')

    def __init__(self, properties=17, commands=2):
        super(DialogWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def buttons(self):
        return self._getViewModel(0)

    @staticmethod
    def getButtonsType():
        return UserListModel

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getIconHighlight(self):
        return self._getResource(2)

    def setIconHighlight(self, value):
        self._setResource(2, value)

    def getAnimationHighlight(self):
        return self._getResource(3)

    def setAnimationHighlight(self, value):
        self._setResource(3, value)

    def getTitle(self):
        return self._getResource(4)

    def setTitle(self, value):
        self._setResource(4, value)

    def getFormattedTitle(self):
        return self._getString(5)

    def setFormattedTitle(self, value):
        self._setString(5, value)

    def getTitleArgs(self):
        return self._getArray(6)

    def setTitleArgs(self, value):
        self._setArray(6, value)

    def getTitleFmtArgs(self):
        return self._getArray(7)

    def setTitleFmtArgs(self, value):
        self._setArray(7, value)

    def getIsTitleFmtArgsNamed(self):
        return self._getBool(8)

    def setIsTitleFmtArgsNamed(self, value):
        self._setBool(8, value)

    def getBackgroundImage(self):
        return self._getResource(9)

    def setBackgroundImage(self, value):
        self._setResource(9, value)

    def getShowSoundId(self):
        return self._getResource(10)

    def setShowSoundId(self, value):
        self._setResource(10, value)

    def getPreset(self):
        return self._getString(11)

    def setPreset(self, value):
        self._setString(11, value)

    def getHasBalance(self):
        return self._getBool(12)

    def setHasBalance(self, value):
        self._setBool(12, value)

    def getHasBottomContent(self):
        return self._getBool(13)

    def setHasBottomContent(self, value):
        self._setBool(13, value)

    def getIsDividerVisible(self):
        return self._getBool(14)

    def setIsDividerVisible(self, value):
        self._setBool(14, value)

    def getDialogTitleTextStyle(self):
        return self._getString(15)

    def setDialogTitleTextStyle(self, value):
        self._setString(15, value)

    def getAdaptiveSettings(self):
        return self._getArray(16)

    def setAdaptiveSettings(self, value):
        self._setArray(16, value)

    @staticmethod
    def getAdaptiveSettingsType():
        return DialogWindowAdaptiveSettingsModel

    def _initialize(self):
        super(DialogWindowModel, self)._initialize()
        self._addViewModelProperty('buttons', UserListModel())
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('iconHighlight', R.invalid())
        self._addResourceProperty('animationHighlight', R.invalid())
        self._addResourceProperty('title', R.invalid())
        self._addStringProperty('formattedTitle', '')
        self._addArrayProperty('titleArgs', Array())
        self._addArrayProperty('titleFmtArgs', Array())
        self._addBoolProperty('isTitleFmtArgsNamed', True)
        self._addResourceProperty('backgroundImage', R.invalid())
        self._addResourceProperty('showSoundId', R.invalid())
        self._addStringProperty('preset', 'default')
        self._addBoolProperty('hasBalance', False)
        self._addBoolProperty('hasBottomContent', False)
        self._addBoolProperty('isDividerVisible', True)
        self._addStringProperty('dialogTitleTextStyle', '')
        self._addArrayProperty('adaptiveSettings', Array())
        self.onClosed = self._addCommand('onClosed')
        self.onBtnClicked = self._addCommand('onBtnClicked')
