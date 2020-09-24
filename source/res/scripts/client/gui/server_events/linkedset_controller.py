# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/linkedset_controller.py
import BigWorld
from constants import EVENT_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.events import ViewEventType
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.linkedset import ILinkedSetController
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from gui import SystemMessages
from skeletons.gui.lobby_context import ILobbyContext
from gui.server_events.bonuses import getTutorialBonuses
from gui.Scaleform.locale.LINKEDSET import LINKEDSET
from gui.server_events.events_constants import LINKEDSET_GROUP_PREFIX
from AccountCommands import isCodeValid
from debug_utils import LOG_WARNING
from gui.SystemMessages import SM_TYPE
from gui import makeHtmlString
from gui.server_events.events_helpers import getLinkedSetMissionIDFromQuest, getLinkedSetQuestID, hasLocalizedQuestHintNameForLinkedSetQuest, hasLocalizedQuestWinDescForLinkedSetQuest, hasLocalizedQuestWinNameForLinkedSetQuest, getLocalizedQuestWinNameForLinkedSetQuest, getLocalizedQuestWinDescForLinkedSetQuest, getLocalizedQuestDescForLinkedSetQuest, getLocalizedQuestHintNameForLinkedSetQuest, getLocalizedQuestHintDescForLinkedSetQuest
from skeletons.gui.server_events import IEventsCache
from helpers.i18n import makeString as _ms
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.server_events.events_helpers import hasAtLeastOneCompletedQuest, isAllQuestsCompleted
from gui.shared.utils import isPopupsWindowsOpenDisabled
from Event import Event, EventManager
_SNDID_ACHIEVEMENT = 'result_screen_achievements'
_SNDID_BONUS = 'result_screen_bonus'
_HMTL_STRING_FORMAT_PATH = 'html_templates:lobby/quests/linkedSet'
_HMTL_STRING_FORMAT_DESC_KEY = 'awardWindowDescTemplate'
_HMTL_STRING_FORMAT_HINT_DESC_KEY = 'awardWindowHintDescTemplate'

class LinkedSetController(ILinkedSetController):
    battleResults = dependency.descriptor(IBattleResultsService)
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        self.needToShowAward = False
        self._app = None
        self._em = EventManager()
        self.onStateChanged = Event(self._em)
        self._isLinkedSetEnabled = False
        return

    def init(self):
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self._onShowBattleResults, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, self._onBattleResultsPosted, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LinkedSetEvent.VEHICLE_SELECTED, self._onLinkedSetVehicleSelected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MissionsEvent.ON_TAB_CHANGED, self._onMissionsTabEventsSelected, EVENT_BUS_SCOPE.LOBBY)
        self.lobbyContext.onServerSettingsChanged += self._onLobbyServerSettingChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingsChange
        self.eventsCache.onSyncCompleted += self._onSyncCompleted
        self._isLinkedSetEnabled = self._getIsLinkedSetEnabled()

    def fini(self):
        self._em.clear()
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self._onShowBattleResults, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, self._onBattleResultsPosted, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LinkedSetEvent.VEHICLE_SELECTED, self._onLinkedSetVehicleSelected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.MissionsEvent.ON_TAB_CHANGED, self._onMissionsTabEventsSelected, EVENT_BUS_SCOPE.LOBBY)
        self.lobbyContext.onServerSettingsChanged -= self._onLobbyServerSettingChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingsChange
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted
        self._isLinkedSetEnabled = False

    def isLinkedSetEnabled(self):
        return self._isLinkedSetEnabled

    def isLinkedSetFinished(self):
        return isAllQuestsCompleted(self.eventsCache.getLinkedSetQuests().itervalues())

    def hasLinkedSetFinishToken(self):
        return self.eventsCache.hasQuestDelayedRewards(self.getFinalQuest().getID())

    def isFinalQuest(self, quest):
        return quest.getID() == self.getFinalQuest().getID()

    def getFinalQuest(self):
        maxMissionID = self.getMaxMissionID()
        if maxMissionID > -1:
            quests = self.getMissionByID(maxMissionID)
            if quests:
                return quests[len(quests) - 1]
        return None

    def getMaxMissionID(self):
        quests = self.eventsCache.getLinkedSetQuests()
        return max((getLinkedSetMissionIDFromQuest(quest) for quest in quests.itervalues())) if quests else -1

    def getCompletedButNotShowedQuests(self):
        completedQuests = self.getCompletedLinkedSetQuests()
        return [ quest for quest in completedQuests.itervalues() if not self.isBootcampQuest(quest) and not self._isCompletedQuestWasShowed(quest) ]

    def getMissions(self):
        missions = {}
        for quest in self.getLinkedSetQuests().itervalues():
            groupID = quest.getGroupID()
            if groupID.startswith(LINKEDSET_GROUP_PREFIX):
                groupID = groupID[len(LINKEDSET_GROUP_PREFIX):]
                try:
                    groupID = str(int(groupID))
                    if groupID not in missions:
                        missions[groupID] = [quest]
                    else:
                        missions[groupID].append(quest)
                except ValueError:
                    LOG_WARNING('Wrong LinkedSet group id for quest "{}"'.format(quest.getID()))

            LOG_WARNING('LinkedSet quest "{}" without right LinkedSet group'.format(quest.getID()))

        for quests in missions.itervalues():
            quests.sort(key=getLinkedSetQuestID)

        return [ mission[1] for mission in sorted(missions.viewitems(), key=lambda t: int(t[0])) ]

    def getMissionByID(self, missionID):
        for mission in self.getMissions():
            if getLinkedSetMissionIDFromQuest(mission[0]) == missionID:
                return mission

        return None

    def isBootcampQuest(self, quest):
        return getLinkedSetMissionIDFromQuest(quest) == 1

    def getInitialMissionID(self):
        pass

    def getBonusForBootcampMission(self):
        finalBonuses = []
        for bonusType, bonusValue in self.lobbyContext.getServerSettings().getBootcampBonuses().iteritems():
            finalBonuses.extend(getTutorialBonuses(bonusType, bonusValue))

        return finalBonuses

    def getCompletedLinkedSetQuests(self, filterFunc=None):
        filterFunc = filterFunc or (lambda a: True)

        def userFilterFunc(q):
            return filterFunc(q) if self.isFinalQuest(q) and q.isAvailable().isValid else q.isCompleted() and filterFunc(q)

        return self.eventsCache.getLinkedSetQuests(userFilterFunc)

    def getLinkedSetQuests(self, filterFunc=None):
        return self.eventsCache.getLinkedSetQuests(filterFunc)

    def _getIsLinkedSetEnabled(self):
        if self.lobbyContext.getServerSettings().isLinkedSetEnabled():
            hasAvailableOrComletedQuests = any((quest for quest in self.eventsCache.getLinkedSetQuests().itervalues() if quest.isAvailable().isValid or quest.isCompleted()))
            if hasAvailableOrComletedQuests:
                if self.lobbyContext.getServerSettings().isBootcampEnabled():
                    return True
                return hasAtLeastOneCompletedQuest(self.eventsCache.getLinkedSetQuests().itervalues())
        return False

    def _onSyncCompleted(self):
        if self._isLinkedSetViewOnScene():
            self._showNewCompletedQuests()
        self._checkIsLinkedSetStateChanged()

    def _onLobbyServerSettingChanged(self, newServerSettings):
        newServerSettings.onServerSettingsChange += self._onServerSettingsChange
        self._checkIsLinkedSetStateChanged()

    def _onServerSettingsChange(self, diff):
        if any((value in diff for value in ('isLinkedSetEnabled', 'isBootcampEnabled'))):
            self._checkIsLinkedSetStateChanged()

    def _checkIsLinkedSetStateChanged(self):
        currentState = self._getIsLinkedSetEnabled()
        if currentState != self._isLinkedSetEnabled:
            self._isLinkedSetEnabled = currentState
            self.onStateChanged(self.isLinkedSetEnabled())

    def _isLinkedSetViewOnScene(self):
        app = self.appLoader.getApp()
        if app is not None and app.containerManager is not None:
            lobbySubContainer = app.containerManager.getContainer(WindowLayer.SUB_VIEW)
            if lobbySubContainer is not None:
                searchCriteria = {POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MISSIONS}
                lobbyMissions = lobbySubContainer.getView(criteria=searchCriteria)
                if lobbyMissions:
                    return lobbyMissions.getCurrentTabAlias() == QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS
        return False

    def _onShowBattleResults(self, event):
        if event.alias == VIEW_ALIAS.BATTLE_RESULTS:
            self.needToShowAward = True

    def _onBattleResultsPosted(self, event):
        if self.needToShowAward:
            arenaUniqueID = None
            if isinstance(event.ctx, dict):
                arenaUniqueID = event.ctx.get('arenaUniqueID', None)
            if arenaUniqueID and self.battleResults.areResultsPosted(arenaUniqueID):
                resultsVO = self.battleResults.getResultsVO(arenaUniqueID)
                affectedQuestIDs = [ quest['questInfo']['questID'] for quest in resultsVO.get('quests', []) ]
                isSutable = lambda q: q.getID() in affectedQuestIDs and not self._isCompletedQuestWasShowed(q)
                completedQuests = self.getCompletedLinkedSetQuests(isSutable)
                if completedQuests:
                    self._showAwardsFor(completedQuests.values())
            self.needToShowAward = False
        return

    def _isCompletedQuestWasShowed(self, quest):
        return self.settingsCore.serverSettings.isLinkedSetQuestWasShowed(getLinkedSetQuestID(quest), getLinkedSetMissionIDFromQuest(quest))

    def _onLinkedSetVehicleSelected(self, event):
        vehicleCD = event.ctx.get('vehicleCD')
        vehicleShortUserName = event.ctx.get('shortUserName')

        def _callback(code, errStr):
            if isCodeValid(code):
                message = {'icon': 'award',
                 'title': LINKEDSET.LINKEDSET_FINISHED_TITTLE,
                 'description': makeHtmlString('html_templates:lobby/quests/linkedSet', 'awardWindowDescTemplate', {'msg': _ms(LINKEDSET.LINKEDSET_FINISHED_DESC, tank_name=vehicleShortUserName)}),
                 'buttonLabel': _ms(LINKEDSET.CONTINUE),
                 'back': 'red',
                 'soundID': _SNDID_ACHIEVEMENT}
                g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LINKEDSET_HINTS), ctx={'messages': [message]}), scope=EVENT_BUS_SCOPE.LOBBY)
                message = _ms('#system_messages:%s' % 'vehicle_buy/success', vehName=vehicleShortUserName, price=0)
                SystemMessages.pushI18nMessage(message, type=SM_TYPE.Information)
            else:
                LOG_WARNING('Error occurred while trying to set LinkedSet reward', code, errStr)

        finalQuest = self.getFinalQuest()
        questID = finalQuest.getID() if finalQuest else ''
        BigWorld.player().chooseQuestReward(EVENT_TYPE.TOKEN_QUEST, questID, str(vehicleCD), _callback)

    def _onMissionsTabEventsSelected(self, event):
        if event.ctx == QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS:
            self._showNewCompletedQuests()

    def _showNewCompletedQuests(self):
        newCompletedQuests = self.getCompletedButNotShowedQuests()
        if newCompletedQuests:
            self._showAwardsFor(newCompletedQuests)

    def _showAwardsFor(self, quests):
        if isPopupsWindowsOpenDisabled():
            return
        if quests:
            quests.sort(key=lambda q: (getLinkedSetMissionIDFromQuest(q), getLinkedSetQuestID(q)))
            messages = []
            for quest in quests:
                winMessage = self._getQuestWinMessage(quest)
                if self.isFinalQuest(quest):
                    messages.append(self._getLinkedSetWinMessage())
                    self._appendMessageWithViewCallback(messages, winMessage, quest, True)
                hasHint = hasLocalizedQuestHintNameForLinkedSetQuest(quest)
                self._appendMessageWithViewCallback(messages, winMessage, quest, not hasHint)
                if hasHint:
                    self._appendMessageWithViewCallback(messages, self._getQuestHintMessage(quest), quest, True)

            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LINKEDSET_HINTS), ctx={'messages': messages}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _appendMessageWithViewCallback(self, messages, message, quest, needQuestViewCallback):
        if needQuestViewCallback:

            def viewCallback():
                self.settingsCore.serverSettings.setLinkedSetQuestWasShowed(getLinkedSetQuestID(quest), getLinkedSetMissionIDFromQuest(quest))

            message['callback'] = viewCallback
        messages.append(message)

    def _getLinkedSetWinMessage(self):
        return {'icon': 'final',
         'title': _ms(LINKEDSET.LINKEDSET_COMPLETED_TITLE),
         'description': makeHtmlString(_HMTL_STRING_FORMAT_PATH, _HMTL_STRING_FORMAT_DESC_KEY, {'msg': _ms(LINKEDSET.LINKEDSET_COMPLETED_DESC)}),
         'buttonLabel': _ms(LINKEDSET.CONTINUE),
         'back': 'red',
         'soundID': _SNDID_BONUS}

    def _getQuestWinMessage(self, quest):
        if hasLocalizedQuestWinNameForLinkedSetQuest(quest):
            title = getLocalizedQuestWinNameForLinkedSetQuest(quest)
        else:
            title = _ms(LINKEDSET.QUEST_COMPLETED)
        if hasLocalizedQuestWinDescForLinkedSetQuest(quest):
            desc = getLocalizedQuestWinDescForLinkedSetQuest(quest)
        else:
            desc = getLocalizedQuestDescForLinkedSetQuest(quest)
        return {'icon': 'finalHint' if self.isFinalQuest(quest) else 'finalSuccess',
         'title': title,
         'description': makeHtmlString(_HMTL_STRING_FORMAT_PATH, _HMTL_STRING_FORMAT_DESC_KEY, {'msg': desc}),
         'buttonLabel': _ms(LINKEDSET.CONTINUE),
         'back': 'red',
         'bonuses': quest.getBonuses(),
         'soundID': _SNDID_ACHIEVEMENT}

    def _getQuestHintMessage(self, quest):
        return {'icon': 'num{}{}'.format(getLinkedSetMissionIDFromQuest(quest), getLinkedSetQuestID(quest)),
         'title': getLocalizedQuestHintNameForLinkedSetQuest(quest),
         'description': makeHtmlString(_HMTL_STRING_FORMAT_PATH, _HMTL_STRING_FORMAT_HINT_DESC_KEY, {'msg': getLocalizedQuestHintDescForLinkedSetQuest(quest)}),
         'buttonLabel': _ms(LINKEDSET.CONTINUE),
         'back': 'blue',
         'soundID': _SNDID_BONUS}
