# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/battle_context_hints/battle_context_hints_ctrl.py
import logging
import BigWorld
import typing
import BattleReplay
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control.battle_context_hints.activation_triggers import HintActivationTrigger, PreBattleHintActivationTrigger
from constants import ARENA_PERIOD, IS_DEVELOPMENT
from gui.battle_control.battle_context_hints.applying_triggers import HintApplyingTrigger
from gui.battle_control.battle_context_hints.hint_descriptor import HintDescriptor
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.battle_context_hints.hint_lifecycle_managers import HintLifecycleMgr
from gui.battle_control.battle_context_hints.settings_data_block import HintDataBlock, HintData
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control import event_dispatcher
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.battle_context_hints.loggers import BattleContextHintsLogger
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List
    from gui.impl.battle.battle_page.battle_context_hints.hint_inject_component import HintInjectComponent
    from helpers.server_settings import _BattleContextHintsConfig
_logger = logging.getLogger(__name__)
_AB_TEST_FEATURE_NAME = 'battle_hints'

class _HintDataProcessor(object):

    def __init__(self, hintDataBlock):
        self.__hintDataBlock = hintDataBlock
        self.__watchingCounter = 0
        self.__watchingCounterPerBattle = 0
        self.__battlesCooldown = 0
        self.__currentBattlesCooldown = 0
        self.__lastBattleTriggered = False
        self.__currentBattleTriggered = False
        self.__changed = False

    def __str__(self):
        return '_HintDataProcessor() watchingCounter={} watchingCounterPerBattle={} battlesCooldown={} currentBattlesCooldown={} lastBattleTriggered={} currentBattleTriggered={} changed={}'.format(self.__watchingCounter, self.__watchingCounterPerBattle, self.__battlesCooldown, self.__currentBattlesCooldown, self.__lastBattleTriggered, self.__currentBattleTriggered, self.__changed)

    def read(self):
        data = self.__hintDataBlock.getValue()
        self.__watchingCounter = data.watchingCounter
        self.__watchingCounterPerBattle = data.watchingCounterPerBattle
        self.__battlesCooldown = data.battlesCooldown
        self.__lastBattleTriggered = data.lastBattleTriggered
        self.__currentBattlesCooldown = self.__battlesCooldown
        self.__currentBattleTriggered = False
        self.__changed = False

    def save(self):
        if self.__changed and not BattleReplay.g_replayCtrl.isPlaying:
            data = HintData(self.__watchingCounter, self.__watchingCounterPerBattle, self.__currentBattlesCooldown, self.__currentBattleTriggered)
            self.__hintDataBlock.setValue(data)
        self.__changed = False

    def reset(self, watchingCounter, watchingCounterPerBattle):
        self.__watchingCounter = watchingCounter
        self.__watchingCounterPerBattle = watchingCounterPerBattle
        self.__battlesCooldown = 0
        self.__currentBattlesCooldown = 0
        self.__lastBattleTriggered = False
        self.__currentBattleTriggered = False
        self.__changed = True

    def getWatchingCounter(self):
        return self.__watchingCounter

    def decrementWatchingCounter(self):
        if self.__watchingCounter > 0:
            self.__watchingCounter -= 1
            if self.__watchingCounterPerBattle > 0:
                self.__watchingCounterPerBattle -= 1
            self.__currentBattleTriggered = True
            self.__changed = True
        return self.__watchingCounter

    def setWatchingCounter(self, counter):
        self.__watchingCounter = counter
        self.__changed = True

    def getWatchingCounterPerBattle(self):
        return self.__watchingCounterPerBattle

    def setWatchingCounterPerBattle(self, counter):
        self.__watchingCounterPerBattle = counter
        self.__changed = True

    def getBattlesCooldown(self):
        return self.__battlesCooldown

    def setBattlesCooldown(self, battlesCooldown):
        self.__currentBattlesCooldown = battlesCooldown
        self.__changed = True

    def decrementBattlesCooldown(self):
        if self.__currentBattlesCooldown > 0:
            self.__currentBattlesCooldown -= 1
            self.__changed = True
        return self.__currentBattlesCooldown

    def getLastBattleTriggered(self):
        return self.__lastBattleTriggered

    def setLastBattleTriggered(self, lastBattleTriggered):
        self.__lastBattleTriggered = lastBattleTriggered
        self.__changed = True


class BattleContextHintsController(ViewComponentsController):
    MAX_HINT_DURATION = 60
    __settingsCache = dependency.descriptor(ISettingsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hintsConfig):
        super(BattleContextHintsController, self).__init__()
        self.__hintView = None
        self.__currentComponent = None
        self.__hintsConfig = {conf.hintId:conf for conf in hintsConfig}
        self.__hintsData = {}
        self.__activationTriggers = {}
        self.__currentHintId = None
        self.__currentHintLifecycleMgr = None
        self.__currentApplyingTrigger = None
        self.__countersFromReplay = {}
        self.__isStarted = False
        self.__finishHintCheckDelayer = CallbackDelayer()
        return

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().battleContextHintsConfig

    def getHintsData(self):
        return self.__hintsData

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_CONTEXT_HINTS

    def startControl(self):
        if self.__isStarted:
            return
        if BattleReplay.isServerSideReplay():
            return
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.setDataCallback(BattleReplay.CallbackDataNames.BATTLE_CONTEXT_HINTS_COUNTERS_CALLBACK, self.__saveCountersFromReplay)
        g_eventBus.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)

    def stopControl(self):
        if not self.__isStarted:
            return
        g_eventBus.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        for trigger in self.__activationTriggers.values():
            trigger.stop()

        self.__settingsCache.onSyncCompleted -= self.__onSettingsReady
        if BattleReplay.g_replayCtrl.isPlaying:
            BattleReplay.g_replayCtrl.delDataCallback(BattleReplay.CallbackDataNames.BATTLE_CONTEXT_HINTS_COUNTERS_CALLBACK, self.__saveCountersFromReplay)
        self.__hintsData = {}
        self.__activationTriggers = {}
        self.__finishHint(self.__currentHintId)

    def isStarted(self):
        return self.__isStarted

    def activateHint(self, hintId, context=None, isDisplay=True, force=False, forceDelay=None):
        _logger.info('[BATTLE_CONTEXT_INTS] BattleContextHintsController.activateHint hintId=%s, isDisplay=%s, force=%s, forceDelay=%s', hintId, isDisplay, force, forceDelay)
        if not force and not self.__isStarted:
            return False
        elif not force and self.__isPlayerObserver():
            return False
        elif not force and not self.__isHintAvailable(hintId):
            return False
        elif force or self.__isCanBeDisplayed(hintId):
            logger = BattleContextHintsLogger(hintId)
            logger.logHintActivated()
            if self.__currentHintId is not None:
                if self.__hintsConfig[self.__currentHintId].priority < self.__hintsConfig[hintId].priority and self.__currentHintLifecycleMgr is not None and not self.__currentHintLifecycleMgr.isShowing():
                    self.__finishHint(self.__currentHintId)
                else:
                    return False
            return self.__activateHint(hintId, context, logger, isDisplay, force, forceDelay)
        else:
            return False

    def applyHint(self, hintId, logger, force=False):
        if not force and not self.__isStarted:
            return
        elif not force and not self.__isHintAvailable(hintId):
            return
        elif self.__currentHintId != hintId:
            return
        else:
            if not force:
                self.__decrementWatchingCounter(hintId, logger)
            if self.__currentHintLifecycleMgr is not None:
                self.__currentHintLifecycleMgr.applied()
            self.__finishHint(self.__currentHintId)
            return

    def devResetCounters(self, hintId=None, watchingCounter=None):

        def resetCounter(hintId_):
            if hintId_ not in self.__hintsConfig:
                return
            else:
                conf = self.__hintsConfig[hintId_]
                hintsData = self.__hintsData.get(hintId_, _HintDataProcessor(conf.dataBlock))
                cntr = watchingCounter if watchingCounter is not None else conf.maxWatchingQty
                if cntr >= 0:
                    hintsData.reset(cntr, conf.maxWatchingQtyPerBattle)
                    hintsData.save()
                return

        if hintId is not None:
            resetCounter(hintId)
            return
        else:
            for hId in self.__hintsConfig:
                resetCounter(hId)

            return

    def needToShowPrebattleHint(self):
        return any([ trigger.needToShowHint() for trigger in self.__activationTriggers.values() if isinstance(trigger, PreBattleHintActivationTrigger) ])

    def isHintActivated(self):
        return self.__currentHintId is not None

    def isHintShowing(self):
        return self.__currentHintLifecycleMgr is not None and self.__currentHintLifecycleMgr.isShowing()

    def __handleBattleLoading(self, event):
        if not event.ctx['isShown']:
            return
        if not self.getConfig().enabled:
            return
        self.__hintsData = {}
        self.__activationTriggers = {}
        if self.__settingsCache.settings.isSynced() or BattleReplay.g_replayCtrl.isPlaying:
            self.__onSettingsReady()
        else:
            self.__settingsCache.onSyncCompleted += self.__onSettingsReady

    def __isHintAvailable(self, hintId):
        if hintId not in self.__hintsData:
            _logger.error('Hint ID not found: "%s"', hintId)
            return False
        return True

    def __onSettingsReady(self):
        self.__settingsCache.onSyncCompleted -= self.__onSettingsReady
        abTestGroup = BigWorld.player().abTestFeatures.get(_AB_TEST_FEATURE_NAME)
        for conf in self.__hintsConfig.values():
            sconf = self.getConfig().hints.get(conf.hintId)
            if sconf is None:
                _logger.error('Can not find in server config hint with id=%s', conf.hintId)
                continue
            conditions = (not sconf['enabled'], abTestGroup is None and not sconf['default'], abTestGroup is not None and abTestGroup not in sconf['ab_test_groups'])
            if any(conditions):
                continue
            hintData = _HintDataProcessor(conf.dataBlock)
            self.__hintsData[conf.hintId] = hintData
            if BattleReplay.g_replayCtrl.isPlaying:
                self.__restoreCounterFromReplay(conf.hintId, hintData)
            else:
                hintData.read()
                if hintData.getWatchingCounter() == 0:
                    continue
            if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
                hintData.setWatchingCounterPerBattle(conf.maxWatchingQtyPerBattle)
                hintData.decrementBattlesCooldown()
                hintData.save()
            if conf.activationTrigger is not None:
                self.__activationTriggers[conf.hintId] = conf.activationTrigger(conf.hintId, self.activateHint)
            _logger.debug('[BATTLE_CONTEXT_INTS] BattleContextHintsController.__onSettingsReady() HintData(hintId=%s) = %s ', conf.hintId, hintData)

        if all((hintData.getWatchingCounter() == 0 for hintData in self.__hintsData.values())):
            return
        else:
            if BattleReplay.g_replayCtrl.isRecording:
                counters = {}
                for hintId, hintData in self.__hintsData.items():
                    counters[hintId] = (hintData.getWatchingCounter(),
                     hintData.getWatchingCounterPerBattle(),
                     hintData.getBattlesCooldown(),
                     hintData.getLastBattleTriggered())

                BattleReplay.g_replayCtrl.serializeCallbackData(BattleReplay.CallbackDataNames.BATTLE_CONTEXT_HINTS_COUNTERS_CALLBACK, (counters,))
            for trigger in self.__activationTriggers.values():
                trigger.start()

            self.__isStarted = True
            return

    def __getComponent(self, injectComponentAlias):
        component = None
        if injectComponentAlias is not None:
            component = findFirst(lambda comp: comp.getAlias() == injectComponentAlias, self._viewComponents)
            if not component:
                _logger.error('Unknown component alias=%s', injectComponentAlias)
        else:
            _logger.error('Unknown alias=%s', injectComponentAlias)
        return component

    def __isCanBeDisplayed(self, hintId):
        hintData = self.__hintsData[hintId]
        _logger.debug('[BATTLE_CONTEXT_INTS] BattleContextHintsController.__isCanBeDisplayed(hintId=%s) hintData=%s', hintId, hintData)
        return hintData.getWatchingCounter() > 0 and hintData.getWatchingCounterPerBattle() != 0 and hintData.getBattlesCooldown() == 0

    def __activateHint(self, hintId, context, logger, isDisplay, force=False, forceDelay=None):
        conf = self.__hintsConfig[hintId]
        _logger.debug('[BATTLE_CONTEXT_INTS] BattleContextHintsController.__activateHint hintId=%s, isDisplay=%s, forceDelay=%s', hintId, isDisplay, forceDelay)
        self.__currentHintLifecycleMgr = None
        if isDisplay:
            component = None
            if conf.injectComponentAlias is not None:
                component = self.__getComponent(conf.injectComponentAlias)
                if component is None:
                    _logger.error('component is None for hintId=%s', hintId)
                    return False
            self.__currentHintLifecycleMgr = None
            if conf.hintLifecycleMgr is not None:
                self.__currentHintLifecycleMgr = conf.hintLifecycleMgr()
                delay = forceDelay if forceDelay is not None else conf.delay
                self.__currentHintLifecycleMgr.start(hintId, conf.soundEvent, context, logger, component, conf.hintView, conf.hintPresenter, delay, conf.duration, self.__onHintFinished)
        applyingTriggerClass = conf.applyingTrigger
        if applyingTriggerClass is None:
            if not force:
                self.__decrementWatchingCounter(hintId, logger)
        else:
            self.__currentApplyingTrigger = applyingTriggerClass(conf.hintId, logger, self.applyHint)
            self.__currentApplyingTrigger.start()
        self.__currentHintId = hintId
        event_dispatcher.activateBattleContextHint()
        if IS_DEVELOPMENT:
            self.__finishHintCheckDelayer.delayCallback(self.MAX_HINT_DURATION, self.__checkFinishHint)
        return True

    def __decrementWatchingCounter(self, hintId, logger):
        _logger.debug('[BATTLE_CONTEXT_INTS] BattleContextHintsController.__decrementWatchingCounter(hintId=%s)', hintId)
        conf = self.__hintsConfig[hintId]
        hintData = self.__hintsData[hintId]
        hintData.decrementWatchingCounter()
        hintData.setBattlesCooldown(conf.battlesCooldown)
        hintData.save()
        logger.logHintApplied()
        if hintData.getWatchingCounter() == 0:
            logger.logHintMaxViewsReached()

    def __onHintFinished(self, hintId):
        self.__finishHint(hintId)

    def __finishHint(self, hintId):
        _logger.debug('[BATTLE_CONTEXT_INTS] BattleContextHintsController.__finishHint(hintId=%s)', hintId)
        if self.__currentHintId is not None:
            if IS_DEVELOPMENT:
                self.__finishHintCheckDelayer.stopCallback(self.__checkFinishHint)
            if self.__currentHintId != hintId:
                _logger.error('self.__currentHintId != hintId: %s!=%s', self.__currentHintId, hintId)
            self.__currentHintId = None
            if self.__currentHintLifecycleMgr is not None:
                self.__currentHintLifecycleMgr.stop()
                self.__currentHintLifecycleMgr = None
            if self.__currentApplyingTrigger is not None:
                self.__currentApplyingTrigger.stop()
                self.__currentApplyingTrigger = None
        return

    def __checkFinishHint(self):
        if self.__currentHintId is not None:
            _logger.warning('__onHintFinished() didnt triggered for hint %s ', self.__currentHintId)
            self.__finishHint(self.__currentHintId)
        return

    def __saveCountersFromReplay(self, counters):
        self.__countersFromReplay = counters

    def __restoreCounterFromReplay(self, hintId, hintData):
        if hintId in self.__countersFromReplay:
            cntrs = self.__countersFromReplay[hintId]
            hintData.setWatchingCounter(cntrs[0])
            hintData.setWatchingCounterPerBattle(cntrs[1])
            hintData.setBattlesCooldown(cntrs[2])
            hintData.setLastBattleTriggered(cntrs[3])
        else:
            hintData.setWatchingCounter(0)
            hintData.setWatchingCounterPerBattle(0)
            hintData.setBattlesCooldown(0)
            hintData.setLastBattleTriggered(False)

    def __isPlayerObserver(self):
        playerVehicleID = BigWorld.player().playerVehicleID
        controllingVehicleID = self.__sessionProvider.shared.vehicleState.getControllingVehicleID()
        return playerVehicleID != controllingVehicleID
