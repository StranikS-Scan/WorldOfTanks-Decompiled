# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_hints.py
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE, IS_DEVELOPMENT
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import TutorialEvent
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from skeletons.tutorial import ITutorialLoader

class BattleMattersHintsHelper(object):
    __settingsCache = dependency.descriptor(ISettingsCache)
    __nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__hints', '__hasHintListeners', '__battleMattersController')

    def __init__(self, controller):
        super(BattleMattersHintsHelper, self).__init__()
        self.__hasHintListeners = False
        self.__battleMattersController = controller
        self.__hints = self.__getDefaultHints()
        self.__addHintsListeners()
        g_playerEvents.onDisconnected += self.__onDisconnected

    def fini(self):
        self.__removeHintsListeners()
        g_playerEvents.onDisconnected -= self.__onDisconnected
        self.__battleMattersController = None
        self.__stopHints()
        return

    @staticmethod
    def __getDefaultHints():
        return (EntryPointHint(), FightBtnMultiShowHint())

    def __addHintsListeners(self):
        self.__hasHintListeners = True
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
        self.__nyController.onNyViewVisibilityChange += self.__onNyViewVisibilityChange

    def __removeHintsListeners(self):
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        g_playerEvents.onAccountBecomePlayer -= self.__onAccountBecomePlayer
        self.__battleMattersController.onStateChanged -= self.__onStateChanged
        self.__settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted
        self.__nyController.onNyViewVisibilityChange -= self.__onNyViewVisibilityChange
        self.__hasHintListeners = False

    def __onAccountBecomePlayer(self):
        self.__battleMattersController.onStateChanged += self.__onStateChanged
        self.__settingsCache.onSyncCompleted += self.__onSettingsSyncCompleted
        self.__startHints()

    def __onDisconnected(self):
        self.__hints = self.__getDefaultHints()
        if not self.__hasHintListeners:
            self.__addHintsListeners()

    def __onAccountBecomeNonPlayer(self):
        self.__stopHints()
        self.__battleMattersController.onStateChanged -= self.__onStateChanged
        self.__settingsCache.onSyncCompleted -= self.__onSettingsSyncCompleted

    def __onSettingsSyncCompleted(self):
        self.__checkHints()

    def __onNyViewVisibilityChange(self, _):
        self.__onStateChanged()

    def __checkHints(self):
        availableHints = []
        for hint in self.__hints:
            if hint.isShown() and not hint.canBeShownInFuture():
                hint.stop()
            availableHints.append(hint)

        self.__hints = availableHints
        if self.__hints:
            self.__startHints()
        else:
            self.__removeHintsListeners()

    def __startHints(self):
        if self.__battleMattersController.isActive() and not self.__nyController.isNyViewShown():
            for hint in self.__hints:
                hint.start()

    def __stopHints(self):
        for hint in self.__hints:
            hint.stop()

    def __onStateChanged(self):
        if self.__battleMattersController.isActive() and not self.__nyController.isNyViewShown():
            self.__startHints()
        else:
            self.__stopHints()


class _BMManualTriggeredHint(object):
    _eventsCache = dependency.descriptor(IEventsCache)
    _battleMattersController = dependency.descriptor(IBattleMattersController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _tutorialLoader = dependency.descriptor(ITutorialLoader)
    _HINT_NAME = None
    CONTROL_NAME = None
    __slots__ = ('_isStarted', '_battleMattersController', '_isHintVisible', '_controlOnScene', '_controlIsEnabled')

    def __init__(self):
        super(_BMManualTriggeredHint, self).__init__()
        self._isStarted = False
        self._isHintVisible = False
        self._controlOnScene = False
        self._controlIsEnabled = False

    def getName(self):
        return self.CONTROL_NAME

    def isShown(self):
        return bool(self._settingsCore.serverSettings.getOnceOnlyHintsSetting(self._HINT_NAME, default=False))

    def start(self):
        if not self._isStarted and self.canBeShownInFuture():
            self._controlOnScene = self.__checkControlOnScene()
            if self._controlOnScene:
                self.__setTriggers()
            self.__addTutorialListeners()
            self._eventsCache.onSyncCompleted += self._onEventsCacheSyncCompleted
            self._onStart()

    def stop(self):
        if self._isStarted:
            self.__removeTutorialListeners()
            self._eventsCache.onSyncCompleted -= self._onEventsCacheSyncCompleted
            self._onStop()
            self._isHintVisible = False

    def canBeShownInFuture(self):
        return not self.isShown()

    @staticmethod
    def _getHintSettings():
        return {}

    def _onStart(self):
        self._isStarted = True

    def _onStop(self):
        self._isStarted = False

    def _onEventsCacheSyncCompleted(self):
        raise NotImplementedError

    def _isReadyToShow(self):
        return self._controlOnScene and self._controlIsEnabled

    def _show(self):
        if not self._isHintVisible:
            self._isHintVisible = self._tutorialLoader.gui.showInteractiveHint(self.CONTROL_NAME, self._getHintSettings(), [], False)
            if self._isHintVisible:
                g_eventBus.handleEvent(TutorialEvent(TutorialEvent.IMPORTANT_HINT_SHOWING, state=True), scope=EVENT_BUS_SCOPE.GLOBAL)

    def _hide(self):
        if self._isHintVisible:
            self._tutorialLoader.gui.closeInteractiveHint(self.CONTROL_NAME)
            g_eventBus.handleEvent(TutorialEvent(TutorialEvent.IMPORTANT_HINT_SHOWING, state=False), scope=EVENT_BUS_SCOPE.GLOBAL)
        self._isHintVisible = False

    def _checkControlConditions(self, componentIsEnabled):
        pass

    def _onItemFound(self, event):
        if event.targetID == self.CONTROL_NAME:
            self._controlOnScene = True
            self.__setTriggers()

    def _onItemLost(self, event):
        if event.targetID == self.CONTROL_NAME:
            self._controlOnScene = False
            self._isHintVisible = False

    def _onTriggerActivated(self, event):
        if event.targetID == self.CONTROL_NAME:
            self._controlIsEnabled = event.componentState
            self._checkControlConditions(self._controlIsEnabled)

    def _getTutorialTriggers(self):
        return (TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE,)

    def __setTriggers(self):
        triggers = self._getTutorialTriggers()
        if triggers:
            self._tutorialLoader.gui.setTriggers(self.CONTROL_NAME, triggers)

    def __checkControlOnScene(self):
        return self.CONTROL_NAME in self._tutorialLoader.gui.getFoundComponentsIDs()

    def __addTutorialListeners(self):
        addListener = g_eventBus.addListener
        addListener(events.TutorialEvent.ON_COMPONENT_FOUND, self._onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(events.TutorialEvent.ON_COMPONENT_LOST, self._onItemLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        if self._getTutorialTriggers():
            addListener(events.TutorialEvent.ON_TRIGGER_ACTIVATED, self._onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)

    def __removeTutorialListeners(self):
        removeListener = g_eventBus.removeListener
        removeListener(events.TutorialEvent.ON_COMPONENT_FOUND, self._onItemFound, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(events.TutorialEvent.ON_COMPONENT_LOST, self._onItemLost, scope=EVENT_BUS_SCOPE.GLOBAL)
        if self._getTutorialTriggers():
            removeListener(events.TutorialEvent.ON_TRIGGER_ACTIVATED, self._onTriggerActivated, scope=EVENT_BUS_SCOPE.GLOBAL)


class FightBtnMultiShowHint(_BMManualTriggeredHint, IGlobalListener):
    CONTROL_NAME = 'FightButton'
    _HINT_NAME = OnceOnlyHints.BATTLE_MATTERS_FIGHT_BUTTON_HINT
    __slots__ = ('__waitingBattle',)

    def __init__(self):
        super(FightBtnMultiShowHint, self).__init__()
        self.__waitingBattle = False

    def onPrbEntitySwitched(self):
        self.__waitingBattle = self.prbEntity.getQueueType() == QUEUE_TYPE.RANDOMS or self.__isDevBattle()
        if self.__waitingBattle:
            g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        else:
            g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        self.__checkFightBtnHint()

    def canBeShownInFuture(self):
        result = super(FightBtnMultiShowHint, self).canBeShownInFuture()
        if result and not self._eventsCache.waitForSync:
            quests = self._battleMattersController.getRegularBattleMattersQuests()
            firstQuestIsNotCompleted = quests and not quests[0].isCompleted()
            result = firstQuestIsNotCompleted
        return result

    @staticmethod
    def _getHintSettings():
        return {'updateRuntime': True}

    def _onStart(self):
        super(FightBtnMultiShowHint, self)._onStart()
        self.__waitingBattle = False
        if self.canBeShownInFuture():
            if self.prbDispatcher is None:
                g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated
            else:
                self.startGlobalListening()
            if self._controlOnScene:
                self._controlIsEnabled = self.__isReadyToFightInRandom()
                self.__checkFightBtnHint()
        return

    def _onStop(self):
        super(FightBtnMultiShowHint, self)._onStop()
        if not self.__waitingBattle:
            g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        self.stopGlobalListening()
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        self._hide()
        self.__resetTriggers()

    def _checkControlConditions(self, componentIsEnabled):
        self.__checkFightBtnHint()

    def _onEventsCacheSyncCompleted(self):
        self.__checkFightBtnHint()

    def _isReadyToShow(self):
        return super(FightBtnMultiShowHint, self)._isReadyToShow() and self.canBeShownInFuture() and self.__isReadyToFightInRandom()

    def __isDevBattle(self):
        return IS_DEVELOPMENT and self.prbEntity.getModeFlags() == FUNCTIONAL_FLAG.TRAINING

    def __resetTriggers(self):
        self._tutorialLoader.gui.setTriggers(self.CONTROL_NAME, [])

    def __onAvatarBecomePlayer(self):
        if BigWorld.player().arenaBonusType in ARENA_BONUS_TYPE.RANDOM_RANGE:
            self._settingsCore.serverSettings.setOnceOnlyHintsSettings({self._HINT_NAME: True})
        self.__waitingBattle = False
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()

    def __checkFightBtnHint(self):
        if self._isReadyToShow():
            self._show()
        elif self.canBeShownInFuture():
            self._hide()
        else:
            self.stop()

    def __isReadyToFightInRandom(self):
        prbEntity = self.prbEntity
        if prbEntity is not None:
            isRandom = prbEntity and prbEntity.getEntityFlags() != FUNCTIONAL_FLAG.UNDEFINED and prbEntity.getQueueType() == QUEUE_TYPE.RANDOMS
            prbDispatcher = self.prbDispatcher
            if isRandom and prbDispatcher is not None:
                items = battle_selector_items.getItems()
                selected = items.update(prbDispatcher.getFunctionalState())
                return prbEntity.canPlayerDoAction().isValid and not selected.isLocked()
        else:
            return False
        return


class EntryPointHint(_BMManualTriggeredHint):
    __itemsCache = dependency.descriptor(IItemsCache)
    CONTROL_NAME = 'BattleMattersEntryPoint'
    _HINT_NAME = OnceOnlyHints.BATTLE_MATTERS_ENTRY_POINT_BUTTON_HINT
    __slots__ = ()

    @staticmethod
    def _getHintSettings():
        return {'updateRuntime': True,
         'hintText': backport.text(R.strings.battle_matters.entryPoint.hint()),
         'hasArrow': True,
         'arrowDir': 'B',
         'arrowLoop': True,
         'positionValue': 0.5}

    def _onStart(self):
        super(EntryPointHint, self)._onStart()
        self.__checkHint()

    def _onStop(self):
        super(EntryPointHint, self)._onStop()
        self._hide()

    def _onEventsCacheSyncCompleted(self):
        self.__checkHint()

    def _isReadyToShow(self):
        result = False
        if self._controlOnScene and not self._eventsCache.waitForSync:
            result = self._battleMattersController.getCompletedBattleMattersQuestsCount() >= 1 and not self.isShown()
        return result

    def _onItemFound(self, event):
        super(EntryPointHint, self)._onItemFound(event)
        if event.targetID == self.CONTROL_NAME:
            self.__checkHint()

    def _onItemLost(self, event):
        if event.targetID == self.CONTROL_NAME:
            self._hide()
        super(EntryPointHint, self)._onItemLost(event)

    def _getTutorialTriggers(self):
        return []

    def __checkHint(self):
        if self._isReadyToShow():
            self._show()
