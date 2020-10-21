# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/difficulty_progress.py
import logging
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from game_event_progress import GameEventProgress, GameEventProgressItem, GameEventProgressItemEmpty
DIFFICULTY_LEVEL_PREFIX = 'hw_2020_difficulty_level_'
DIFFICULTY_LEVEL_TOKEN = 'hw_2020_difficulty_level_{}'
DIFFICULTY_EVENT_POINTS_TOKEN = 'hw_2020_difficulty_event_points'
DIFFICULTY_LEVEL_OFFSET = 1
_logger = logging.getLogger(__name__)

class DifficultyEventProgress(GameEventProgress):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(DifficultyEventProgress, self).__init__('hw_2020_difficulty', 'level', 'final_reward', 'bonuses', 'hw_2020_difficulty_level_bought_last_level')

    def getItemOnDifficultyLevel(self, difficultyLevel):
        return self._items[min(difficultyLevel - 1, self.getMaxLevel())]

    def _createProgressItem(self, quest):
        return DifficultyEventProgressItem(self, quest)

    def _createProgressItemEmpty(self):
        return DifficultyGameEventProgressItemEmpty(self)

    def getProgressTokenName(self):
        return DIFFICULTY_EVENT_POINTS_TOKEN

    def isDifficultyLevelShown(self, level):
        value = self._getGameEventServerSetting(UIGameEventKeys.DIFFICULTY_LEVEL_SHOWN, 0)
        offset = DIFFICULTY_LEVEL_OFFSET + (level - 1)
        return value & 1 << offset

    def setDifficultyLevelShown(self, level):
        oldValue = self._getGameEventServerSetting(UIGameEventKeys.DIFFICULTY_LEVEL_SHOWN, 0)
        offset = DIFFICULTY_LEVEL_OFFSET + 1
        flags = (1 << level - 1) - 1
        newValue = oldValue | flags << offset
        self._setGameEventServerSetting(UIGameEventKeys.DIFFICULTY_LEVEL_SHOWN, newValue)

    def _getGameEventServerSetting(self, key, default=None):
        value = self.settingsCore.serverSettings.getGameEventStorage().get(key)
        return value or default

    def _setGameEventServerSetting(self, key, value):
        self.settingsCore.serverSettings.saveInGameEventStorage({key: value})


class DifficultyEventProgressItem(GameEventProgressItem):

    def getDifficultyLevel(self):
        return self.getLevel() + 1


class DifficultyGameEventProgressItemEmpty(GameEventProgressItemEmpty):

    def getDifficultyLevel(self):
        return self.getLevel() + 1
