# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/style_option_model.py
from frameworks.wulf import ViewModel

class StyleOptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(StyleOptionModel, self).__init__(properties=properties, commands=commands)

    def getStyle(self):
        return self._getString(0)

    def setStyle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getTank(self):
        return self._getString(2)

    def setTank(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(StyleOptionModel, self)._initialize()
        self._addStringProperty('style', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('tank', '')
