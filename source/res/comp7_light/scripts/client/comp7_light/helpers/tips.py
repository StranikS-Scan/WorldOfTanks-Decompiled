# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/helpers/tips.py
import typing
from comp7_light_constants import ARENA_GUI_TYPE
from helpers.tips import readTips
from comp7_core.helpers.tips import Comp7BaseTipsCriteria
_COMP7_LIGHT_TIPS_PATTERN = '^(comp7(Core|Light)\\d+$)'
_comp7LightTips = readTips(_COMP7_LIGHT_TIPS_PATTERN)

class Comp7LightTipsCriteria(Comp7BaseTipsCriteria):

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.COMP7_LIGHT

    @staticmethod
    def _getRegularTips():
        return _comp7LightTips
