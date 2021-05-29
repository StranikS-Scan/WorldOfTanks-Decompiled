# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_price.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_value_price import BlueprintValuePrice

class BlueprintPrice(BlueprintValuePrice):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BlueprintPrice, self).__init__(properties=properties, commands=commands)

    def getIconBig(self):
        return self._getResource(7)

    def setIconBig(self, value):
        self._setResource(7, value)

    def getNationName(self):
        return self._getString(8)

    def setNationName(self, value):
        self._setString(8, value)

    def getValue(self):
        return self._getNumber(9)

    def setValue(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(BlueprintPrice, self)._initialize()
        self._addResourceProperty('iconBig', R.invalid())
        self._addStringProperty('nationName', '')
        self._addNumberProperty('value', 0)
