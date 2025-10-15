# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/ribbons_panel.py
import logging
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel, _singleVehRibbonFormatter
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES as _BET
from portal.gui.Scaleform.daapi.view.battle import ribbons_aggregator
_logger = logging.getLogger(__name__)
_RIBBONS_FMTS = {_BET.DEALT_DMG_BY_CORRODING_SHOT: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_FIRE_CIRCLE: _singleVehRibbonFormatter,
 _BET.RECEIVED_BY_THUNDER_STRIKE: _singleVehRibbonFormatter}

class PortalRibbonsPanel(BattleRibbonsPanel):

    def _populate(self):
        super(PortalRibbonsPanel, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
        return

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
        super(PortalRibbonsPanel, self)._dispose()
        return

    def _createRibbonAggregator(self):
        return ribbons_aggregator.createPortalRibbonsAggregator()

    def _getVehicleData(self, vehArenaID):
        if not vehArenaID:
            return ('', '')
        else:
            arena = getattr(BigWorld.player(), 'arena', None)
            vehicleRole = arena.arenaInfo.vehicleRoleArenaComponent.getRoleName(vehArenaID) if arena else None
            vehicleType = vehicleRole or ''
            vTypeInfoVO = self._getArenaDP.getVehicleInfo(vehArenaID).vehicleType
            vehicleName = vTypeInfoVO.shortNameWithPrefix
            return (vehicleName, vehicleType)

    def _invalidateRibbon(self, ribbon, method):
        if self._shouldShowRibbon(ribbon):
            ribbonsFmts = self._getRibbonsFormatters()
            if ribbon.getType() in ribbonsFmts:
                updater = ribbonsFmts[ribbon.getType()]
                updater(ribbon, method, self._getArenaDP, self._getVehicleData)
            else:
                _logger.error('Could not find formatter for ribbon %s', ribbon)

    def _clearPanel(self):
        self.as_resetS()
        self._getRibbonAggregator().clearRibbonsData()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._clearPanel()

    @classmethod
    def _getRibbonsFormatters(cls):
        ribbonsFmts = BattleRibbonsPanel._getRibbonsFormatters()
        ribbonsFmts.update(_RIBBONS_FMTS)
        return ribbonsFmts

    @classmethod
    def _getAdditionalRibbons(cls):
        return [[_BET.DEALT_DMG_BY_CORRODING_SHOT, backport.text(R.strings.portal_battle.efficiencyRibbons.guidedMissile())],
         [_BET.RECEIVED_BY_FIRE_CIRCLE, backport.text(R.strings.portal_battle.efficiencyRibbons.superBossAura())],
         [_BET.RECEIVED_BY_THUNDER_STRIKE, backport.text(R.strings.portal_battle.efficiencyRibbons.sentinelAttack())],
         [_BET.DEATH_ZONE, backport.text(R.strings.portal_battle.efficiencyRibbons.portalDeathZone())]]
