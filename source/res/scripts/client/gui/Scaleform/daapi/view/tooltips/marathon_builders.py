# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/marathon_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts, marathon
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.MARATHON_QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, marathon.MarathonEventTooltipData(contexts.QuestContext())), DataBuilder(TOOLTIPS_CONSTANTS.QUEST_BONUS_INFO, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, marathon.MarathonBonusInfoTooltipData(contexts.QuestContext())))
