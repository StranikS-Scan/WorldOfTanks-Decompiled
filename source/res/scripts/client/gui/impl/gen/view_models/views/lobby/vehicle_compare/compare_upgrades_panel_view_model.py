# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/compare_upgrades_panel_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.upgrades_model import UpgradesModel

class CompareUpgradesPanelViewModel(ViewModel):
    __slots__ = ('onSelectUpgrades',)

    def __init__(self, properties=1, commands=1):
        super(CompareUpgradesPanelViewModel, self).__init__(properties=properties, commands=commands)

    def getUpgrades(self):
        return self._getArray(0)

    def setUpgrades(self, value):
        self._setArray(0, value)

    @staticmethod
    def getUpgradesType():
        return UpgradesModel

    def _initialize(self):
        super(CompareUpgradesPanelViewModel, self)._initialize()
        self._addArrayProperty('upgrades', Array())
        self.onSelectUpgrades = self._addCommand('onSelectUpgrades')
