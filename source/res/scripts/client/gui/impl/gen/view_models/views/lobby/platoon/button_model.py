# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/button_model.py
from frameworks.wulf import ViewModel

class ButtonModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(ButtonModel, self).__init__(properties=properties, commands=commands)

    def getCaption(self):
        return self._getString(0)

    def setCaption(self, value):
        self._setString(0, value)

    def getIsEnabled(self):
        return self._getBool(1)

    def setIsEnabled(self, value):
        self._setBool(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ButtonModel, self)._initialize()
        self._addStringProperty('caption', '')
        self._addBoolProperty('isEnabled', True)
        self._addStringProperty('description', '')
        self.onClick = self._addCommand('onClick')
