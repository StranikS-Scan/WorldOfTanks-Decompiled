# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tank_setup/configuration.py
from frontline.gui.impl.lobby.tank_setup.array_provider import BattleAbilityProvider
from gui.impl.common.tabs_controller import tabUpdateFunc
from gui.impl.lobby.tank_setup.configurations.base import BaseTankSetupTabsController, BaseDealPanel

class EpicBattleTabs(object):
    BATTLE_ABILITY = 'battleAbility'
    ALL = (BATTLE_ABILITY,)


class EpicBattleTabsController(BaseTankSetupTabsController):
    __slots__ = ()

    def getDefaultTab(self):
        return EpicBattleTabs.BATTLE_ABILITY

    @tabUpdateFunc(EpicBattleTabs.BATTLE_ABILITY)
    def _updateOptDevice(self, viewModel, isFirst=False):
        pass

    def tabOrderKey(self, tabName):
        return EpicBattleTabs.ALL.index(tabName)

    def _getAllProviders(self):
        return {EpicBattleTabs.BATTLE_ABILITY: BattleAbilityProvider}


class EpicBattleDealPanel(BaseDealPanel):

    @classmethod
    def updateDealPanelPrice(cls, vehicle, items, dealPanelModel):
        pass
