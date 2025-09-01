# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/helpers/tips.py
from comp7_light_constants import ARENA_GUI_TYPE
from helpers.tips import TipsCriteria, readTips
_COMP7_LIGHT_TIPS_PATTERN = '^(comp7(Core|Light)\\d+$)'
_comp7LightTips = readTips(_COMP7_LIGHT_TIPS_PATTERN)

class Comp7LightTipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _comp7LightTips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.COMP7_LIGHT
