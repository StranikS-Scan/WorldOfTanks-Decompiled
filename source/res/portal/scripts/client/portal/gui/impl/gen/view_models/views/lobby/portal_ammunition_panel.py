# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_ammunition_panel.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class PortalAmmunitionPanel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PortalAmmunitionPanel, self).__init__(properties=properties, commands=commands)

    def getShellType(self):
        return self._getString(0)

    def setShellType(self, value):
        self._setString(0, value)

    def getAbilities(self):
        return self._getArray(1)

    def setAbilities(self, value):
        self._setArray(1, value)

    @staticmethod
    def getAbilitiesType():
        return unicode

    def getHasNewUpgrade(self):
        return self._getBool(2)

    def setHasNewUpgrade(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(PortalAmmunitionPanel, self)._initialize()
        self._addStringProperty('shellType', '')
        self._addArrayProperty('abilities', Array())
        self._addBoolProperty('hasNewUpgrade', False)
