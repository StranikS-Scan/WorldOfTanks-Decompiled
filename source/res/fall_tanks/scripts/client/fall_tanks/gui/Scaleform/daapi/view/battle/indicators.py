# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/indicators.py
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator, DAMAGE_INDICATOR_TYPE

class FallTanksDamageIndicator(_DamageIndicator):
    _DEFAULT_DAMAGE_INDICATOR_TYPE = DAMAGE_INDICATOR_TYPE.STANDARD

    def _getIndicatorType(self):
        return self._DEFAULT_DAMAGE_INDICATOR_TYPE


def createFallTanksDamageIndicator():
    return FallTanksDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)
