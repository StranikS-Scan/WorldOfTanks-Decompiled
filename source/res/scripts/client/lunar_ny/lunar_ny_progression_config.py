# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_progression_config.py
import logging
import typing
from gui.server_events.bonuses import mergeBonuses, splitDossierBonus
from gifts.gifts_common import LUNAR_NY_PROGRESSION_QUEST_TOKEN
from lunar_ny.lunar_ny_constants import LUNAR_NY_PROGRESSION_QUEST_ID_FORMAT, LUNAR_NY_PROGRESSION_QUEST_ID
from shared_utils import first
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)

class LunarNYProgressionConfig(object):
    __slots__ = ('__levels', '__maxLevel')

    def __init__(self, levelQuests):
        self.__levels = getLevelsFromQuest(levelQuests)
        self.__maxLevel = len(self.__levels)

    def getLevelInfo(self, level):
        return self.__levels[level] if 0 <= level < self.__maxLevel else None

    def getLevels(self):
        return self.__levels[:]


class LunarNYProgressionLevel(object):
    __slots__ = ('__bonuses', '__level', '__minEnvelopes', '__maxEnvelopes')

    def __init__(self, levelID, minEnvelopes, maxEnvelopes, bonuses):
        self.__level = levelID
        self.__minEnvelopes = minEnvelopes
        self.__maxEnvelopes = maxEnvelopes
        self.__bonuses = bonuses

    def __repr__(self):
        return '{}(minEnvelopes={}, maxEnvelopes={}, bonuses={}, levelID={})'.format(self.__class__.__name__, self.__minEnvelopes, self.__maxEnvelopes, self.__bonuses, self.__level)

    def __cmp__(self, other):
        return NotImplemented if not isinstance(other, self.__class__) else cmp(self.__level, other.getLevel())

    def __eq__(self, other):
        return False if not isinstance(other, self.__class__) else self.getLevel() == other.getLevel()

    def getBonuses(self):
        return self.__bonuses[:] if self.__bonuses else ()

    def getEnvelopesRange(self):
        return (self.__minEnvelopes, self.__maxEnvelopes)

    def getLevel(self):
        return self.__level


def getEnvelopesRequiredFromQuest(questData):
    return first((t.getNeededCount() for t in questData.accountReqs.getTokens() if t.getID() == LUNAR_NY_PROGRESSION_QUEST_TOKEN), default=0)


def getLevelsFromQuest(levelQuests):
    lastRequiredEnvelopes = 0
    levels = []
    lastLevelBonusesForMerge = []
    maxLevelIdx = len(levelQuests) + 1
    for levelIdx in range(1, maxLevelIdx + 1):
        if levelIdx <= len(levelQuests):
            quest = levelQuests.get(LUNAR_NY_PROGRESSION_QUEST_ID_FORMAT.format(levelIdx), None)
            if quest is None:
                _logger.error('Wrong lunar NY progression level quest format!')
                return []
            requiredEnvelopes = getEnvelopesRequiredFromQuest(quest)
        else:
            quest = None
            requiredEnvelopes = float('inf')
        if requiredEnvelopes < 1:
            _logger.error('Wrong lunar NY progression level quest format!')
            return []
        if quest is not None:
            bonuses = getLevelBonuses(quest, lastLevelBonusesForMerge)
            lastLevelBonusesForMerge.extend(getBonusesForMerge(quest.getBonuses()))
        else:
            bonuses = None
        levels.append(LunarNYProgressionLevel(levelIdx - 1, lastRequiredEnvelopes, requiredEnvelopes - 1, bonuses))
        lastRequiredEnvelopes = requiredEnvelopes

    return levels


def isLunarNYProgressionQuest(qID):
    return qID.startswith(LUNAR_NY_PROGRESSION_QUEST_ID)


def getLevelFromQuestID(qID):
    return int(qID.split('_')[-1])


_DOSSIER_TO_MERGE = (('achievements', 'lunarNY2022Progression'),)

def getBonusesForMerge(bonuses):
    res = []
    for bonus in bonuses:
        if bonus.getName() == 'dossier':
            dossierBonuses = splitDossierBonus(bonus)
            for dossierBonus in dossierBonuses:
                if dossierBonus.getRecords().keys()[0] in _DOSSIER_TO_MERGE:
                    res.append(dossierBonus)

    return res


def getLevelBonuses(quest, lastLevelBonusesForMerge):
    bonuses = quest.getBonuses()
    needMergeLastBonuses = False
    for bonus in bonuses:
        if bonus.getName() == 'dossier':
            for record in bonus.getRecords():
                if record in _DOSSIER_TO_MERGE:
                    needMergeLastBonuses = True
                    break

    if needMergeLastBonuses:
        bonuses.extend(lastLevelBonusesForMerge)
        bonuses = mergeBonuses(bonuses)
    return bonuses
