# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/cond_formatters/hb_requirements.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.server_events.events_helpers import getPreviousBattleQuest
from gui.server_events.cond_formatters.requirements import AccountRequirementsFormatter, TQRecursiveGroupFormatter, SingleGroupFormatter

class HBRecursiveGroupFormatter(TQRecursiveGroupFormatter):

    def conclusion(self, group, event, requirements, passed, total):
        prevQuest = getPreviousBattleQuest(event)
        if prevQuest is not None and not prevQuest.isCompleted():
            rRequirements = R.strings.quests.missionDetails.requirements
            icon = (icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.marker_blocked()), width=14, height=14, vSpace=-1, hSpace=-2),)
            reason = backport.text(rRequirements.conclusion.previousIncomplete(), quest_name=prevQuest.getUserName())
            return text_styles.concatStylesWithSpace(icon, text_styles.error(backport.text(rRequirements.header.unavailable())), text_styles.main(reason))
        else:
            return


class HBRequirementsFormatter(AccountRequirementsFormatter):

    def __init__(self):
        super(HBRequirementsFormatter, self).__init__({'and': HBRecursiveGroupFormatter(),
         'or': HBRecursiveGroupFormatter(),
         'single': SingleGroupFormatter()})

    def _showDetailedRequirementsButton(self):
        return False
