# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/nation_change/nation_change_tankman_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NationChangeTankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NationChangeTankmanModel, self).__init__(properties=properties, commands=commands)

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getInvID(self):
        return self._getNumber(1)

    def setInvID(self, value):
        self._setNumber(1, value)

    def getIsSimpleTooltip(self):
        return self._getBool(2)

    def setIsSimpleTooltip(self, value):
        self._setBool(2, value)

    def getSimpleTooltipHeader(self):
        return self._getString(3)

    def setSimpleTooltipHeader(self, value):
        self._setString(3, value)

    def getSimpleTooltipBody(self):
        return self._getString(4)

    def setSimpleTooltipBody(self, value):
        self._setString(4, value)

    def getIsDog(self):
        return self._getBool(5)

    def setIsDog(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NationChangeTankmanModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addNumberProperty('invID', 0)
        self._addBoolProperty('isSimpleTooltip', False)
        self._addStringProperty('simpleTooltipHeader', '')
        self._addStringProperty('simpleTooltipBody', '')
        self._addBoolProperty('isDog', False)
