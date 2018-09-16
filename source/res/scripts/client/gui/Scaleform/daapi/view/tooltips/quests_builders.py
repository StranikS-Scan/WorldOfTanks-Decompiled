# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/tooltips/quests_builders.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.tooltips import contexts
from gui.shared.tooltips import quests
from gui.shared.tooltips.builders import DataBuilder
__all__ = ('getTooltipBuilders',)

def getTooltipBuilders():
    return (DataBuilder(TOOLTIPS_CONSTANTS.QUESTS_PREVIEW, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, quests.QuestsPreviewTooltipData(contexts.QuestsBoosterContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.SHEDULE_QUEST, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, quests.ScheduleQuestTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.MISSION_VEHICLE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, quests.MissionVehiclesConditionTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.MISSION_VEHICLE_TYPE, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, quests.MissionVehiclesTypeTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.ADDITIONAL_AWARDS, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, quests.AdditionalAwardTooltipData(contexts.QuestContext())),
     DataBuilder(TOOLTIPS_CONSTANTS.UNAVAILABLE_QUEST, TOOLTIPS_CONSTANTS.BLOCKS_DEFAULT_UI, quests.UnavailableQuestTooltipData(contexts.QuestContext())))
