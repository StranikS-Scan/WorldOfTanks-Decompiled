# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/prmp_controller.py
import Event
from adisp import process, async
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.SystemMessages import pushI18nMessage
from gui.game_control.links import URLMarcos
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, getClientLanguage
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.account_helpers.settings_core import ISettingsCache, ISettingsCore
from skeletons.gui.game_control import IEncyclopediaController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
_ACTIVATION_TOKEN = 'prmp:encyclopediaEnabled'
_MAX_RECOMMENDATION_ID = 32767
_RECOMMENDATIONS_COUNT = 6

class EncyclopediaController(IEncyclopediaController):
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCache = dependency.descriptor(ISettingsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(EncyclopediaController, self).__init__()
        self.__activated = False
        self.__recommendations = []
        self.__eventManager = Event.EventManager()
        self.__urlMacros = URLMarcos()
        self.__isLobbyStarted = False
        self.__hasNewRecommendations = False
        if GUI_SETTINGS.lookup('encyclopedia'):
            self.__baseUrl = GUI_SETTINGS.encyclopedia['url']
            self.__isSuitableLanguage = getClientLanguage() in GUI_SETTINGS.encyclopedia.get('languages', ())
        else:
            self.__baseUrl = None
            self.__isSuitableLanguage = False
        self.onNewRecommendationReceived = Event.Event(self.__eventManager)
        self.onStateChanged = Event.Event(self.__eventManager)
        self.__isStateSynced = False
        return

    def onAccountBecomePlayer(self):
        self.settingsCache.onSyncCompleted += self.__updateRecommendations

    def onConnected(self):
        if GUI_SETTINGS.lookup('encyclopedia'):
            self.__baseUrl = GUI_SETTINGS.encyclopedia['url']
            self.__isSuitableLanguage = getClientLanguage() in GUI_SETTINGS.encyclopedia.get('languages', ())

    def onLobbyStarted(self, _):
        self.__isLobbyStarted = True
        self.__updateRecommendations()
        self.__updateActivationState()

    def onAvatarBecomePlayer(self):
        self.__isLobbyStarted = False
        self.settingsCache.onSyncCompleted -= self.__updateRecommendations

    def onDisconnected(self):
        self.__isStateSynced = False

    def fini(self):
        self.__eventManager.clear()
        super(EncyclopediaController, self).fini()

    def isActivated(self):
        return self.__activated

    def hasNewRecommendations(self):
        return self.__hasNewRecommendations

    def getRecommendations(self):
        return self.__recommendations

    def addEncyclopediaRecommendation(self, recId):
        if not self.__isLobbyStarted:
            return
        recId = int(recId)
        if 0 <= recId > _MAX_RECOMMENDATION_ID:
            LOG_ERROR('Recommendation ID is out of range', recId)
            return
        if self.__recommendations and self.__recommendations[0] == recId:
            return
        if recId in self.__recommendations:
            self.__recommendations.remove(recId)
        self.__recommendations.insert(0, recId)
        self.__recommendations = self.__recommendations[:_RECOMMENDATIONS_COUNT]
        _setEncyclopediaRecommendationsSections(self.__recommendations, self.settingsCore)
        self.settingsCore.serverSettings.setHasNewEncyclopediaRecommendations()
        self.onNewRecommendationReceived()
        if self.isActivated():
            pushI18nMessage(SYSTEM_MESSAGES.PRMP_NOTIFICATION_NEWENCYCLOPEDIARECOMMENDATION, priority=NotificationPriorityLevel.MEDIUM)

    def moveEncyclopediaRecommendationToEnd(self, recId):
        recId = int(recId)
        if recId in self.__recommendations:
            self.__recommendations.remove(recId)
            self.__recommendations.append(recId)
            _setEncyclopediaRecommendationsSections(self.__recommendations, self.settingsCore)

    def resetHasNew(self):
        self.__hasNewRecommendations = False
        self.settingsCore.serverSettings.setHasNewEncyclopediaRecommendations(False)

    @async
    @process
    def buildUrl(self, callback):
        if self.__baseUrl is None:
            LOG_ERROR('Requesting URL for encyclopedia when base URL is not specified')
            yield lambda clb: clb(False)
        else:
            queryParams = {'id': self.getRecommendations()}
            url = yield self.__urlMacros.parse(self.__baseUrl)
            callback(addParamsToUrlQuery(url, queryParams))
        return

    def __updateRecommendations(self):
        self.__recommendations = _getEncyclopediaRecommendations(self.settingsCore)
        self.__hasNewRecommendations = self.settingsCore.serverSettings.getHasNewEncyclopediaRecommendations()

    def __updateActivationState(self, *_):
        if self.__baseUrl is None or not self.__isSuitableLanguage or self.__isStateSynced:
            return False
        else:
            tokensCount = self.eventsCache.questsProgress.getTokenCount(_ACTIVATION_TOKEN)
            newState = self.lobbyContext.getServerSettings().isEncyclopediaEnabled(tokensCount)
            self.__isStateSynced = True
            if newState != self.__activated:
                self.__activated = newState
                self.onStateChanged()
            return


def _getEncyclopediaRecommendations(settingsCore):
    recsDict = settingsCore.serverSettings.getEncyclopediaRecommendations()
    result = []
    for i in range(1, _RECOMMENDATIONS_COUNT + 1):
        value = recsDict.get('item_%i' % i)
        if value:
            result.append(value)

    return result


def _setEncyclopediaRecommendationsSections(ids, settingsCore):
    dataToSave = _buildServerSettingsSectionsDict(ids + [0] * (_RECOMMENDATIONS_COUNT - len(ids)))
    settingsCore.serverSettings.setEncyclopediaRecommendationsSections(dataToSave)


def _buildServerSettingsSectionsDict(listOfIds):
    return {'item_%i' % (i + 1):v for i, v in enumerate(listOfIds)}
