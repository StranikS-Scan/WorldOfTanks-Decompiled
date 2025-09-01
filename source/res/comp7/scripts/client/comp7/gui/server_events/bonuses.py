# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/server_events/bonuses.py
import logging
from comp7_common_const import COMP7_WEEKLY_QUESTS_COMPLETE_TOKEN_REGEXP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.bonuses import TokensBonus
from gui.shared.utils.functions import makeTooltip
COMP7_TOKEN_WEEKLY_REWARD_NAME = 'comp7TokenWeeklyReward'
_logger = logging.getLogger(__name__)

class Comp7TokenWeeklyRewardBonus(TokensBonus):

    def __init__(self, name, value, isCompensation=False, ctx=None):
        super(Comp7TokenWeeklyRewardBonus, self).__init__(name, value, isCompensation, ctx)
        self._name = COMP7_TOKEN_WEEKLY_REWARD_NAME

    def isShowInGUI(self):
        return False

    def getTooltip(self):
        header = TOOLTIPS.getAwardHeader(self.getName())
        body = TOOLTIPS.getAwardBody(self.getName())
        return makeTooltip(header or None, body or None)


def isComp7WeeklyQuestToken(tID):
    return COMP7_WEEKLY_QUESTS_COMPLETE_TOKEN_REGEXP.match(tID)
