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
    """
    :param token:
    :return: isPersonalMissionsToken, operationID, isMain
    """
    eventsCache = dependency.instance(IEventsCache)
    for opID in eventsCache.personalMissions.getOperations().iterkeys():
        if token == MAIN_PERSONAL_MISSION_TOKEN % opID:
            return (True, opID, True)
        if token == ADD_PERSONAL_MISSION_TOKEN % opID:
            return (True, opID, False)

    return (False, None, None)


def getQuestsByTokenAndBonus(quests, tokenFinder=None, bonusFinder=None):
    """
    Finds all quests that match given finders
    :param quests: quests dictionary
    :param tokenFinder: finder for token requirement (None means first)
    :param bonusFinder: finder for bonus requirement (None means first)
    :return: matched quests dictionary
    """
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
    """
    Finds first quest that matches finder requirements
    """
    return first(getQuestsByTokenAndBonus(quests, tokenFinder, bonusFinder).itervalues())


def tokenFinder(tokenID):
    """
    Finder functor that searches token by given ID
    """

    def finder(token):
        return token.getID() == tokenID

    return finder


def multipleTokenFinder(tokenIDs):
    """
    Finder functor that searches token within IDs list
    """

    def finder(token):
        return token.getID() in tokenIDs

    return finder


def pmTokenDetector(operationsCount):
    """
    Finder functor which allows to detect any token related to personal mission
    """
    tokensList = []
    for operationID in range(1, operationsCount + 1):
        tokensList.extend([ pattern % operationID for pattern in OPERATIONS_TOKENS_PATTERNS ])

    tokensList.append(PERSONAL_MISSION_BADGES_TOKEN)
    return multipleTokenFinder(tokensList)


def mainQuestTokenFinder(operationID):
    """
    Finder functor that searches main token for operation
    """
    return tokenFinder(MAIN_PERSONAL_MISSION_TOKEN % operationID)


def addQuestTokenFinder(operationID):
    """
    Finder functor that searches additional token for operation
    """
    return tokenFinder(ADD_PERSONAL_MISSION_TOKEN % operationID)


def tokenBonusFinder(tokenID):
    """
    Finder functor that searches token bonus
    """

    def finder(bonus):
        return bonus.getName() == 'battleToken' and tokenID in bonus.getTokens()

    return finder


def operationCompletionBonusFinder(operationID):
    """
    Finder functor that searches operation completion token bonus
    """
    return tokenBonusFinder(PERSONAL_MISSION_COMPLETE_TOKEN % operationID)


def freeTokenBonusFinder():
    """
    Finder functor that searches free token bonus
    """
    return tokenBonusFinder(PERSONAL_QUEST_FREE_TOKEN_NAME)


def badgeBonusFinder():
    """
    Finder functor that searches player badge bonus
    """

    def finder(bonus):
        return bonus.getName() == 'dossier' and bonus.getBadges()

    return finder
