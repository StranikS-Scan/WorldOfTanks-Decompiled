# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/badges_builders.py
from gui.Scaleform.daapi.view.lobby.badges_tooltips import BadgesSuffixItem, BadgesSuffixRankedItem
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.BADGES_SUFFIX_ITEM, TOOLTIPS_CONSTANTS.BADGES_SUFFIX_ITEM_UI, BadgesSuffixItem(contexts.ToolTipContext(None))), DataBuilder(TOOLTIPS_CONSTANTS.BADGES_SUFFIX_RANKED_ITEM, TOOLTIPS_CONSTANTS.BADGES_SUFFIX_RANKED_ITEM_UI, BadgesSuffixRankedItem(contexts.ToolTipContext(None))))
