# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_progression_controller.py
import Event
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.game_control.epic_meta_game_ctrl import FRONTLINE_SCREENS
from gui.game_control.links import URLMacros
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
EVENT_PROGRESSION_SETTINGS_KEY = 'event_progression_config'

def _showBrowserView(url):
    from gui.Scaleform.daapi.view.lobby.event_progression.web_handlers import createEventProgressionWebHandlers
    webHandlers = createEventProgressionWebHandlers()
    g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BROWSER_VIEW, ctx={'url': url,
     'webHandlers': webHandlers,
     'returnAlias': VIEW_ALIAS.LOBBY_HANGAR}), EVENT_BUS_SCOPE.LOBBY)


class EventProgressionController(IEventProgressionController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    onUpdated = Event.Event()

    def __init__(self):
        self.__urlMacros = URLMacros()
        self.__isEnabled = False
        self.__url = ''
        self.__actualRewardPoints = 0
        self.__seasonRewardPoints = 0
        self.__maxRewardPoints = 0
        self.__rewardPointsTokenID = ''
        self.__seasonPointsTokenID = ''
        self.__rewardVehicles = []
        self.__questIDs = []

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def url(self):
        return self.__url

    @property
    def actualRewardPoints(self):
        return self.__actualRewardPoints

    @property
    def seasonRewardPoints(self):
        dossier = self.__itemsCache.items.getAccountDossier()
        achievements = dossier.getDossierDescr().expand('epicSeasons')
        seasonRewardPoints = self.__seasonRewardPoints
        for seasonID, episodeID in achievements:
            key = (seasonID, episodeID)
            _, _, awardPoints, _ = achievements[key]
            seasonRewardPoints += awardPoints

        return seasonRewardPoints

    @property
    def maxRewardPoints(self):
        return self.__maxRewardPoints

    @property
    def rewardPointsTokenID(self):
        return self.__rewardPointsTokenID

    @property
    def rewardVehicles(self):
        return self.__rewardVehicles

    @property
    def questIDs(self):
        return self.__questIDs

    def getRewardVehiclePrice(self, vehicleCD):
        return {intCD:price for intCD, price in self.__rewardVehicles}.get(vehicleCD, 0)

    @process
    def openURL(self, url=None):
        requestUrl = url or self.__url
        if requestUrl:
            parsedUrl = yield self.__urlMacros.parse(requestUrl)
            if parsedUrl:
                _showBrowserView(parsedUrl)

    def showCustomScreen(self, screen):
        if self.__url and screen in FRONTLINE_SCREENS.ALL():
            self.openURL('/'.join((self.__url.strip('/'), screen.strip('/'))))

    def onLobbyInited(self, ctx):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__itemsCache.onSyncCompleted += self.__updatePlayerData
        self.__updateSettings()
        self.__updatePlayerData()

    def __clear(self):
        self.__itemsCache.onSyncCompleted -= self.__updatePlayerData
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onServerSettingsChange(self, diff):
        if EVENT_PROGRESSION_SETTINGS_KEY in diff:
            self.__updateSettings()
            self.onUpdated(diff)

    def __onSyncCompleted(self, *args, **kwargs):
        self.__updatePlayerData()
        self.onUpdated(args, kwargs)

    def __updateSettings(self):
        s = self.__lobbyContext.getServerSettings().eventProgression
        self.__isEnabled = s.isEnabled
        self.__url = s.url
        self.__maxRewardPoints = s.maxRewardPoints
        self.__rewardPointsTokenID = s.rewardPointsTokenID
        self.__seasonPointsTokenID = s.seasonPointsTokenID
        self.__rewardVehicles = s.rewardVehicles
        self.__questIDs = s.questIDs

    def __updatePlayerData(self, *_):
        t = self.__itemsCache.items.tokens.getTokens()
        self.__actualRewardPoints = t.get(self.__rewardPointsTokenID, (0, 0))[1]
        self.__seasonRewardPoints = t.get(self.__seasonPointsTokenID, (0, 0))[1]
