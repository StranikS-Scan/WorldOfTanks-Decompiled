# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/universal_flag/details/universal_flag_background.py
from frameworks.wulf import ViewModel

class UniversalFlagBackground(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(UniversalFlagBackground, self).__init__(properties=properties, commands=commands)

    def getActive(self):
        return self._getString(0)

    def setActive(self, value):
        self._setString(0, value)

    def getActiveHover(self):
        return self._getString(1)

    def setActiveHover(self, value):
        self._setString(1, value)

    def getDisabled(self):
        return self._getString(2)

    def setDisabled(self, value):
        self._setString(2, value)

    def getDisabledHover(self):
        return self._getString(3)

    def setDisabledHover(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(UniversalFlagBackground, self)._initialize()
        self._addStringProperty('active', '')
        self._addStringProperty('activeHover', '')
        self._addStringProperty('disabled', '')
        self._addStringProperty('disabledHover', '')
