# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/difficulty_level_controller.py
from __future__ import absolute_import
from future.utils import viewvalues
import typing
from collections import namedtuple
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from last_stand.gui.ls_gui_constants import FUNCTIONAL_FLAG
from last_stand.gui import ls_account_settings
from last_stand.gui.ls_gui_constants import DifficultyLevel, QUEUE_TYPE_TO_DIFFICULTY_LEVEL
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getFirstNewStatusUnlockLevel
from last_stand.gui.prb_control.entities.squad.entity import LastStandSquadEntity
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from last_stand_common.last_stand_constants import LAST_STAND_QUEUE_TYPES, QUEUE_TYPE, DifficultyLevelToken, TOKEN_DIFFICULTY_LEVEL_TO_QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.entity import BasePrbEntity
_Level = namedtuple('_Level', ('queueType', 'level', 'isUnlock'))

class DifficultyLevelController(IDifficultyLevelController, IGlobalListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self):
        super(DifficultyLevelController, self).__init__()
        self._em = EventManager()
        self.onChangeDifficultyLevelStatus = Event(self._em)
        self.onChangeDifficultyLevel = Event(self._em)
        self.onLevelsInfoReady = Event(self._em)
        self.selectedLevel = DifficultyLevel.EASY
        self.items = {}

    @prbEntityProperty
    def prbEntity(self):
        return None

    def onPrbEntitySwitched(self):
        if self.prbEntity and self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.LAST_STAND:
            if isinstance(self.prbEntity, LastStandSquadEntity) and not self.prbEntity.isCommander():
                return
            self.selectLevel(self.getLastSelectedLevel())

    def onDequeued(self, queueType, *args):
        if queueType in LAST_STAND_QUEUE_TYPES:
            self.selectLevel(self.getLastSelectedLevel())

    def init(self):
        super(DifficultyLevelController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self._onSyncTokensCompleted})

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.items = {}
        self._em.clear()
        super(DifficultyLevelController, self).fini()

    def onDisconnected(self):
        super(DifficultyLevelController, self).onDisconnected()
        self.stopGlobalListening()

    def onAvatarBecomePlayer(self):
        super(DifficultyLevelController, self).onAvatarBecomePlayer()
        self.stopGlobalListening()

    def onAccountBecomePlayer(self):
        super(DifficultyLevelController, self).onAccountBecomePlayer()
        self.selectedLevel = self.getLastSelectedLevel()

    def getLastSelectedLevel(self):
        level = getFirstNewStatusUnlockLevel()
        if level:
            levelItem = findFirst(lambda item: item.level == level, viewvalues(self.items))
        else:
            cashedLvl = DifficultyLevel(ls_account_settings.getSettings(AccountSettingsKeys.SELECTED_LEVEL))
            levelItem = findFirst(lambda item: item.level == cashedLvl, viewvalues(self.items))
        return levelItem.level if levelItem and levelItem.isUnlock else DifficultyLevel.EASY

    def getLevelsInfo(self):
        return sorted(viewvalues(self.items), key=lambda item: item.level)

    def getLevelInfo(self, levelNum):
        for levelItem in viewvalues(self.items):
            if levelItem.level.value == levelNum:
                return levelItem

    def onLobbyInited(self, event):
        self.startGlobalListening()

    def onLobbyStarted(self, ctx):
        super(DifficultyLevelController, self).onLobbyStarted(ctx)
        tokens = self._itemsCache.items.tokens.getTokens()
        for difficultyLevelToken in DifficultyLevelToken.ALL_LEVELS:
            queueType, level = self._getLevelInfo(difficultyLevelToken)
            isUnlock = difficultyLevelToken in DifficultyLevelToken.ALWAYS_AVIABLED or difficultyLevelToken in tokens
            self.items[difficultyLevelToken] = _Level(queueType, level, isUnlock)
            if isUnlock:
                self.__setNewStatus(level)
                self.onChangeDifficultyLevelStatus(self.items[difficultyLevelToken])

        self.onLevelsInfoReady()

    def selectLevel(self, level):
        if level == self.selectedLevel:
            return
        wasBattleEnabled = self.lsCtrl.isBattlesEnabled()
        self.selectedLevel = level
        difficultyLevel = findFirst(lambda item: item.level == level, viewvalues(self.items))
        if difficultyLevel and difficultyLevel.isUnlock:
            ls_account_settings.setSettings(AccountSettingsKeys.SELECTED_LEVEL, level.value)
            unlockedLevels = ls_account_settings.getSettings(AccountSettingsKeys.UNLOCK_LEVELS)
            if unlockedLevels.get(level.value, {}).get('isNew', False):
                ls_account_settings.setNewStatusUnlockLevel(level, False)
        self.onChangeDifficultyLevel(level)
        if wasBattleEnabled != self.lsCtrl.isBattlesEnabled():
            g_eventDispatcher.updateUI()

    def getSelectedLevel(self):
        return self.selectedLevel

    def getCurrentQueueType(self):
        difficultyLevel = findFirst(lambda item: item.level == self.selectedLevel, viewvalues(self.items))
        return difficultyLevel.queueType if difficultyLevel else QUEUE_TYPE.LAST_STAND

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
        unlockedLevels = ls_account_settings.getSettings(AccountSettingsKeys.UNLOCK_LEVELS)
        if level.value not in unlockedLevels:
            ls_account_settings.setNewStatusUnlockLevel(level, True)
            if not self.prbEntity:
                return
            if self.prbEntity.isInQueue():
                return
            if not self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.LAST_STAND:
                return
            if isinstance(self.prbEntity, LastStandSquadEntity) and not self.prbEntity.isCommander():
                return
            self.selectLevel(level)
