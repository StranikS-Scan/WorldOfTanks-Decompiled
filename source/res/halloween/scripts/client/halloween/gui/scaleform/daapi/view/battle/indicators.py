# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/indicators.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator
from gui.Scaleform.daapi.view.battle.shared.indicators import _DamageIndicator
from gui.battle_control.battle_constants import HIT_INDICATOR_MAX_ON_SCREEN

class HWDamageIndicator(_DamageIndicator):
    _DAMAGE_INDICATOR_SWF = 'halloween|halloweenBattleDamageIndicatorApp.swf'


def hwCreateDamageIndicator():
    return HWDamageIndicator(HIT_INDICATOR_MAX_ON_SCREEN)


class HalloweenSixthSenseIndicator(SixthSenseIndicator):
    pass
