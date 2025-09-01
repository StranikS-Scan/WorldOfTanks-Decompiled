# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/helpers/tips.py
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from helpers.tips import TipsCriteria, readTips
_COMP7_TIPS_PATTERN = '^(comp7(Core|Ranked)\\d+$)'
_comp7Tips = readTips(_COMP7_TIPS_PATTERN)

class Comp7TipsCriteria(TipsCriteria):

    def _getTargetList(self):
        return _comp7Tips

    def _getArenaGuiType(self):
        return ARENA_GUI_TYPE.COMP7
