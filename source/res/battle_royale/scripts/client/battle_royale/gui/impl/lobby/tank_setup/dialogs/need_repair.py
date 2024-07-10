# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tank_setup/dialogs/need_repair.py
from BattleRoyaleConstants import BATTLE_ROYALE_REPAIR_COST
from constants import Configs
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import NeedRepairMainContent
from gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepair
from helpers import dependency, server_settings
from skeletons.gui.lobby_context import ILobbyContext

class NeedRepairMainContentBattleRoyale(NeedRepairMainContent):

    def onLoading(self, *args, **kwargs):
        super(NeedRepairMainContentBattleRoyale, self).onLoading(*args, **kwargs)
        repairCost = self.vehicle.repairCost
        maxRepairCost = BATTLE_ROYALE_REPAIR_COST
        with self._viewModel.transaction() as model:
            model.setRepairPercentage(round((maxRepairCost - repairCost) * 100 / maxRepairCost))
            model.setFreeAutoRepair(False)


class NeedRepairBattleRoyale(NeedRepair):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def _initialize(self, *args, **kwargs):
        super(NeedRepairBattleRoyale, self)._initialize(*args, **kwargs)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def _finalize(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(NeedRepairBattleRoyale, self)._finalize()

    @server_settings.serverSettingsChangeListener(Configs.BATTLE_ROYALE_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        if not diff[Configs.BATTLE_ROYALE_CONFIG.value].get('isEnabled', True):
            self._onCancel()
