# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/indicators.py
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN
from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator

class DamageIndicator(_DamageIndicator):
    pass


def createPortalBattlesDamageIndicator():
    return DamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)
