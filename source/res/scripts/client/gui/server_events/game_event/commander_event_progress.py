# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/commander_event_progress.py
import logging
from game_event_progress import GameEventProgress, GameEventProgressItem, GameEventProgressItemEmpty
from gui.server_events.awards_formatters import getEventAwardFormatter, AWARDS_SIZES
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from gui.server_events.bonuses import TokensBonus
from constants import HE19_MONEY_TOKEN_ID
_BONUS_TANKMEN = 'tankmen'
BONUS_TANKMAN_TOKEN = 'tmanToken'
_BONUS_BATTLE_TOKEN = 'battleToken'
COMMANDER_PROGRESS_TOKEN = 'hw_2019_commander_{}_event_points'
COMMANDER_QUEST_PREFIX = 'hw_commander_'
_logger = logging.getLogger(__name__)

class CommanderEventProgress(GameEventProgress):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, commanderId):
        super(CommanderEventProgress, self).__init__('hw_2019_commander_{}'.format(commanderId), 'progress', 'final_reward', 'bonuses', 'hw_commander_{}_bought_last_level'.format(commanderId))
        self._id = commanderId

    def getID(self):
        return self._id

    def getItemOnLevel(self, level):
        return self._items[min(level, self.getMaxLevel())]

    def getProgressTokenName(self):
        return COMMANDER_PROGRESS_TOKEN.format(self.getID())

    def getCurrentProgressOnLevel(self, level):
        if level >= self.getMaxLevel():
            return self._items[self.getMaxLevel()].getCurrentProgress()
        item = self._items[level + 1]
        return item.getCurrentProgress()

    def getMaxProgressOnLevel(self, level):
        if level >= self.getMaxLevel():
            return self._items[self.getMaxLevel()].getMaxProgress()
        else:
            item = self._items[level]
            return item.getMaxProgress() if item is not None else 0

    def getBonusesForLevel(self, level):
        if level >= self.getMaxLevel():
            return self._items[self.getMaxLevel()].getBonuses()
        else:
            item = self._items[level + 1]
            return [] if item is None else item.getBonuses()

    def getBonusesList(self, currentLevel, awardSize=AWARDS_SIZES.BIG):
        if self.isCompleted():
            return []
        bonuses = getEventAwardFormatter().format(self.getBonusesForLevel(currentLevel))
        return sorted([ self.createBonusToolTip(bonus, awardSize) for bonus in bonuses ], reverse=True)

    def createBonusToolTip(self, bonus, awardSize):
        return {'icon': bonus.getImage(awardSize),
         'tooltip': bonus.tooltip,
         'specialArgs': bonus.specialArgs,
         'specialAlias': bonus.specialAlias,
         'isSpecial': bonus.isSpecial,
         'label': bonus.label}

    def _createProgressItem(self, quest):
        return CommanderGameEventProgressItem(self, quest)

    def _createProgressItemEmpty(self):
        return CommanderGameEventProgressItemEmpty(self)


class CommanderGameEventProgressItem(GameEventProgressItem):

    def getCoinsReward(self):
        for bonus in self.getBonuses():
            if not isinstance(bonus, TokensBonus):
                continue
            for tokenID, tokenRecord in bonus.getTokens().iteritems():
                if tokenID == HE19_MONEY_TOKEN_ID:
                    return tokenRecord.count


class CommanderGameEventProgressItemEmpty(GameEventProgressItemEmpty):

    def getCoinsReward(self):
        pass
