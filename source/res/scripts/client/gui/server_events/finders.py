# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/finders.py
from helpers import dependency
from shared_utils import findFirst, first
from constants import PERSONAL_QUEST_FREE_TOKEN_NAME
from skeletons.gui.server_events import IEventsCache
PERSONAL_MISSION_TOKEN = 'token:pt:final:s1:t%s'
MAIN_PERSONAL_MISSION_TOKEN = PERSONAL_MISSION_TOKEN + ':main'
ADD_PERSONAL_MISSION_TOKEN = PERSONAL_MISSION_TOKEN + ':add'
PERSONAL_MISSION_COMPLETE_TOKEN = PERSONAL_MISSION_TOKEN + ':complete'
PERSONAL_MISSION_BADGES_TOKEN = 'token:pt:s1:badges'
OPERATIONS_TOKENS_PATTERNS = (PERSONAL_MISSION_TOKEN, MAIN_PERSONAL_MISSION_TOKEN, ADD_PERSONAL_MISSION_TOKEN)

def getPersonalMissionDataFromToken(token):
    eventsCache = dependency.instance(IEventsCache)
    for opID in eventsCache.personalMissions.getOperations().iterkeys():
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


def pmTokenDetector(operationsCount):
    tokensList = []
    for operationID in range(1, operationsCount + 1):
        tokensList.extend([ pattern % operationID for pattern in OPERATIONS_TOKENS_PATTERNS ])

    tokensList.append(PERSONAL_MISSION_BADGES_TOKEN)
    return multipleTokenFinder(tokensList)


def mainQuestTokenFinder(operationID):
    return tokenFinder(MAIN_PERSONAL_MISSION_TOKEN % operationID)


def addQuestTokenFinder(operationID):
    return tokenFinder(ADD_PERSONAL_MISSION_TOKEN % operationID)


def tokenBonusFinder(tokenID):

    def finder(bonus):
        return bonus.getName() == 'battleToken' and tokenID in bonus.getTokens()

    return finder


def operationCompletionBonusFinder(operationID):
    return tokenBonusFinder(PERSONAL_MISSION_COMPLETE_TOKEN % operationID)


def freeTokenBonusFinder():
    return tokenBonusFinder(PERSONAL_QUEST_FREE_TOKEN_NAME)


def badgeBonusFinder():

    def finder(bonus):
        return bonus.getName() == 'dossier' and bonus.getBadges()

    return finder
