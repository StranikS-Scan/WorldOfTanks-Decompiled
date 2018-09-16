# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/football_config.py


class MILESTONE(object):
    NONE = ''
    FIRST = 'fb18:milestone_1'
    SECOND = 'fb18:milestone_2'
    THIRD = 'fb18:milestone_3'
    ALL = (THIRD, SECOND, FIRST)


MILESTONE_IDX = {milestone:idx for idx, milestone in enumerate(MILESTONE.ALL + (MILESTONE.NONE,))}

class MILESTONE_SCORE(object):
    FIRST = 30
    SECOND = 60
    THIRD = 100


class DECK_TYPE(object):
    STRIKER = 0
    MIDFIELDER = 1
    DEFENDER = 2


CARDS_BY_TOKEN = {'img:fb18_uni_small:fb18us': (1, 0, 0, 0),
 'img:fb18_uni_big:fb18ub': (2, 0, 0, 0),
 'img:fb18_str_small:fb18ss': (0, 1, 0, 0),
 'img:fb18_str_big:fb18sb': (0, 2, 0, 0),
 'img:fb18_mid_small:fb18ms': (0, 0, 1, 0),
 'img:fb18_mid_big:fb18mb': (0, 0, 2, 0),
 'img:fb18_def_small:fb18ds': (0, 0, 0, 1),
 'img:fb18_def_big:fb18db': (0, 0, 0, 2),
 'img:fb18_str_full:fb18sf': (0, 6, 0, 0),
 'img:fb18_mid_full:fb18mf': (0, 0, 12, 0),
 'img:fb18_def_full:fb18df': (0, 0, 0, 12),
 'img:fb18_full:fb18f': (0, 6, 12, 12)}
PACKET_TOKENS = CARDS_BY_TOKEN.keys()
DECK_TOKENS = (('fb18:deck_0', 'fb18:deck_1'), ('fb18:deck_2', 'fb18:deck_3', 'fb18:deck_4', 'fb18:deck_5'), ('fb18:deck_6', 'fb18:deck_7', 'fb18:deck_8', 'fb18:deck_9'))
DECK_TYPES = {'fb18:deck_0': DECK_TYPE.STRIKER,
 'fb18:deck_1': DECK_TYPE.STRIKER,
 'fb18:deck_2': DECK_TYPE.MIDFIELDER,
 'fb18:deck_3': DECK_TYPE.MIDFIELDER,
 'fb18:deck_4': DECK_TYPE.MIDFIELDER,
 'fb18:deck_5': DECK_TYPE.MIDFIELDER,
 'fb18:deck_6': DECK_TYPE.DEFENDER,
 'fb18:deck_7': DECK_TYPE.DEFENDER,
 'fb18:deck_8': DECK_TYPE.DEFENDER,
 'fb18:deck_9': DECK_TYPE.DEFENDER}
DECKS_NUM = 10
DECK_TOKEN_TEMPLATE = 'fb18:deck_{num:d}'
MAX_CARDS_IN_DECK = 3
CARD_CREDIT_COMPENSATION = 30000
BUFFON_TOKEN = 'img:fb18_buffon_recruit:fb18br'
MILESTONE_TOKENS = {MILESTONE_SCORE.FIRST: 'fb18:milestone_1',
 MILESTONE_SCORE.SECOND: 'fb18:milestone_2',
 MILESTONE_SCORE.THIRD: 'fb18:milestone_3'}
MILESTONE_SCORES = {token:score for score, token in MILESTONE_TOKENS.iteritems()}
STACK_MULTIPLIERS = {0: 0,
 1: 3,
 2: 6,
 3: 10}
BUFFON_PURCHASE_ALERT_INTERVAL = 604800

def getObtainedMilestones(prevMilestone, currMilestone):
    currMilestoneIdx = MILESTONE_IDX[currMilestone]
    prevMilestoneIdx = MILESTONE_IDX[prevMilestone]
    milestoneTokens = []
    for idx in range(currMilestoneIdx, prevMilestoneIdx):
        milestoneTokens.append(MILESTONE.ALL[idx])

    return milestoneTokens


def calculateProgress(decks):
    progress = 0
    for stackCount in decks.itervalues():
        progress += STACK_MULTIPLIERS.get(stackCount, 0)

    return progress


def calculateMilestone(progress):
    reachedMilestone = MILESTONE.NONE
    for milestone in reversed(MILESTONE.ALL):
        score = MILESTONE_SCORES[milestone]
        if progress >= score:
            reachedMilestone = milestone

    return reachedMilestone
