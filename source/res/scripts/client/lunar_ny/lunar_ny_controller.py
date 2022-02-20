# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_controller.py
import Event
import Settings
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LUNAR_NY_INTRO_VIEWED, IS_LUNAR_NY_INTRO_VIDEO_VIEWED
from adisp import process, async
from gui.game_control.links import URLMacros
from gui.impl.gen import R
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showLunarNYIntroWindow, showVideoViewWithNotificationManager
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.server_settings import LUNAR_NY_EVENT_CONFIG
from helpers.time_utils import getServerUTCTime
from lunar_ny import ILunarNYController
from lunar_ny.sub_controllers.charms import CharmsSubController
from lunar_ny.sub_controllers.gift_system import LunarNYGiftSystemSubController
from lunar_ny.sub_controllers.progression import ProgressionSubController
from lunar_ny.sub_controllers.received_envelopes import ReceivedEnvelopesSubController
from skeletons.gui.lobby_context import ILobbyContext
from lunar_ny.lunar_ny_sounds import LunarNYVideoStartStopHandler, PausedSoundManager

class LunarNYController(ILunarNYController):
    __slots__ = ('__statusChangeNotifier', '__eManager', '__giftSystem', '__receivedEnvelopes', '__charms', '__progression', '__urlMacros', 'onStatusChange')
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(LunarNYController, self).__init__()
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__eManager = Event.EventManager()
        self.onStatusChange = Event.Event(self.__eManager)
        self.__giftSystem = LunarNYGiftSystemSubController(self.__eManager)
        self.__receivedEnvelopes = ReceivedEnvelopesSubController(self.__eManager)
        self.__charms = CharmsSubController()
        self.__progression = ProgressionSubController(self.__eManager)
        self.__videoStartStopHandler = LunarNYVideoStartStopHandler()
        self.__urlMacros = URLMacros()

    def fini(self):
        self.__urlMacros.clear()
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onLobbyInited(self, _):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__statusChangeNotifier.startNotification()
        self.__charms.start()
        self.__receivedEnvelopes.start()
        self.__progression.start()
        self.__giftSystem.start()
        self.onStatusChange()
        if self.isActive():
            self.__openIntroView()

    @property
    def giftSystem(self):
        return self.__giftSystem

    @property
    def receivedEnvelopes(self):
        return self.__receivedEnvelopes

    @property
    def charms(self):
        return self.__charms

    @property
    def progression(self):
        return self.__progression

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def getAboutEnvelopesUrl(self):
        return self.__getConfig().aboutEnvelopesUrl

    def getEventRulesURL(self):
        return self.__getConfig().eventRulesURL

    def getInfoVideoURL(self):
        return self.__getConfig().infoVideoURL

    @async
    @process
    def getEnvelopesExternalShopURL(self, callback=None):
        url = yield self.__urlMacros.parse(self.__getConfig().envelopesExternalShopURL)
        if callback is not None:
            callback(url)
        return

    def getEnvelopePurchasesLimit(self):
        return self.__getConfig().envelopePurchasesLimit

    def getMinRareCharmProbability(self):
        return self.__getConfig().minRareCharmProbability

    def isActive(self):
        if self.isEnabled():
            currentUTCTime = getServerUTCTime()
            eventActiveTime = self.__getConfig().getEventActiveTime()
            return eventActiveTime[0] <= currentUTCTime < eventActiveTime[1]
        return False

    def isGiftSystemEventActive(self):
        return self.isActive() and self.__giftSystem.isGiftEventActive()

    def getEventActiveTime(self):
        return self.__getConfig().getEventActiveTime()

    def __getTimeToStatusChange(self):
        if self.isEnabled():
            startTime, finishTime = self.getEventActiveTime()
            currentTime = getServerUTCTime()
            if startTime >= getServerUTCTime():
                return startTime - currentTime
            if currentTime <= finishTime:
                return finishTime - currentTime

    def __onNotifyStatusChange(self):
        self.onStatusChange()
        if self.isActive():
            self.__openIntroView()

    def __stop(self):
        self.__giftSystem.stop()
        self.__progression.stop()
        self.__receivedEnvelopes.stop()
        self.__charms.stop()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.onStatusChange.clear()
        self.__statusChangeNotifier.stopNotification()

    def __onServerSettingsChange(self, settings):
        if LUNAR_NY_EVENT_CONFIG in settings:
            self.onStatusChange()
            self.__statusChangeNotifier.startNotification()
            if self.isActive():
                self.__openIntroView()

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getLunarNYEventConfig()

    def __openIntroView(self):
        isLunarNYIntroViewed = AccountSettings.getSettings(IS_LUNAR_NY_INTRO_VIEWED)
        isLunarNYIntroVideoViewed = AccountSettings.getSettings(IS_LUNAR_NY_INTRO_VIDEO_VIEWED)
        if not isLunarNYIntroViewed:
            showLunarNYIntroWindow()
        elif not isLunarNYIntroVideoViewed:
            showVideoViewWithNotificationManager(videoResID=R.videos.lunar_ny.red_envelope_event_intro(), onVideoStarted=self.__onIntroLunarNYVideoStarted, onVideoStopped=self.__onIntroLunarNYVideoClosed, onVideoClosed=self.__onIntroLunarNYVideoClosed, isAutoClose=True, soundControl=PausedSoundManager())

    def __onIntroLunarNYVideoStarted(self):
        AccountSettings.setSettings(IS_LUNAR_NY_INTRO_VIDEO_VIEWED, True)
        self.__videoStartStopHandler.onVideoStart()

    def __onIntroLunarNYVideoClosed(self):
        self.__videoStartStopHandler.onVideoDone()
        Settings.g_instance.save()
