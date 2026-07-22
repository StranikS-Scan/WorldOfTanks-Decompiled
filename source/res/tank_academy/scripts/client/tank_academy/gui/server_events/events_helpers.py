# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/server_events/events_helpers.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import QuestPostBattleInfo
from gui.server_events import conditions, formatters
from tank_academy_common.tank_academy_constants import AB_TEST_DEFAULT_GROUP_NAME
from tank_academy.gui.server_events.events_constants import TANK_ACADEMY_QUEST_PREFIX, TANK_ACADEMY_QUEST_GROUP_PREFIX
_DELAYED_REWARD_OFFER_TOKEN_PREFIX = 'offer:tank_academy'

def isTankAcademyOfferVehicleToken(token):
    return token.startswith(_DELAYED_REWARD_OFFER_TOKEN_PREFIX)


def isTankAcademyOfferToken(token):
    return isTankAcademyOfferVehicleToken(token) and not token.endswith('_gift')


def isTankAcademyDelayedRewardToken(token):
    return isTankAcademyOfferToken(token)


def isTankAcademyDelayedRewardCurrencyToken(token):
    return isTankAcademyOfferVehicleToken(token) and token.endswith('_gift')


def isTankAcademyQuestID(questID):
    return questID.startswith(TANK_ACADEMY_QUEST_PREFIX)


def parseTankAcademyQuestID(questID):
    return _parseTankAcademyID(questID, TANK_ACADEMY_QUEST_PREFIX)


def isTankAcademyGroupID(groupID):
    return groupID.startswith(TANK_ACADEMY_QUEST_GROUP_PREFIX)


def parseTankAcademyGroupID(groupID):
    return _parseTankAcademyID(groupID, TANK_ACADEMY_QUEST_GROUP_PREFIX)


def _parseTankAcademyID(taID, taIDPrefix):
    order = -1
    abTestGroup = AB_TEST_DEFAULT_GROUP_NAME
    body = taID[len(taIDPrefix) + 1:]
    try:
        parts = body.rsplit('_', 1)
        if parts:
            order = int(parts[-1])
            if len(parts) == 2:
                abTestGroup = parts[-2]
    except ValueError:
        pass

    return (order, abTestGroup)


class TankAcademyQuestPostBattleInfo(QuestPostBattleInfo):

    def getInfo(self, svrEvents, pCur=None, pPrev=None, noProgressInfo=False):
        battleResults = R.strings.tank_academy.battleResults
        result = super(TankAcademyQuestPostBattleInfo, self).getInfo(svrEvents, pCur, pPrev, noProgressInfo)
        result['description'] = backport.text(battleResults.descr()).format(questIdx=self.event.getOrder())
        result['linkTooltip'] = backport.text(battleResults.linkBtn.tooltip())
        return result

    def _getProgresses(self, pCur, pPrev):
        index = 0
        progresses = []
        for cond in self.event.bonusCond.getConditions().items:
            if isinstance(cond, conditions.Cumulativable):
                for _, (curProg, totalProg, diff, _) in cond.getProgressPerGroup(pCur, pPrev).iteritems():
                    if not diff:
                        continue
                    index += 1
                    progresses.append({'progrTooltip': None,
                     'progrBarType': formatters.PROGRESS_BAR_TYPE.SIMPLE,
                     'maxProgrVal': totalProg,
                     'currentProgrVal': curProg,
                     'description': '%d. %s' % (index, self.event.getConditionLbl()),
                     'progressDiff': '+ %s' % backport.getIntegralFormat(diff),
                     'progressDiffTooltip': backport.text(R.strings.tank_academy.battleResults.progress.tooltip())})

        return progresses
