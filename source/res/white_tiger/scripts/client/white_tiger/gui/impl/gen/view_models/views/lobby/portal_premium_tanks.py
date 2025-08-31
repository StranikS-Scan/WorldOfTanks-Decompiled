# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_premium_tanks.py
from frameworks.wulf import ViewModel

class PortalPremiumTanks(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(PortalPremiumTanks, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(PortalPremiumTanks, self)._initialize()
        self._addStringProperty('name', '')
