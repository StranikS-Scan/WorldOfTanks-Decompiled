# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/game_event/wt_battle_shell_tooltip.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.shared.tooltips import ToolTipBaseData
from gui.wt_event.wt_event_helpers import isPlayerBoss
from helpers import dependency
from items import vehicles
from skeletons.gui.battle_session import IBattleSessionProvider

class WtBattleShellTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(WtBattleShellTooltipData, self).__init__(context, TOOLTIPS_CONSTANTS.WT_EVENT_SHELL_BATTLE)

    @staticmethod
    def _getShellParams(ammoCtrl, damageMultiplier):
        shellCD = ammoCtrl.getNextShellCD()
        gunSettings = ammoCtrl.getGunSettings()
        descriptor = vehicles.getItemByCompactDescr(shellCD)
        piercingPower = int(gunSettings.getPiercingPower(shellCD))
        damage = 0
        if descriptor and descriptor.damage:
            damage = int(descriptor.damage[0] * damageMultiplier)
        return (damage, piercingPower)

    @staticmethod
    def _getDamageMultiplier(arenaInfoCtrl):
        return 1 if not arenaInfoCtrl else arenaInfoCtrl.powerPoints + 1

    def getDisplayableData(self, *args, **kwargs):
        sessionProvider = dependency.instance(IBattleSessionProvider)
        ammoCtrl = sessionProvider.shared.ammo
        if ammoCtrl is None:
            return
        else:
            isBossVehicle = isPlayerBoss()
            vehicleType = 'boss' if isBossVehicle else 'hunter'
            damageMultiplier = self._getDamageMultiplier(sessionProvider.dynamic.arenaInfo) if not isBossVehicle else 1
            damage, piercingPower = self._getShellParams(ammoCtrl, damageMultiplier)
            return {'header': backport.text(R.strings.wt_event.shell.dyn(vehicleType).header()),
             'body': backport.text(R.strings.wt_event.shell.dyn(vehicleType).body(), damage=damage, piercingPower=piercingPower)}
