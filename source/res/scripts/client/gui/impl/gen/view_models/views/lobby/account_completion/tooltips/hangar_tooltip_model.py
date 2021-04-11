# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/tooltips/hangar_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class HangarTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(HangarTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getText(self):
        return self._getResource(1)

    def setText(self, value):
        self._setResource(1, value)

    def getTextInner(self):
        return self._getResource(2)

    def setTextInner(self, value):
        self._setResource(2, value)

    def getEmail(self):
        return self._getString(3)

    def setEmail(self, value):
        self._setString(3, value)

    def getBonuses(self):
        return self._getArray(4)

    def setBonuses(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(HangarTooltipModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('text', R.invalid())
        self._addResourceProperty('textInner', R.invalid())
        self._addStringProperty('email', '')
        self._addArrayProperty('bonuses', Array())
