# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/limited_ui/lui_controller.py
import logging
from collections import defaultdict
import enum
import typing
from future.utils import itervalues
from Event import EventManager, Event
from ab_feature_test_token_based_shared import getFeatures
from account_helpers import AccountSettings
from constants import Configs
from gui import GUI_SETTINGS
from gui.clans.clan_helpers import isStrongholdsEnabled
from gui.SystemMessages import SM_TYPE as _SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.limited_ui.lui_rules_storage import RulesStorageMaker, LuiRules
from gui.limited_ui.lui_tokens_storage import getTokensInfo
from gui.limited_ui.lui_representations_storage import getRepresentations
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.notifications import NotificationPriorityLevel
from gui.tournament.tournament_helpers import isTournamentEnabled
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.game_control import ILimitedUIController, IBootcampController, IBattleRoyaleController, IVersusAIController, IComp7Controller, IFunRandomController, IEpicBattleMetaGameController, IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from constants import PREBATTLE_TYPE
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Optional, Tuple, List, Set, Union
    from helpers.server_settings import _LimitedUIConfig
    from gui.limited_ui.lui_rules_storage import _LimitedUIRules, _LimitedUIRule
    from gui.limited_ui.lui_tokens_storage import LimitedUICondition, LimitedUITokenInfo
    from gui.limited_ui.lui_representations_storage import LimitedUIConditionRepresentation
_logger = logging.getLogger(__name__)

class CallHandlerReason(enum.Enum):
    FEATURE_STATE_CHANGED = 'featureStateChanged'
    SETTINGS_CHANGED = 'settingsChanged'
    COMPLETE_RULE = 'completeRule'
    COMPLETE_CONDITION = 'completeCondition'
    CONDITION_REPRESENTATION_CHANGED = 'conditionRepresentationChanged'


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


class _LimitedUIConditionsRepresentationService(object):

    def __init__(self):
        self.__representationsDict = {}
        self.__conditionRepresentations = {}
        self.onConditionRepresentationChanged = Event()
        self.__fillRepresentationsDict(getRepresentations())

    def destroy(self):
        self.__representationsDict.clear()
        self.__conditionRepresentations.clear()

    def updateConditionRepresentations(self, rules):
        self.__conditionRepresentations.clear()
        for ruleID in rules.getRulesIDs():
            if ruleID not in self.__conditionRepresentations.keys():
                self.__conditionRepresentations[ruleID] = self.__makeRepresentation(rules.getExpressionElements(ruleID))
                self.onConditionRepresentationChanged(ruleID)

    def getConditionRepresentation(self, ruleID):
        return self.__conditionRepresentations.get(ruleID, [])

    def __fillRepresentationsDict(self, refRepresentations):
        for representation in refRepresentations:
            self.__representationsDict.setdefault(representation.condition, representation)

    def __makeRepresentation(self, expressionElements):
        conditionGroups = []
        currentConditions = []
        currentConditionText = ''
        for element in expressionElements:
            if not currentConditionText:
                if element == 'or':
                    if currentConditions:
                        conditionGroups.append(currentConditions)
                        currentConditions = []
                    continue
                elif element == 'and':
                    continue
            currentConditionText += element
            representation = self.__representationsDict.get(currentConditionText)
            if representation:
                currentConditions.append(representation)
                currentConditionText = ''

        if currentConditions:
            conditionGroups.append(currentConditions)
        return conditionGroups


class LimitedUIController(ILimitedUIController, CallbackDelayer):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    __bootcampController = dependency.descriptor(IBootcampController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCache = dependency.descriptor(ISettingsCache)
    __versusAIController = dependency.descriptor(IVersusAIController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __funRandomController = dependency.descriptor(IFunRandomController)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __epicBattleController = dependency.descriptor(IEpicBattleMetaGameController)
    _SEND_CONTENT_UNLOCKED_MESSAGE_TIMEOUT = 3
    _AB_TEST_TOKEN_FEATURE = 'limited_ui'
    _AB_TEST_TOKEN_DISABLE_ACTION = 'disabled'
    _PREBATTLE_TYPE_TO_LUI_RULE_MAP = {PREBATTLE_TYPE.RANKED: LuiRules.RANKED_CONTENT,
     PREBATTLE_TYPE.COMP7: LuiRules.COMP7_CONTENT,
     PREBATTLE_TYPE.EPIC: LuiRules.FRONTLINE_CONTENT,
     PREBATTLE_TYPE.VERSUS_AI: LuiRules.VERSUS_AI_CONTENT}

    def __init__(self):
        super(LimitedUIController, self).__init__()
        self.__luiConfig = None
        self.__luiService = None
        self.__luiRepresentationService = None
        self.__rules = None
        self.__observers = defaultdict(list)
        self.__skippedObserves = defaultdict(list)
        self.__postponedCompleteRules = None
        self.__serverSettings = None
        self.__isEnabled = False
        self.__postponedContentUnlockedMessageRules = None
        self.__sendContentUnlockedMessageDelayer = CallbackDelayer()
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
    def version(self):
        return self.__itemsCache.items.stats.luiVersion

    @property
    def isOnlyUISpamOff(self):
        return self.version == _UI_SPAM_OFF_VERSION

    @property
    def isUserSettingsMayShow(self):
        return False

    @property
    def isFullCompleted(self):
        return all((self.__isRuleCompleted(ruleID) or self.__checkCondition(ruleID) for ruleID in self.__rules.getRulesIDs()))

    def getRuleConditionRepresentation(self, ruleID):
        return self.__luiRepresentationService.getConditionRepresentation(ruleID)

    def isRuleCompleted(self, ruleID):
        return not self.isEnabled or self.__checkRule(ruleID)

    def __getRuleByBattleType(self, prbType):
        if prbType == PREBATTLE_TYPE.FUN_RANDOM and self.__funRandomController.isArcade():
            return LuiRules.ARCADE_CONTENT
        return LuiRules.FIELD_TRIALS_CONTENT if prbType == PREBATTLE_TYPE.FUN_RANDOM and self.__funRandomController.isFieldTrials() else self._PREBATTLE_TYPE_TO_LUI_RULE_MAP.get(prbType)

    def isRuleCompletedByPrebattleType(self, prbType):
        rule = self.__getRuleByBattleType(prbType)
        return True if not rule else self.isRuleCompleted(rule)

    def completeRule(self, ruleID):
        if not self.__isRuleCompleted(ruleID):
            self.__completeRules([ruleID])
            for handler in self.__observers[ruleID]:
                handler(ruleID, CallHandlerReason.COMPLETE_RULE)

    def completeAllRules(self):
        self.__completeRules(self.__rules.getRulesIDs())
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
        self.__postponedContentUnlockedMessageRules = set()
        self.__luiService = _LimitedUIConditionsService()
        self.__luiRepresentationService = _LimitedUIConditionsRepresentationService()
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
            self.__luiRepresentationService.destroy()
            self.__luiRepresentationService = None
            self.__isEnabled = False
            self.__serverSettings = None
            self.__postponedCompleteRules = None
            self.__sendContentUnlockedMessageDelayer.destroy()
            self.__postponedContentUnlockedMessageRules = None
            self.__luiConfig = None
            return

    def __subscribe(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__luiService.onConditionValueUpdated += self.__onConditionUpdated
        self.__luiRepresentationService.onConditionRepresentationChanged += self.__onConditionRepresentationUpdated
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__settingsCache.onSyncCompleted += self.__onSettingsCacheSyncCompleted

    def __unsubscribe(self):
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__luiService.onConditionValueUpdated -= self.__onConditionUpdated
        self.__luiRepresentationService.onConditionRepresentationChanged -= self.__onConditionRepresentationUpdated
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
            self.__updateStatus()

    def __onSettingsCacheSyncCompleted(self):
        self.__storePostponed()

    def __isEnabledByAbTest(self):
        tokenNames = self.__itemsCache.items.tokens.getTokens().keys()
        abTestFeatures = getFeatures(tokenNames)
        return abTestFeatures.get(self._AB_TEST_TOKEN_FEATURE, '') != self._AB_TEST_TOKEN_DISABLE_ACTION

    def __updateStatus(self):
        isEnableState = self.__luiConfig.enabled and self.__luiConfig.hasRules() and not self.__bootcampController.isInBootcamp() and self.__isEnabledByAbTest()
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
        self.__updateConditionsRepresentations()
        if not self.__updateStatus():
            self.__notifyObservers(CallHandlerReason.SETTINGS_CHANGED)
        self.__tryNotifyStateChanged()
        self.onConfigChanged()

    def __buildRules(self):
        if self.__rules:
            self.__rules.clear()
        self.__rules = RulesStorageMaker.makeStorage(self.__luiConfig.rules)

    def __updateConditionsRepresentations(self):
        self.__luiRepresentationService.updateConditionRepresentations(self.__rules)

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
            if self.__isRuleFirstlyCompleted(ruleID):
                for handler in self.__observers[ruleID]:
                    handler(ruleID, CallHandlerReason.COMPLETE_CONDITION)

    def __onConditionRepresentationUpdated(self, ruleID):
        if ruleID not in self.__observers:
            return
        for handler in self.__observers[ruleID]:
            handler(ruleID, CallHandlerReason.CONDITION_REPRESENTATION_CHANGED)

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
            self.__completeRules([ruleID])
            if self.__isRuleCompleted(ruleID):
                self.__updateTutorialHints(state=self.__isEnabled, arguments=ruleID.value)
        return isComplete

    def __checkCondition(self, ruleID):
        rule = self.__rules.getRule(ruleID)
        ctx = self.__luiService.fillContext(rule.tokens)
        return rule.expression(ctx) if ctx else False

    def __isRuleCompleted(self, ruleID):
        return ruleID in self.__postponedCompleteRules or self.__readSettings(ruleID)

    def __isRuleFirstlyCompleted(self, ruleID):
        return not self.__isRuleCompleted(ruleID) and self.__checkRule(ruleID)

    def __completeRules(self, ruleIDs):
        self.__postponedCompleteRules.update(ruleIDs)
        self.delayCallback(0, self.__storePostponed)

    def __readSettings(self, ruleID):
        return self.__settingsCore.serverSettings.getLimitedUIProgress(ruleID, default=False)

    def __storePostponed(self):
        if self.__postponedCompleteRules and self.__settingsCore.serverSettings.setLimitedUIProgress(self.__postponedCompleteRules):
            for ruleID in self.__postponedCompleteRules:
                self.__sendSysMessage(ruleID)

            self.__postponedCompleteRules.clear()

    def __sendSysMessage(self, ruleID):
        sysMessageTemplate = self.__rules.getSysMessage(ruleID)
        if sysMessageTemplate:
            auxData = [sysMessageTemplate,
             NotificationPriorityLevel.MEDIUM,
             None,
             None]
            self.__systemMessages.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.SYS_MSG_TYPE, auxData=auxData)
        if self.__needToSendContentUnlockedMessage(ruleID):
            self.__postponedContentUnlockedMessageRules.add(ruleID)
            if not self.__sendContentUnlockedMessageDelayer.hasDelayedCallback(self.__sendContentUnlockedMessage):
                self.__sendContentUnlockedMessageDelayer.delayCallback(self._SEND_CONTENT_UNLOCKED_MESSAGE_TIMEOUT, self.__sendContentUnlockedMessage)
        return

    def __tryNotifyStateChanged(self):
        if self.__bootcampController.isInBootcamp() or self.version <= 0 or self.isOnlyUISpamOff or not self.__luiConfig.hasRules():
            return
        else:
            isLuiConfigEnabled = self.__luiConfig.enabled
            luiSwitcherState = AccountSettings.getUIFlag(_ACC_SETTINGS_SWITCHER_FLAG)
            if luiSwitcherState is None:
                AccountSettings.setUIFlag(_ACC_SETTINGS_SWITCHER_FLAG, isLuiConfigEnabled)
                return
            if luiSwitcherState != isLuiConfigEnabled:
                AccountSettings.setUIFlag(_ACC_SETTINGS_SWITCHER_FLAG, isLuiConfigEnabled)
                if not self.isFullCompleted:
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

    def __sendContentUnlockedMessage(self):
        if not self.__postponedContentUnlockedMessageRules:
            return
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'rules': self.__postponedContentUnlockedMessageRules}, SCH_CLIENT_MSG_TYPE.LIMITED_UI_CONTENT_UNLOCKED)
        self.__postponedContentUnlockedMessageRules.clear()

    def sendPlatoonLockedMessage(self, prbType, name):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'inviterName': name,
         'prbType': prbType}, SCH_CLIENT_MSG_TYPE.LIMITED_UI_PLATOON_LOCKED)

    def __needToSendContentUnlockedMessage(self, ruleID):
        if ruleID == LuiRules.PERSONAL_MISSIONS_CONTENT:
            return self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled()
        if ruleID == LuiRules.TOURNAMENTS_CONTENT:
            return isTournamentEnabled()
        if ruleID == LuiRules.VERSUS_AI_CONTENT:
            return self.__versusAIController and self.__versusAIController.isEnabled()
        if ruleID == LuiRules.STRONGHOLD_CONTENT:
            return isStrongholdsEnabled()
        if ruleID == LuiRules.SPEC_BATTLE_CONTENT:
            return GUI_SETTINGS.specPrebatlesVisible
        if ruleID == LuiRules.COMP7_CONTENT:
            return self.__comp7Controller and self.__comp7Controller.isEnabled()
        if ruleID == LuiRules.ARCADE_CONTENT:
            return self.__funRandomController and self.__funRandomController.isEnabled() and self.__funRandomController.isArcade()
        if ruleID == LuiRules.FIELD_TRIALS_CONTENT:
            return self.__funRandomController and self.__funRandomController.isEnabled() and self.__funRandomController.isFieldTrials()
        if ruleID == LuiRules.FRONTLINE_CONTENT:
            return self.__epicBattleController and self.__epicBattleController.isEnabled()
        return self.__rankedController and self.__rankedController.isEnabled() if ruleID == LuiRules.RANKED_CONTENT else False
