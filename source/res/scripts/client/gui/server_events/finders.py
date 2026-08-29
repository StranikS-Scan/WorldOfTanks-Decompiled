# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/finders.py
import re
from helpers import dependency
from personal_missions import PM_BRANCH
from shared_utils import findFirst, first
from skeletons.gui.server_events import IEventsCache
PT_TOKEN_PREFIX = 'token:pt:'
PERSONAL_MISSION_TOKEN = PT_TOKEN_PREFIX + 'final:s%s:t%s'
MAIN_PERSONAL_MISSION_TOKEN = PERSONAL_MISSION_TOKEN + ':main'
ADD_PERSONAL_MISSION_TOKEN = PERSONAL_MISSION_TOKEN + ':add'
PERSONAL_MISSION_COMPLETE_TOKEN = PERSONAL_MISSION_TOKEN + ':complete'
PERSONAL_MISSION_BADGES_TOKEN = PT_TOKEN_PREFIX + 's%s:badges'
FINAL_PT_TOKEN_PREFIX = 'pt_final_'
FINAL_PERSONAL_MISSION_TOKEN = FINAL_PT_TOKEN_PREFIX + 's%s_t%s'
NO_AWARD_LIST_FINISHED_QUEST = 'pm%s_campaign_finished_honor'
NO_AWARD_LIST_OPERATION_FINISHED_HONOR_QUEST = 'pt_final_s%s_t%s_honor'
NO_AWARD_LIST_OPERATION_REWARD_QUEST = 'pm%s_operation_%s_reward'
NO_AWARD_LIST_PM_BASE_TOKEN = PT_TOKEN_PREFIX + 's%s:t%s:finished:base'
NO_AWARD_LIST_HONOR_POSTFIX = 'honor'
NO_AWARD_LIST_PM_REWARD_CLAIMED = PT_TOKEN_PREFIX + 's%s:t%s:reward:claimed'
NO_AWARD_LIST_FINISHED_CAMPAIGN_TOKEN = PT_TOKEN_PREFIX + 's%s:finished:' + NO_AWARD_LIST_HONOR_POSTFIX
NO_AWARD_LIST_VEHICLE_DETAIL_TOKEN = PT_TOKEN_PREFIX + 's%s:t%s:vehElement'
NO_AWARD_LIST_QUEST_PREFIX_TEMPLATE = 'pm%s_'
NO_AWARD_LIST_MILESTONE_QUEST_PREFIX = NO_AWARD_LIST_QUEST_PREFIX_TEMPLATE + 'operation'
NO_AWARD_LIST_MILESTONE_QUEST_POSTFIX = 'milestone'
PM_POINTS_PREFIX = PM_NO_AWARD_LIST_QUESTS_PREFIX = 'pm'
PM_POINTS_POSTFIX = ':points'
PM_POINTS_TOKEN = PM_POINTS_PREFIX + PM_POINTS_POSTFIX
PM_OPERATION_POINTS_TOKEN = PM_POINTS_PREFIX + '%s:%s' + PM_POINTS_POSTFIX
isPMQuestRegExp = re.compile('pt_(s\\d_t\\d+_c\\d|final(_s\\d_t\\d+)?)(_[A-Za-z_]+)?')
CHAMPION_BADGES_BY_BRANCH = {PM_BRANCH.REGULAR: FINAL_PT_TOKEN_PREFIX + 'badge',
 PM_BRANCH.PERSONAL_MISSION_2: FINAL_PT_TOKEN_PREFIX + 'badge_s2'}
OPERATIONS_TOKENS_PATTERNS = (PERSONAL_MISSION_TOKEN, MAIN_PERSONAL_MISSION_TOKEN, ADD_PERSONAL_MISSION_TOKEN)
CHAMPION_BADGE_AT_OPERATION_ID = {operationIds[-1]:CHAMPION_BADGES_BY_BRANCH[branch] for branch, operationIds in PM_BRANCH.BRANCH_TO_OPERATION_IDS.items() if CHAMPION_BADGES_BY_BRANCH.get(branch)}
NO_AWARD_LIST_QUEST_PREFIXES = [ NO_AWARD_LIST_QUEST_PREFIX_TEMPLATE % PM_BRANCH.PM_CAMPAIGNS_IDS[PM_BRANCH.NAME_TO_TYPE[branchName]] for branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES ]

def getBranchByOperationId(operationID):
    return PM_BRANCH.OPERATION_ID_TO_BRANCH[operationID]


def isPMNoAwardListMilestone(questID):
    return questID and questID.startswith(PM_NO_AWARD_LIST_QUESTS_PREFIX) and NO_AWARD_LIST_MILESTONE_QUEST_POSTFIX in questID


def getPMNoAwardListMilestones(quests, branch, operationID):
    milestonesName = (NO_AWARD_LIST_MILESTONE_QUEST_PREFIX % PM_BRANCH.PM_CAMPAIGNS_IDS[branch] + '_{}_' + NO_AWARD_LIST_MILESTONE_QUEST_POSTFIX).format(operationID)
    result = {questID:quest for questID, quest in quests.items() if questID.startswith(milestonesName)}
    return result


def isPMPoints(tokenName):
    return tokenName.startswith(PM_POINTS_PREFIX) and tokenName.endswith(PM_POINTS_POSTFIX)


def getFinalTokenQuestIdByOperationId(operationId):
    return FINAL_PERSONAL_MISSION_TOKEN % (PM_BRANCH.PM_CAMPAIGNS_IDS[getBranchByOperationId(operationId)], operationId)


def getAdditionalTokenQuestIdByOperationId(operationId, addCamouflage=False, addBadge=False):
    result = []
    finalId = getFinalTokenQuestIdByOperationId(operationId)
    if addCamouflage:
        result.append(''.join((finalId, '_camouflage')))
    if addBadge:
        branch = getBranchByOperationId(operationId)
        if branch == PM_BRANCH.REGULAR:
            result.append(''.join((finalId, '_badge2')))
        elif branch == PM_BRANCH.PERSONAL_MISSION_2:
            result.append(''.join((finalId, '_badge')))
    return result


PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID = {opId:getFinalTokenQuestIdByOperationId(opId) for opId in PM_BRANCH.OPERATION_ID_TO_BRANCH.keys()}

def getPersonalMissionDataFromToken(token):
    eventsCache = dependency.instance(IEventsCache)
    for branch in PM_BRANCH.ALL:
        for opID in eventsCache.getPersonalMissions().getOperationsForBranch(branch).iterkeys():
            if token == MAIN_PERSONAL_MISSION_TOKEN % opID:
                return (True, opID, True)
            if token == ADD_PERSONAL_MISSION_TOKEN % opID:
                return (True, opID, False)

    return (False, None, None)


def getQuestsByTokenAndBonus(quests, tokenFinder=None, bonusFinder=None):
    result = {}
    for questID, quest in quests.iteritems():
        token = findFirst(tokenFinder, quest.accountReqs.getTokens())
        if token is None:
            continue
        bonus = findFirst(bonusFinder, quest.getBonuses())
        if bonus is not None:
            result[questID] = quest

    return result


def getQuestsByToken(quests, tokenFinder):
    return [ quest for quest in quests.values() if filter(tokenFinder, quest.accountReqs.getTokens()) ]


def getQuestByTokenAndBonus(quests, tokenFinder=None, bonusFinder=None):
    return first(getQuestsByTokenAndBonus(quests, tokenFinder, bonusFinder).itervalues())


def tokenFinder(tokenID):

    def finder(token):
        return token.getID() == tokenID

    return finder


def multipleTokenFinder(tokenIDs):

    def finder(token):
        return token.getID() in tokenIDs

    return finder


def pmTokenDetector(operations):
    tokensList = set()
    for opID, op in operations.iteritems():
        tokensList.update({pattern % (op.getCampaignID(), opID) for pattern in OPERATIONS_TOKENS_PATTERNS})
        tokensList.add(PERSONAL_MISSION_BADGES_TOKEN % op.getCampaignID())

    return multipleTokenFinder(tokensList)


def mainQuestTokenFinder(operation):
    return tokenFinder(MAIN_PERSONAL_MISSION_TOKEN % (operation.getCampaignID(), operation.getID()))


def pmPointsTokenFinder(operation):
    return tokenFinder(PM_OPERATION_POINTS_TOKEN % (operation.getCampaignID(), operation.getID()))


def addQuestTokenFinder(operation):
    return tokenFinder(ADD_PERSONAL_MISSION_TOKEN % (operation.getCampaignID(), operation.getID()))


def tokenBonusFinder(tokenID):

    def finder(bonus):
        return bonus.getName() == 'battleToken' and tokenID in bonus.getTokens()

    return finder


def getOperationCompleteToken(operation):
    return (NO_AWARD_LIST_PM_BASE_TOKEN if operation.isWithoutAwardListBranch() else PERSONAL_MISSION_COMPLETE_TOKEN) % (operation.getCampaignID(), operation.getID())


def operationCompletionBonusFinder(operation):
    return tokenBonusFinder(getOperationCompleteToken(operation))


def badgeBonusFinder():

    def finder(bonus):
        return bonus.getName() == 'dossier' and bonus.getBadges()

    return finder
