# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/shell_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.tooltips.portal_shell_stat import PortalShellStat

class ShellTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ShellTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getCaliber(self):
        return self._getNumber(2)

    def setCaliber(self, value):
        self._setNumber(2, value)

    def getStats(self):
        return self._getArray(3)

    def setStats(self, value):
        self._setArray(3, value)

    @staticmethod
    def getStatsType():
        return PortalShellStat

    def _initialize(self):
        super(ShellTooltipModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addNumberProperty('caliber', 0)
        self._addArrayProperty('stats', Array())
