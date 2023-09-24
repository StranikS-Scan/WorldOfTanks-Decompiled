# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/limited_ui/lui_controller.py
import logging
from collections import defaultdict
import enum
import typing
from future.utils import itervalues
from Event import EventManager, Event
from account_helpers import AccountSettings
from constants import Configs
from gui.SystemMessages import SM_TYPE as _SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.limited_ui.lui_rules_storage import RulesStorageMaker
from gui.limited_ui.lui_tokens_storage import getTokensInfo
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.game_control import ILimitedUIController, IBootcampController, IBattleRoyaleController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Tuple, List, Set, Union
    from helpers.server_settings import _LimitedUIConfig
    from gui.limited_ui.lui_rules_storage import _LimitedUIRules, _LimitedUIRule, LuiRules
    from gui.limited_ui.lui_tokens_storage import LimitedUICondition, LimitedUITokenInfo
_logger = logging.getLogger(__name__)

class CallHandlerReason(enum.Enum):
    FEATURE_STATE_CHANGED = 'featureStateChanged'
    SETTINGS_CHANGED = 'settingsChanged'
    COMPLETE_RULE = 'completeRule'
    COMPLETE_CONDITION = 'completeCondition'


_ACC_SETTINGS_SWITCHER_FLAG = 'luiSwitcherState'
_TUTORIAL_HINTS_CLASS_CONDITION = 'LimitedUIHintChecker'
_UI_SPAM_OFF_VERSION = 1

class _LimitedUIConditionsService(object):

    def __init__(self):
        self.__conditions = {}
        self.__activeTokens = set()
        self.onConditionValueUpdated = Event()
        self.__registerConditions(getTokensInfo())

    def destroy(self):
        self.updateActiveTokens(set())
        self.__unregisterConditions()

    def fillContext(self, tokens):
        if not tokens - set(self.__conditions):
            return {token:self.__conditions[token].value() for token in tokens}
        else:
            _logger.error('fillContext: Tokens: %s are not defined.', ', '.join(tokens))
            return None

    def updateActiveTokens(self, tokens):
        inactivateTokens = self.__activeTokens - tokens
        activateTokens = tokens - self.__activeTokens
        for token in inactivateTokens:
            self.__conditions[token].deactivate()

        for token in activateTokens:
            self.__conditions[token].activate()

        self.__activeTokens = tokens

    def __registerConditions(self, refConditionsInfos):
        for tokenInfo in refConditionsInfos:
            if tokenInfo.tokenID not in self.__conditions.keys():
                args = tokenInfo.args if tokenInfo.args else tuple()
                condition = tokenInfo.clazz(tokenInfo.tokenID)
                condition.initialize(*args)
                condition.onConditionValueUpdated += self.__onUpdated
                self.__conditions[tokenInfo.tokenID] = condition

    def __unregisterConditions(self):
        for condition in itervalues(self.__conditions):
            condition.onConditionValueUpdated -= self.__onUpdated
            condition.finalize()

        self.__conditions.clear()

    def __onUpdated(self, tokenID):
        self.onConditionValueUpdated(tokenID)


class LimitedUIController(ILimitedUIController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCache = dependency.descriptor(ISettingsCache)
    _SERVER_SETTINGS_BLOCK_BITS = 32

    def __init__(self):
        super(LimitedUIController, self).__init__()
        self.__luiConfig = None
        self.__luiService = None
        self.__rules = None
        self.__observers = defaultdict(list)
        self.__skippedObserves = defaultdict(list)
        self.__postponedCompleteRules = None
        self.__serverSettings = None
        self.__isEnabled = False
        self.__em = EventManager()
        self.onStateChanged = Event(self.__em)
        self.onConfigChanged = Event(self.__em)
        self.onVersionUpdated = Event(self.__em)
        return

    def fini(self):
        self.__em.clear()
        super(LimitedUIController, self).fini()

    def onDisconnected(self):
        self.__clear()

    def onAccountBecomePlayer(self):
        super(LimitedUIController, self).onAccountBecomePlayer()
        if self.__bootcampController.isInBootcamp():
            return
        self.__initialize()

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isInited(self):
        return self.__luiConfig is not None

    @property
    def configVersion(self):
        return self.__luiConfig.version if self.__luiConfig else 0

    @property
    def version(self):
        return self.__itemsCache.items.stats.luiVersion

    @property
    def isOnlyUISpamOff(self):
        return self.version == _UI_SPAM_OFF_VERSION

    @property
    def isUserSettingsMayShow(self):
        return self.isEnabled and not self.isOnlyUISpamOff and not self.isFullCompleted

    @property
    def isFullCompleted(self):
        return all((self.__isRuleCompleted(ruleID) or self.__checkCondition(ruleID) for ruleID in self.__rules.getRulesIDs()))

    def isRuleCompleted(self, ruleID):
        return not self.isEnabled or self.__checkRule(ruleID)

    def completeRule(self, ruleID):
        if not self.__isRuleCompleted(ruleID):
            self.__completeRule(ruleID)
            for handler in self.__observers[ruleID]:
                handler(ruleID, CallHandlerReason.COMPLETE_RULE)

    def completeAllRules(self):
        count = len(self.__rules.getRulesIDs())
        lastStorageOffset = count % self._SERVER_SETTINGS_BLOCK_BITS
        self.__settingsCore.serverSettings.setLimitedUIFullComplete(lastStorageOffset)
        for ruleID, handlers in self.__observers.items():
            for handler in handlers:
                handler(ruleID, CallHandlerReason.COMPLETE_RULE)

    def startObserve(self, ruleID, handler):
        if self.isRuleCompleted(ruleID):
            if handler not in self.__skippedObserves[ruleID]:
                self.__skippedObserves[ruleID].append(handler)
            return
        if handler not in self.__observers[ruleID]:
            self.__observers[ruleID].append(handler)
            self.__updateActiveRules()

    def stopObserve(self, ruleID, handler):
        if handler in self.__skippedObserves[ruleID]:
            self.__skippedObserves[ruleID].remove(handler)
        if handler in self.__observers[ruleID]:
            self.__observers[ruleID].remove(handler)
            self.__updateActiveRules()

    def __initialize(self):
        if self.isInited:
            return
        self.__postponedCompleteRules = set()
        self.__luiService = _LimitedUIConditionsService()
        self.__subscribe()

    def __clear(self):
        if not self.isInited:
            return
        else:
            self.__unsubscribe()
            self.__clearObservers(self.__observers)
            self.__clearObservers(self.__skippedObserves)
            if self.__rules:
                self.__rules.clear()
                self.__rules = None
            self.__luiService.destroy()
            self.__luiService = None
            self.__isEnabled = False
            self.__serverSettings = None
            self.__postponedCompleteRules = None
            self.__luiConfig = None
            return

    def __subscribe(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__luiService.onConditionValueUpdated += self.__onConditionUpdated
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__settingsCache.onSyncCompleted += self.__onSettingsCacheSyncCompleted

    def __unsubscribe(self):
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__luiService.onConditionValueUpdated -= self.__onConditionUpdated
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__settingsCache.onSyncCompleted -= self.__onSettingsCacheSyncCompleted
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateLimitedUISettings
        return

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateLimitedUISettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onUpdateLimitedUISettings
        self.__updateConfig()
        return

    def __onSyncCompleted(self, _, diff):
        if not diff or 'limitedUi' in diff:
            self.__tryNotifyStateChanged()
            self.onVersionUpdated()

    def __onSettingsCacheSyncCompleted(self):
        self.__storePostponed()

    def __updateStatus(self):
        isEnableState = self.__luiConfig.enabled and self.__luiConfig.hasRules() and not self.__bootcampController.isInBootcamp()
        changeState = self.__isEnabled != isEnableState
        if changeState:
            self.__isEnabled = isEnableState
            self.__updateObservers()
            self.onStateChanged()
            self.__updateTutorialHints(state=not self.__isEnabled)
        self.__updateActiveRules()
        return changeState

    def __updateTutorialHints(self, state, targetID=_TUTORIAL_HINTS_CLASS_CONDITION, arguments=''):
        g_eventBus.handleEvent(events.TutorialEvent(events.TutorialEvent.UPDATE_TUTORIAL_HINTS, targetID=targetID, state=state, arguments=arguments), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __onUpdateLimitedUISettings(self, diff):
        if Configs.LIMITED_UI_CONFIG.value in diff:
            self.__updateConfig()

    def __updateConfig(self):
        self.__luiConfig = self.__serverSettings.limitedUIConfig
        self.__buildRules()
        if not self.__updateStatus():
            self.__notifyObservers(CallHandlerReason.SETTINGS_CHANGED)
        self.__tryNotifyStateChanged()
        self.onConfigChanged()

    def __buildRules(self):
        if self.__rules:
            self.__rules.clear()
        self.__rules = RulesStorageMaker.makeStorage(self.__luiConfig.rules)

    def __updateObservers(self):
        if self.isEnabled:
            self.__restoreSkippedObservers()
        else:
            self.__storeSkippedObservers()

    def __updateActiveRules(self):
        activeRulesIDs = set((ruleID for ruleID in self.__observers if self.__observers[ruleID]))
        activeTokens = set().union(*(self.__rules.getTokens(ruleID) for ruleID in activeRulesIDs))
        self.__luiService.updateActiveTokens(activeTokens)

    def __onConditionUpdated(self, tokenID):
        notifyRules = [ ruleID for ruleID in self.__observers if tokenID in self.__rules.getTokens(ruleID) ]
        for ruleID in notifyRules:
            if not self.__isRuleCompleted(ruleID) and self.__checkRule(ruleID):
                for handler in self.__observers[ruleID]:
                    handler(ruleID, CallHandlerReason.COMPLETE_CONDITION)

    def __storeSkippedObservers(self):
        for ruleID, handlers in self.__observers.items():
            for handler in handlers:
                handler(ruleID, CallHandlerReason.FEATURE_STATE_CHANGED)

            self.__skippedObserves[ruleID].extend(handlers)

        self.__clearObservers(self.__observers)

    def __restoreSkippedObservers(self):
        for ruleID, handlers in self.__skippedObserves.items():
            for handler in handlers:
                handler(ruleID, CallHandlerReason.FEATURE_STATE_CHANGED)

            if handlers and not self.isRuleCompleted(ruleID):
                self.__observers[ruleID].extend(handlers)
                del self.__skippedObserves[ruleID][:]

    def __notifyObservers(self, reason):
        for ruleID, handlers in self.__observers.items():
            if handlers and not self.__isRuleCompleted(ruleID) and self.__checkRule(ruleID):
                for handler in handlers:
                    handler(ruleID, reason)

    @staticmethod
    def __clearObservers(observers):
        for ruleID in observers:
            del observers[ruleID][:]

        observers.clear()

    def __checkRule(self, ruleID):
        if not self.__rules or not self.__rules.hasRule(ruleID) or self.__isRuleCompleted(ruleID):
            return True
        isComplete = self.__checkCondition(ruleID)
        if isComplete:
            self.__completeRule(ruleID)
            if self.__readSettings(ruleID):
                self.__updateTutorialHints(state=self.__isEnabled, arguments=ruleID.value)
        return isComplete

    def __checkCondition(self, ruleID):
        rule = self.__rules.getRule(ruleID)
        ctx = self.__luiService.fillContext(rule.tokens)
        return rule.expression(ctx) if ctx else False

    def __isRuleCompleted(self, ruleID):
        return self.__readSettings(ruleID)

    def __completeRule(self, ruleID):
        if not self.__storeSettings(ruleID):
            self.__postponedCompleteRules.add(ruleID)
            return
        self.__sendSysMessage(ruleID)

    def __getServerSettingsID(self, ruleID):
        rule = self.__rules.getRule(ruleID)
        if rule is None:
            return (None, None)
        else:
            index = rule.idx
            storageIdx = index / self._SERVER_SETTINGS_BLOCK_BITS
            offset = index % self._SERVER_SETTINGS_BLOCK_BITS
            return (storageIdx, offset)

    def __readSettings(self, ruleID):
        storage, offset = self.__getServerSettingsID(ruleID)
        return True if storage is None else bool(self.__settingsCore.serverSettings.getLimitedUIProgress(storage, offset))

    def __storeSettings(self, ruleID):
        storage, offset = self.__getServerSettingsID(ruleID)
        return False if storage is None else self.__settingsCore.serverSettings.setLimitedUIProgress(storage, offset)

    def __storePostponed(self):
        settings = defaultdict(list)
        for ruleID in self.__postponedCompleteRules:
            storage, offset = self.__getServerSettingsID(ruleID)
            if storage is None:
                continue
            settings[storage].append(offset)

        if settings and self.__settingsCore.serverSettings.setLimitedUIGroupProgress(settings):
            for ruleID in self.__postponedCompleteRules:
                self.__sendSysMessage(ruleID)

            self.__postponedCompleteRules.clear()
        return

    def __sendSysMessage(self, ruleID):
        sysMessageTemplate = self.__rules.getSysMessage(ruleID)
        if sysMessageTemplate:
            auxData = [sysMessageTemplate,
             NotificationPriorityLevel.MEDIUM,
             None,
             None]
            self.__systemMessages.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE, auxData=auxData)
        return

    def __tryNotifyStateChanged(self):
        if self.__bootcampController.isInBootcamp() or self.version <= 0 or self.isOnlyUISpamOff or not self.__luiConfig.hasRules() or self.isFullCompleted:
            return
        else:
            isLuiConfigEnabled = self.__luiConfig.enabled
            luiSwitcherState = AccountSettings.getUIFlag(_ACC_SETTINGS_SWITCHER_FLAG)
            if luiSwitcherState is None:
                AccountSettings.setUIFlag(_ACC_SETTINGS_SWITCHER_FLAG, isLuiConfigEnabled)
                return
            if luiSwitcherState != isLuiConfigEnabled:
                AccountSettings.setUIFlag(_ACC_SETTINGS_SWITCHER_FLAG, isLuiConfigEnabled)
                self.__changeSwitcherNotifier(isLuiConfigEnabled)
            return

    def __changeSwitcherNotifier(self, isOn):
        if isOn:
            textID = R.strings.system_messages.limitedUI.switchOn()
            msgType = _SM_TYPE.Warning
        else:
            textID = R.strings.system_messages.limitedUI.switchOff()
            msgType = _SM_TYPE.ErrorSimple
        self.__systemMessages.pushMessage(backport.text(textID), msgType)
