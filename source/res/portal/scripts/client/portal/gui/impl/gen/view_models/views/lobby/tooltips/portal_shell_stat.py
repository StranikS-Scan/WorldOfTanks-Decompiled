# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/portal_shell_stat.py
from frameworks.wulf import ViewModel

class PortalShellStat(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PortalShellStat, self).__init__(properties=properties, commands=commands)

    def getFrom(self):
        return self._getNumber(0)

    def setFrom(self, value):
        self._setNumber(0, value)

    def getTo(self):
        return self._getNumber(1)

    def setTo(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(PortalShellStat, self)._initialize()
        self._addNumberProperty('from', 0)
        self._addNumberProperty('to', 0)
        self._addStringProperty('name', '')
