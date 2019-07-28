# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/front_progress.py
import logging
from account_helpers.settings_core.ServerSettingsManager import UI_GAME_EVENT_KEYS
from game_event_progress import GameEventProgress, GameEventProgressItem, GameEventProgressItemEmpty
from gui.server_events.awards_formatters import getEventAwardFormatter
from gui.server_events.bonuses import mergeBonuses
from gui.server_events.conditions import getTokenNeededCountInCondition
_logger = logging.getLogger(__name__)
_FRONT_BIT_MASK_LENGTH = 8

class FrontProgress(GameEventProgress):

    def __init__(self, frontID):
        super(FrontProgress, self).__init__('se1_2019_front_{}'.format(frontID), 'progress', 'final_reward', 'bonuses', 'se1_front_{}_bought_last_level'.format(frontID))
        self._id = frontID

    def getID(self):
        return self._id

    def getProgressTokenName(self):
        return 'se1_front_{}_event_points'.format(self.getID())

    def getFrontMarkTokenName(self):
        return 'img:front_mark_{}:webId'.format(self.getID())

    def getFrontMarksCount(self):
        return self.getFrontMarksTotalCount() if self.isCompleted() else self.eventsCache.questsProgress.getTokenCount(self.getFrontMarkTokenName())

    def getFrontMarksTotalCountForLevel(self, level):
        return sum((self.items[itemID].getMaxFrontMarksCount() for itemID in xrange(level + 1)))

    def getFrontMarksTotalCount(self):
        return self.getFrontMarksTotalCountForLevel(self.getMaxLevel())

    def getBonuses(self):
        if not self.items:
            return []
        bonuses = [ bonus for item in self.items for bonus in item.getBonuses() ]
        return mergeBonuses(bonuses)

    def getBonusesFormatted(self):
        return getEventAwardFormatter().format(self.getBonuses())

    def isAwardShown(self, index):
        offset = _FRONT_BIT_MASK_LENGTH * self.getID() + index
        return self._getGameEventServerSetting(UI_GAME_EVENT_KEYS.FRONT_AWARD_SHOWN, 0) & 1 << offset

    def setAwardIsShown(self, index):
        offset = _FRONT_BIT_MASK_LENGTH * self.getID() + index
        oldValue = self._getGameEventServerSetting(UI_GAME_EVENT_KEYS.FRONT_AWARD_SHOWN, 0)
        newValue = oldValue | 1 << offset
        self.settingsCore.serverSettings.saveInGameEventStorage({UI_GAME_EVENT_KEYS.FRONT_AWARD_SHOWN: newValue})

    def _createProgressItem(self, quest):
        return FrontProgressItem(self, quest)

    def _createProgressItemEmpty(self):
        return FrontProgressItemEmpty(self)


class FrontProgressItem(GameEventProgressItem):

    def getMaxFrontMarksCount(self):
        return getTokenNeededCountInCondition(self._quest, self._progressController.getFrontMarkTokenName(), default=0)


class FrontProgressItemEmpty(GameEventProgressItemEmpty):

    def getMaxFrontMarksCount(self):
        pass
