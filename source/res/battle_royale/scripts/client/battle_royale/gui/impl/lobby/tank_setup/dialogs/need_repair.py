# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tank_setup/dialogs/need_repair.py
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import NeedRepairMainContent

class NeedRepairBattleRoyale(NeedRepairMainContent):

    def onLoading(self, *args, **kwargs):
        super(NeedRepairBattleRoyale, self).onLoading(*args, **kwargs)
        with self._viewModel.transaction() as model:
            model.setRepairPercentage(self._repairPercentage)
            model.setFreeAutoRepair(False)
