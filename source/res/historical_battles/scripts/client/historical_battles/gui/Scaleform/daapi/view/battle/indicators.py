# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/indicators.py
from constants import BigWorld
from gui.Scaleform.daapi.view.battle.shared.indicators import _ExtendedMarkerVOBuilder, _ExtendedCriticalMarkerVOBuilder, _ExtendedMarkerVOBuilderFactory, _DamageIndicator
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from historical_battles_common.hb_constants import VehicleRole

class HBMarkersMixin(object):

    def _getTankType(self, markerData):
        tankTypeStr = super(HBMarkersMixin, self)._getTankType(markerData)
        if not markerData.hitData.isFriendlyFire():
            attackerID = markerData.hitData.getAttackerID()
            arena = getattr(BigWorld.player(), 'arena', None)
            if arena is not None:
                role = arena.arenaInfo.vehicleRoleArenaComponent.getRole(attackerID)
                if role == VehicleRole.elite:
                    tankTypeStr += role.capitalize()
                elif role.hasUniqueIcon():
                    tankTypeStr = role.name
        return tankTypeStr


class HBExtendedMarkerVOBuilder(HBMarkersMixin, _ExtendedMarkerVOBuilder):
    pass


class HBExtendedCriticalMarkerVOBuilder(HBMarkersMixin, _ExtendedCriticalMarkerVOBuilder):
    pass


class HBExtendedMarkerVOBuilderFactory(_ExtendedMarkerVOBuilderFactory):
    _extendedMarkerClass = HBExtendedMarkerVOBuilder
    _extendedCriticalMarkerClass = HBExtendedCriticalMarkerVOBuilder


class HBDamageIndicator(_DamageIndicator):
    _extendedMarkerFactoryClass = HBExtendedMarkerVOBuilderFactory


def createHistoricalBattlesDamageIndicator():
    return HBDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)
