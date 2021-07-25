# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/ammunition_shells_section.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_items_section import AmmunitionItemsSection

class AmmunitionShellsSection(AmmunitionItemsSection):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(AmmunitionShellsSection, self).__init__(properties=properties, commands=commands)

    def getInstalledCount(self):
        return self._getNumber(6)

    def setInstalledCount(self, value):
        self._setNumber(6, value)

    def getMaxCount(self):
        return self._getNumber(7)

    def setMaxCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(AmmunitionShellsSection, self)._initialize()
        self._addNumberProperty('installedCount', 0)
        self._addNumberProperty('maxCount', 0)
