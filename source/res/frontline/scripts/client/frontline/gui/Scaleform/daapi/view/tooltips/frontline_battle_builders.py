# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/tooltips/frontline_battle_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips.builders import DataBuilder
from frontline.gui.shared.tooltips.FLRandomReserve import FLRandomReserve
from frontline.gui.Scaleform.daapi.view.battle.tooltips.epic_battle_tooltips import EpicRankUnlockTooltipData, _FLRandomReserveContext
from gui.shared.tooltips import contexts
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.FRONTLINE_RANDOM_RESERVE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, FLRandomReserve(_FLRandomReserveContext())), DataBuilder(TOOLTIPS_CONSTANTS.EPIC_RANK_UNLOCK_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, EpicRankUnlockTooltipData(contexts.ToolTipContext(None))))
