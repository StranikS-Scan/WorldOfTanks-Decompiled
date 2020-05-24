# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/style_unlocked_view/style_unlocked_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class StyleUnlockedViewModel(ViewModel):
    __slots__ = ('onOkClick', 'onSecondaryClick', 'onAnimationSound')

    def __init__(self, properties=5, commands=3):
        super(StyleUnlockedViewModel, self).__init__(properties=properties, commands=commands)

    def getTankLevel(self):
        return self._getString(0)

    def setTankLevel(self, value):
        self._setString(0, value)

    def getTankTypeIcon(self):
        return self._getResource(1)

    def setTankTypeIcon(self, value):
        self._setResource(1, value)

    def getTankName(self):
        return self._getString(2)

    def setTankName(self, value):
        self._setString(2, value)

    def getSecondaryButtonTooltip(self):
        return self._getString(3)

    def setSecondaryButtonTooltip(self, value):
        self._setString(3, value)

    def getSecondaryButtonEnabled(self):
        return self._getBool(4)

    def setSecondaryButtonEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(StyleUnlockedViewModel, self)._initialize()
        self._addStringProperty('tankLevel', '')
        self._addResourceProperty('tankTypeIcon', R.invalid())
        self._addStringProperty('tankName', '')
        self._addStringProperty('secondaryButtonTooltip', '')
        self._addBoolProperty('secondaryButtonEnabled', False)
        self.onOkClick = self._addCommand('onOkClick')
        self.onSecondaryClick = self._addCommand('onSecondaryClick')
        self.onAnimationSound = self._addCommand('onAnimationSound')
