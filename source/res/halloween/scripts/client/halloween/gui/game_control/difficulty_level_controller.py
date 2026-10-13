# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/difficulty_level_controller.py
from __future__ import absolute_import
import typing
from collections import namedtuple
from future.utils import viewvalues
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from halloween.gui import halloween_account_settings
from halloween.gui.halloween_gui_constants import DifficultyLevel, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween_common.halloween_constants import QUEUE_TYPE, DifficultyLevelToken, TOKEN_DIFFICULTY_LEVEL_TO_QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
_Level = namedtuple('_Level', ('queueType', 'level', 'isUnlock'))

class DifficultyLevelController(IDifficultyLevelController):
    _itemsCache = dependency.descriptor(IItemsCache)
    __halloweenBattleCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self):
        super(DifficultyLevelController, self).__init__()
        self._em = EventManager()
        self.onChangeDifficultyLevelStatus = Event(self._em)
        self.onChangeDifficultyLevel = Event(self._em)
        self.selectedLevel = DifficultyLevel.EASY
        self.items = {}

    def init(self):
        super(DifficultyLevelController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self._onSyncTokensCompleted})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.items = {}
        self._em.clear()
        super(DifficultyLevelController, self).fini()

    def onAccountBecomePlayer(self):
        self.selectedLevel = self.getLastSelectedLevel()

    @staticmethod
    def getLastSelectedLevel():
        return DifficultyLevel(halloween_account_settings.getSettings(AccountSettingsKeys.SELECTED_LEVEL))

    def getLevelsInfo(self):
        return sorted(self.items.values(), key=lambda item: item.level)

    def onLobbyInited(self, event):
        for level in self.items.values():
            if level.isUnlock:
                self.onChangeDifficultyLevelStatus(level)

    def onLobbyStarted(self, ctx):
        super(DifficultyLevelController, self).onLobbyStarted(ctx)
        tokens = self._itemsCache.items.tokens.getTokens()
        for difficultyLevelToken in DifficultyLevelToken.ALL_LEVELS:
            queueType, level = self._getLevelInfo(difficultyLevelToken)
            isUnlock = difficultyLevelToken in DifficultyLevelToken.ALWAYS_AVIABLED or difficultyLevelToken in tokens
            self.items[difficultyLevelToken] = _Level(queueType, level, isUnlock)
            if isUnlock:
                self.__setNewStatus(level)

    def selectLevel(self, level):
        if level == self.selectedLevel:
            return
        wasBattleEnabled = self.__halloweenBattleCtrl.isBattlesEnabled()
        self.selectedLevel = level
        difficultyLevel = findFirst(lambda item: item.level == level, viewvalues(self.items))
        if difficultyLevel and difficultyLevel.isUnlock:
            halloween_account_settings.setSettings(AccountSettingsKeys.SELECTED_LEVEL, level.value)
            unlockedLevels = halloween_account_settings.getSettings(AccountSettingsKeys.UNLOCK_LEVELS)
            if unlockedLevels.get(level.value, {}).get('isNew', False):
                halloween_account_settings.setNewStatusUnlockLevel(level, False)
        self.onChangeDifficultyLevel(level)
        if wasBattleEnabled != self.__halloweenBattleCtrl.isBattlesEnabled():
            g_eventDispatcher.updateUI()

    def getSelectedLevel(self):
        return self.selectedLevel

    def getCurrentQueueType(self):
        difficultyLevel = findFirst(lambda item: item.level == self.selectedLevel, viewvalues(self.items))
        return difficultyLevel.queueType if difficultyLevel else QUEUE_TYPE.HALLOWEEN

    def _onSyncTokensCompleted(self, diff):
        for difficultyLevelToken in DifficultyLevelToken.ALL_LEVELS:
            if difficultyLevelToken not in diff:
                continue
            queueType, level = self._getLevelInfo(difficultyLevelToken)
            isUnlock = bool(diff[difficultyLevelToken])
            if isUnlock:
                self.__setNewStatus(level)
            self.items[difficultyLevelToken] = _Level(queueType, level, isUnlock)
            self.onChangeDifficultyLevelStatus(self.items[difficultyLevelToken])

    def _getLevelInfo(self, token):
        queueType = TOKEN_DIFFICULTY_LEVEL_TO_QUEUE_TYPE[token]
        level = QUEUE_TYPE_TO_DIFFICULTY_LEVEL[queueType]
        return (queueType, level)

    def __setNewStatus(self, level):
        if level == DifficultyLevel.EASY:
            return
        unlockedLevels = halloween_account_settings.getSettings(AccountSettingsKeys.UNLOCK_LEVELS)
        if level.value not in unlockedLevels:
            halloween_account_settings.setNewStatusUnlockLevel(level, True)
