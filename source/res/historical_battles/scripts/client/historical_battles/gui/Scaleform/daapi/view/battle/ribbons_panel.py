# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/ribbons_panel.py
import logging
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel, _singleVehRibbonFormatter
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from historical_battles.gui.Scaleform.daapi.view.battle import ribbons_aggregator
_logger = logging.getLogger(__name__)

def _healVehicleFormatter(ribbon, updater, arenaDP, vehicleDataGetter):
    leftFieldStr = backport.getIntegralFormat(ribbon.actionValue)
    vehName, vehicleClassTag = vehicleDataGetter(ribbon.victimID)
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=leftFieldStr, vehName=vehName, vehType=vehicleClassTag)


def _totalVehiclesHealFormatter(ribbon, updater, arenaDP, vehicleDataGetter):
    leftFieldStr = backport.getIntegralFormat(ribbon.actionValue)
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=leftFieldStr)


_RIBBONS_FMTS = {_BET.BOMBERS: _singleVehRibbonFormatter,
 _BET.ARTILLERY: _singleVehRibbonFormatter,
 _BET.RECEIVED_BOMBERS_DAMAGE: _singleVehRibbonFormatter,
 _BET.HB_DEATH_ZONE: _singleVehRibbonFormatter,
 _BET.HB_PERSONAL_DEATH_ZONE: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_HB_MINEFIELD: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_BOMBERCAS: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_ARTILLERY_ROCKET: _singleVehRibbonFormatter,
 _BET.DAMAGE_BY_ARTILLERY_MORTAR: _singleVehRibbonFormatter,
 _BET.HEAL_VEHICLE_APPLIED: _healVehicleFormatter,
 _BET.TOTAL_VEHICLES_HEAL_APPLIED: _totalVehiclesHealFormatter,
 _BET.HEAL_SELF_VEHICLE_APPLIED: _totalVehiclesHealFormatter}

class HistoricalBattlesRibbonsPanel(BattleRibbonsPanel):

    def _populate(self):
        super(HistoricalBattlesRibbonsPanel, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
        return

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        super(HistoricalBattlesRibbonsPanel, self)._dispose()
        return

    def _createRibbonAggregator(self):
        self._ribbonsAggregator = ribbons_aggregator.createHBRibbonsAggregator()

    def _getVehicleData(self, vehArenaID):
        if not vehArenaID:
            return ('', '')
        else:
            arena = getattr(BigWorld.player(), 'arena', None)
            vehicleRole = arena.arenaInfo.vehicleRoleArenaComponent.getRoleName(vehArenaID) if arena else None
            vehicleType = vehicleRole or ''
            vTypeInfoVO = self._arenaDP.getVehicleInfo(vehArenaID).vehicleType
            vehicleName = vTypeInfoVO.shortNameWithPrefix
            return (vehicleName, vehicleType)

    def _invalidateRibbon(self, ribbon, method):
        if self._shouldShowRibbon(ribbon):
            ribbonsFmts = self._getRibbonsFormatters()
            if ribbon.getType() in ribbonsFmts:
                updater = ribbonsFmts[ribbon.getType()]
                updater(ribbon, method, self._arenaDP, self._getVehicleData)
            else:
                _logger.error('Could not find formatter for ribbon %s', ribbon)

    def _clearPanel(self):
        self.as_resetS()
        self._getRibbonsAggregator().clearRibbonsData()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._clearPanel()

    @classmethod
    def _getRibbonsFormatters(cls):
        ribbonsFmts = BattleRibbonsPanel._getRibbonsFormatters()
        ribbonsFmts.update(_RIBBONS_FMTS)
        return ribbonsFmts

    @classmethod
    def _getAdditionalRibbons(cls):
        return [[_BET.BOMBERS, backport.text(R.strings.hb_battle.efficiencyRibbons.bombers())],
         [_BET.ARTILLERY, backport.text(R.strings.hb_battle.efficiencyRibbons.artillery())],
         [_BET.RECEIVED_BOMBERS_DAMAGE, backport.text(R.strings.hb_battle.efficiencyRibbons.receivedBombersDamage())],
         [_BET.DAMAGE_BY_BOMBERCAS, backport.text(R.strings.hb_battle.efficiencyRibbons.bombercas())],
         [_BET.DAMAGE_BY_ARTILLERY_ROCKET, backport.text(R.strings.hb_battle.efficiencyRibbons.artilleryRocket())],
         [_BET.DAMAGE_BY_ARTILLERY_MORTAR, backport.text(R.strings.hb_battle.efficiencyRibbons.artilleryMortar())],
         [_BET.HB_DEATH_ZONE, backport.text(R.strings.hb_battle.efficiencyRibbons.HBDeathZone())],
         [_BET.HB_PERSONAL_DEATH_ZONE, backport.text(R.strings.hb_battle.efficiencyRibbons.receivedBombersDamage())],
         [_BET.DAMAGE_BY_HB_MINEFIELD, backport.text(R.strings.hb_battle.efficiencyRibbons.damageByHBMinefield())],
         [_BET.HEAL_VEHICLE_APPLIED, backport.text(R.strings.hb_battle.efficiencyRibbons.healVehicleApplied())],
         [_BET.TOTAL_VEHICLES_HEAL_APPLIED, backport.text(R.strings.hb_battle.efficiencyRibbons.TotalVehiclesHealApplied())],
         [_BET.HEAL_SELF_VEHICLE_APPLIED, backport.text(R.strings.hb_battle.efficiencyRibbons.healSelfVehicleApplied())]]
