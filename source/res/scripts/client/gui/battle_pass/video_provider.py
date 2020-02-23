# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_pass/video_provider.py
import logging
import weakref
from adisp import process
from Event import Event, EventManager
from account_helpers.AccountSettings import AccountSettings, BATTLE_PASS_VIDEOS_CONFIG
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from gui.battle_pass.web_controller import BattlePassWebController
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from gui.wgcg.battle_pass.contexts import BattlePassGetVideoDataCtx
from helpers import dependency, time_utils
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class BattlePassVideoProvider(object):
    __slots__ = ('onVideosConfigUpdated', '__videosConfig', '__eventsManager', '__battlePassController', '__isStarted', '__unlockVideoNotifier', '__requestVideoNotifier', '__failedRequestCount', '__webController')
    SIZE_STORAGE = 16
    CALLBACK_REPEAT_TIME = 20
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, battlePassController):
        super(BattlePassVideoProvider, self).__init__()
        self.__battlePassController = weakref.proxy(battlePassController)
        self.__eventsManager = EventManager()
        self.__videosConfig = {}
        self.__unlockVideoNotifier = SimpleNotifier(self.__getTimeToNotifyUnlockVideo, self.__onNotifyUnlockVideo)
        self.__requestVideoNotifier = SimpleNotifier(self.__getTimeToNotifyFailedRequest, self.__onMakeRepeatRequest)
        self.__isStarted = False
        self.__failedRequestCount = 0
        self.__webController = None
        self.onVideosConfigUpdated = Event(self.__eventsManager)
        return

    @property
    def isStarted(self):
        return self.__isStarted

    def start(self):
        self.__webController = BattlePassWebController()
        self.__webController.init()
        self.__webController.invalidate()
        self.__isStarted = True
        self.__requestVideoData()
        self.__battlePassController.onLevelUp += self.__onLevelUp

    def stop(self):
        self.__isStarted = False
        self.__failedRequestCount = 0
        self.__battlePassController.onLevelUp -= self.__onLevelUp
        self.__unlockVideoNotifier.stopNotification()
        self.__requestVideoNotifier.stopNotification()
        if self.__webController is not None:
            self.__webController.fini()
        self.__webController = None
        return

    def getVideosTotal(self):
        return len(self.__videosConfig)

    def getAvailableVideosCount(self):
        return len(self.__getAvailableVideos())

    def hasUnviewedVideo(self):
        return True if self.getAvailableVideosCount() > len(self.getViewedVideos()) else False

    def setShownVideo(self, videoID):
        self.__saveShownVideoInStorage(videoID)
        self.onVideosConfigUpdated()

    def getViewedVideos(self):
        shownVideoFlags = self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.SHOWN_VIDEOS_FLAGS)
        result = []
        for videoID, video in self.__videosConfig.items():
            videoIndex = video.get('idx')
            if shownVideoFlags & 1 << videoIndex:
                result.append(videoID)

        return result

    def __saveShownVideoInStorage(self, videoID):
        offset = self.__getShownFlagOffset(self.__videosConfig, videoID)
        if offset is None:
            _logger.warning('Failed to save shown video')
            return
        else:
            shownVideoFlags = self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.SHOWN_VIDEOS_FLAGS)
            self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.SHOWN_VIDEOS_FLAGS: shownVideoFlags | 1 << offset})
            return

    def __resetShownVideoInStorage(self, videoID):
        offset = self.__getShownFlagOffset(self.__videosConfig, videoID)
        if offset is None:
            _logger.warning('Failed to clear save shown video')
            return
        else:
            shownVideoFlags = self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.SHOWN_VIDEOS_FLAGS)
            if shownVideoFlags:
                self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.SHOWN_VIDEOS_FLAGS: shownVideoFlags & ~(1 << offset)})
            return

    def __getAvailableVideos(self):
        result = []
        for video in self.__videosConfig.values():
            if video.get('is_available'):
                result.append(video)

        return result

    def __getTimeToNotifyUnlockVideo(self):
        if not self.__videosConfig:
            return 0
        serverVideosIDs = self.__getVideoIndexAndIDFromConfig(self.__videosConfig)
        for videoIndex in sorted(serverVideosIDs.keys()):
            video = self.__videosConfig[serverVideosIDs[videoIndex]]
            if not video.get('is_available'):
                publicationTime = video.get('condition', {}).get('publication_start', 0)
                return max(0, publicationTime - time_utils.getServerUTCTime())

    def __updateVideosConfig(self):
        for video in self.__videosConfig.values():
            if not video.get('is_available'):
                publicationTime = video.get('publication_start')
                needLevel = video.get('level')
                needVote = video.get('need_vote')
                if publicationTime > time_utils.getServerUTCTime():
                    continue
                if needLevel > self.__battlePassController.getCurrentLevel():
                    continue
                if needVote and not self.__battlePassController.isPlayerVoted():
                    continue
                self.__requestVideoData()
                break

    def __onLevelUp(self):
        self.__updateVideosConfig()

    def __onNotifyUnlockVideo(self):
        self.__updateVideosConfig()

    def __getTimeToNotifyFailedRequest(self):
        time = self.CALLBACK_REPEAT_TIME * 2 ** self.__failedRequestCount
        self.__failedRequestCount += 1
        return time

    def __onMakeRepeatRequest(self):
        self.__requestVideoData()

    @process
    def __requestVideoData(self):
        if self.__battlePassController.isPlayerVoted():
            voteID = self.__battlePassController.getVoteOption()
            isBought = self.__isVotedWithBoughtBP()
        else:
            voteID = None
            isBought = self.__battlePassController.isBought()
        ctx = BattlePassGetVideoDataCtx(self.__battlePassController.getSeasonID(), self.__battlePassController.getCurrentLevel(), int(isBought), voteID)
        response = yield self.__webController.sendRequest(ctx=ctx)
        if not self.__isStarted:
            return
        else:
            if response.isSuccess():
                self.__videosConfig = ctx.getDataObj(response.getData())
                self.__checkConflicts()
                self.__unlockVideoNotifier.startNotification()
                self.__failedRequestCount = 0
                self.onVideosConfigUpdated()
            else:
                self.__requestVideoNotifier.startNotification()
            return

    def __checkConflicts(self):
        localConfig = AccountSettings.getSettings(BATTLE_PASS_VIDEOS_CONFIG)
        localVideosIDs = self.__getVideoIndexAndIDFromConfig(localConfig)
        serverVideosIDs = self.__getVideoIndexAndIDFromConfig(self.__videosConfig)
        if not localConfig:
            AccountSettings.setSettings(BATTLE_PASS_VIDEOS_CONFIG, self.__videosConfig)
            localVideosIDs = self.__getVideoIndexAndIDFromConfig(self.__videosConfig)
        for videoIdx in serverVideosIDs.keys():
            localVideoID = localVideosIDs.get(videoIdx)
            serverVideoID = serverVideosIDs[videoIdx]
            if localVideoID is None or localVideoID != serverVideoID:
                self.__resetShownVideoInStorage(serverVideoID)
                localConfig.pop(localVideoID, None)
                localConfig[serverVideoID] = self.__videosConfig[serverVideoID]
                AccountSettings.setSettings(BATTLE_PASS_VIDEOS_CONFIG, localConfig)

        return

    def __isVotedWithBoughtBP(self):
        return self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.VOTED_WITH_BOUGHT_BP)

    @staticmethod
    def __getVideoIndexAndIDFromConfig(config):
        return {video.get('idx'):videoID for videoID, video in config.items()}

    @staticmethod
    def __getShownFlagOffset(config, videoID):
        video = config.get(videoID, None)
        if video is None:
            _logger.error('Failed to get video! Check videos config are correct.')
            return
        else:
            return video.get('idx')
