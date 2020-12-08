# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/dialog_button_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DialogButtonModel(ViewModel):
    __slots__ = ('onClicked',)
    BTN_SUBMIT = 'submit'
    BTN_CANCEL = 'cancel'
    BTN_RESEARCH = 'research'
    BTN_PURCHASE = 'purchase'

    def __init__(self, properties=11, commands=1):
        super(DialogButtonModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getRawLabel(self):
        return self._getString(1)

    def setRawLabel(self, value):
        self._setString(1, value)

    def getLabel(self):
        return self._getResource(2)

    def setLabel(self, value):
        self._setResource(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getDoSetFocus(self):
        return self._getBool(4)

    def setDoSetFocus(self, value):
        self._setBool(4, value)

    def getIcon(self):
        return self._getResource(5)

    def setIcon(self, value):
        self._setResource(5, value)

    def getIconAfterText(self):
        return self._getBool(6)

    def setIconAfterText(self, value):
        self._setBool(6, value)

    def getSoundDown(self):
        return self._getResource(7)

    def setSoundDown(self, value):
        self._setResource(7, value)

    def getTooltipHeader(self):
        return self._getResource(8)

    def setTooltipHeader(self, value):
        self._setResource(8, value)

    def getTooltipBody(self):
        return self._getResource(9)

    def setTooltipBody(self, value):
        self._setResource(9, value)

    def getIsVisible(self):
        return self._getBool(10)

    def setIsVisible(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(DialogButtonModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('rawLabel', '')
        self._addResourceProperty('label', R.invalid())
        self._addBoolProperty('isEnabled', True)
        self._addBoolProperty('doSetFocus', False)
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('iconAfterText', True)
        self._addResourceProperty('soundDown', R.invalid())
        self._addResourceProperty('tooltipHeader', R.invalid())
        self._addResourceProperty('tooltipBody', R.invalid())
        self._addBoolProperty('isVisible', True)
        self.onClicked = self._addCommand('onClicked')
