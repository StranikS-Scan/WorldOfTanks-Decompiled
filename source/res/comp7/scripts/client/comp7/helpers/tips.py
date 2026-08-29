# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/helpers/tips.py
import typing
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from helpers.tips import readTips
from comp7_core.helpers.tips import Comp7BaseTipsCriteria
_COMP7_TIPS_PATTERN = '^(comp7(Core|Ranked)\\d+$)'
_comp7Tips = readTips(_COMP7_TIPS_PATTERN)

class Comp7TipsCriteria(Comp7BaseTipsCriteria):

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.COMP7

    @staticmethod
    def _getRegularTips():
        return _comp7Tips
