# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/finders.py
from helpers import dependency
from personal_missions import PM_BRANCH
from shared_utils import findFirst, first
from skeletons.gui.server_events import IEventsCache
PERSONAL_MISSION_TOKEN = 'token:pt:final:s%s:t%s'
MAIN_PERSONAL_MISSION_TOKEN = PERSONAL_MISSION_TOKEN + ':main'
ADD_PERSONAL_MISSION_TOKEN = PERSONAL_MISSION_TOKEN + ':add'
PERSONAL_MISSION_COMPLETE_TOKEN = PERSONAL_MISSION_TOKEN + ':complete'
PERSONAL_MISSION_BADGES_TOKEN = 'token:pt:s%s:badges'
FINAL_PERSONAL_MISSION_TOKEN = 'pt_final_s%s_t%s'
CHAMPION_BADGES_BY_BRANCH = {PM_BRANCH.REGULAR: 'pt_final_badge',
 PM_BRANCH.PERSONAL_MISSION_2: 'pt_final_badge_s2'}
OPERATIONS_TOKENS_PATTERNS = (PERSONAL_MISSION_TOKEN, MAIN_PERSONAL_MISSION_TOKEN, ADD_PERSONAL_MISSION_TOKEN)
BRANCH_TO_OPERATION_IDS = {PM_BRANCH.REGULAR: (1, 2, 3, 4),
 PM_BRANCH.PERSONAL_MISSION_2: (5, 6, 7)}
OPERATION_ID_TO_BRANCH = {operationsId:branch for branch in BRANCH_TO_OPERATION_IDS.iterkeys() for operationsId in BRANCH_TO_OPERATION_IDS[branch]}
CHAMPION_BADGE_AT_OPERATION_ID = {operationIds[-1]:CHAMPION_BADGES_BY_BRANCH[branch] for branch, operationIds in BRANCH_TO_OPERATION_IDS.iteritems()}

def getBranchByOperationId(operationId):
    return OPERATION_ID_TO_BRANCH.get(operationId, None)


def getFinalTokenQuestIdByOperationId(operationId):
    season = {PM_BRANCH.REGULAR: 1,
     PM_BRANCH.PERSONAL_MISSION_2: 2}
    result = [FINAL_PERSONAL_MISSION_TOKEN % (season[getBranchByOperationId(operationId)], operationId)]
    if operationId in CHAMPION_BADGE_AT_OPERATION_ID:
        result.append(CHAMPION_BADGE_AT_OPERATION_ID[operationId])
    return tuple(result)


def getAdditionalTokenQuestIdByOperationId(operationId, addCamouflage=False, addBadge=False):
    result = []
    finalId = getFinalTokenQuestIdByOperationId(operationId)[0]
    if addCamouflage:
        result.append(''.join((finalId, '_camouflage')))
    if addBadge:
        branch = getBranchByOperationId(operationId)
        if branch == PM_BRANCH.REGULAR:
            result.append(''.join((finalId, '_badge2')))
        elif branch == PM_BRANCH.PERSONAL_MISSION_2:
            result.append(''.join((finalId, '_badge')))
    return result


PM_FINAL_TOKEN_QUEST_IDS_BY_OPERATION_ID = {opId:getFinalTokenQuestIdByOperationId(opId) for opId in OPERATION_ID_TO_BRANCH.iterkeys()}

def getPersonalMissionDataFromToken(token):
    eventsCache = dependency.instance(IEventsCache)
    for branch in PM_BRANCH.ACTIVE_BRANCHES:
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


def addQuestTokenFinder(operation):
    return tokenFinder(ADD_PERSONAL_MISSION_TOKEN % (operation.getCampaignID(), operation.getID()))


def tokenBonusFinder(tokenID):

    def finder(bonus):
        return bonus.getName() == 'battleToken' and tokenID in bonus.getTokens()

    return finder


def operationCompletionBonusFinder(operation):
    return tokenBonusFinder(PERSONAL_MISSION_COMPLETE_TOKEN % (operation.getCampaignID(), operation.getID()))


def badgeBonusFinder():

    def finder(bonus):
        return bonus.getName() == 'dossier' and bonus.getBadges()

    return finder
