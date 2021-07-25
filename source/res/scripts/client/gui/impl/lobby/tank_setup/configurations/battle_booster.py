# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/configurations/battle_booster.py
from gui.impl.lobby.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.array_providers.battle_booster import OptDeviceBattleBoosterProvider, CrewBattleBoosterProvider
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController

class BattleBoosterTabs(object):
    OPT_DEVICE = 'optDevice'
    CREW = 'crew'
    ALL = (OPT_DEVICE, CREW)


class BattleBoostersTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return BattleBoosterTabs.OPT_DEVICE

    @tabUpdateFunc(BattleBoosterTabs.OPT_DEVICE)
    def _updateOptDevice(self, viewModel, isFirst=False):
        pass

    @tabUpdateFunc(BattleBoosterTabs.CREW)
    def _updateCrew(self, viewModel, isFirst=False):
        pass

    def tabOrderKey(self, tabName):
        return BattleBoosterTabs.ALL.index(tabName)

    def _getAllProviders(self):
        return {BattleBoosterTabs.OPT_DEVICE: OptDeviceBattleBoosterProvider,
         BattleBoosterTabs.CREW: CrewBattleBoosterProvider}
