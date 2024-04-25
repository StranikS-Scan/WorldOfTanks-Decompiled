# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/shared/tooltips/quests.py
from gui.shared.tooltips import quests
from gui.server_events.events_helpers import getPreviousBattleQuest
from gui.shared.tooltips import formatters
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles

class HBUnavailableQuestTooltipData(quests.UnavailableQuestTooltipData):

    def _getRequirementsOverrides(self, quest):
        prevQuest = getPreviousBattleQuest(quest)
        if prevQuest is not None and not prevQuest.isCompleted():
            text = backport.text(R.strings.quests.missionDetails.requirements.conclusion.previousIncomplete(), quest_name=prevQuest.getUserName())
            return [formatters.packTextParameterBlockData(name=text_styles.main(text), value=text_styles.main(TOOLTIPS.QUESTS_UNAVAILABLE_BULLET), valueWidth=16)]
        else:
            return []
