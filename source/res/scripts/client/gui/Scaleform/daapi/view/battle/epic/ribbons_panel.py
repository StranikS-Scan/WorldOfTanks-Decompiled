# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/ribbons_panel.py
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel, killRibbonFormatter
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from gui.impl import backport
from gui.impl.gen import R
from supply_shared import Supply

def _epicEventRibbonFormatter(ribbon, arenaDP, updater):
    value = ribbon.getExtraValue()
    leftFieldStr = backport.getIntegralFormat(value) if value else ''
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=leftFieldStr)


def _epicKillRibbonFormatter(ribbon, arenaDP, updater):
    vehicleType = arenaDP.getVehicleInfo(ribbon.getVehicleID()).vehicleType
    ribbonType = _BET.SUPPLY_DESTRUCTION if Supply.isSupply(vehicleType.tags) else None
    killRibbonFormatter(ribbon, arenaDP, updater, ribbonType)
    return


_EPIC_RIBBONS_FMTS = {_BET.VEHICLE_RECOVERY: _epicEventRibbonFormatter,
 _BET.ENEMY_SECTOR_CAPTURED: _epicEventRibbonFormatter,
 _BET.DESTRUCTIBLE_DAMAGED: _epicEventRibbonFormatter,
 _BET.DESTRUCTIBLE_DESTROYED: _epicEventRibbonFormatter,
 _BET.DESTRUCTIBLES_DEFENDED: _epicEventRibbonFormatter,
 _BET.DEFENDER_BONUS: _epicEventRibbonFormatter,
 _BET.DESTRUCTION: _epicKillRibbonFormatter}

class EpicRibbonsPanel(BattleRibbonsPanel):

    def _getRibbonFormatter(self, ribbonType):
        return _EPIC_RIBBONS_FMTS.get(ribbonType) or super(EpicRibbonsPanel, self)._getRibbonFormatter(ribbonType)

    def _getViewData(self):
        return super(EpicRibbonsPanel, self)._getViewData() + [[_BET.VEHICLE_RECOVERY, backport.text(R.strings.ingame_gui.efficiencyRibbons.vehicleRecovery())],
         [_BET.ENEMY_SECTOR_CAPTURED, backport.text(R.strings.ingame_gui.efficiencyRibbons.enemySectorCaptured())],
         [_BET.DESTRUCTIBLE_DAMAGED, backport.text(R.strings.ingame_gui.efficiencyRibbons.destructibleDamaged())],
         [_BET.DEFENDER_BONUS, backport.text(R.strings.ingame_gui.efficiencyRibbons.defenderBonus())],
         [_BET.DESTRUCTIBLE_DESTROYED, backport.text(R.strings.ingame_gui.efficiencyRibbons.destructibleDestroyed())],
         [_BET.DESTRUCTIBLES_DEFENDED, backport.text(R.strings.ingame_gui.efficiencyRibbons.destructiblesDefended())],
         [_BET.SUPPLY_DESTRUCTION, backport.text(R.strings.ingame_gui.efficiencyRibbons.kill())]]
