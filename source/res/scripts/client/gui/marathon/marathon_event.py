# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_event.py
import logging
import typing
from functools import partial
import constants
from constants import MarathonConfig
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MARATHON_REWARD_WAS_SHOWN_PREFIX, MARATHON_VIDEO_WAS_SHOWN_PREFIX
from adisp import async, process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.lobby.marathon.marathon_reward_helper import showMarathonReward
from gui.marathon.marathon_event_container import MarathonEventContainer
from gui.marathon.marathon_resource_manager import MarathonResourceManager
from gui.marathon.marathon_constants import MarathonState, MarathonWarning, ZERO_TIME
from gui.prb_control import prbEntityProperty
from gui.server_events.bonuses import mergeBonuses, VehiclesBonus, getVehicleCrewReward
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from helpers.time_utils import ONE_DAY
from items.writers.c11n_writers import natsorted
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from web.web_client_api.common import ItemPackEntry
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)

class MarathonEvent(object):
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcamp = dependency.descriptor(IBootcampController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, resourceGeneratorClass, dataContainerClass):
        super(MarathonEvent, self).__init__()
        self._data = dataContainerClass()
        self._resource = resourceGeneratorClass(self._data)
        self._remainingPackedRewards = []
        self._remainingRewards = []

    @property
    def prefix(self):
        return self._data.prefix

    @property
    def tabTooltip(self):
        return self._data.tabTooltip

    @property
    def tooltips(self):
        return self._data.tooltips

    @property
    def icons(self):
        return self._data.icons

    @property
    def label(self):
        return self._data.label

    @property
    def backBtnLabel(self):
        return self._data.backBtnLabel

    @property
    def showFlagTooltipBottom(self):
        return self._data.showFlagTooltipBottom

    @property
    def rewardPostfix(self):
        return self._data.rewardPostfix

    @property
    def vehicleID(self):
        return self._data.vehicleID

    @property
    def vehicle(self):
        return self._itemsCache.items.getItemByCD(self.vehicleID)

    @property
    def remainingPackedRewards(self):
        return self._remainingPackedRewards

    @property
    def remainingRewards(self):
        return self._remainingRewards

    @prbEntityProperty
    def prbEntity(self):
        return None

    @property
    def styleID(self):
        return self._data.styleID

    @async
    @process
    def getUrl(self, callback):
        url = yield self._data.urlMacros.parse(self._getUrl())
        callback(url)

    @async
    @process
    def getMarathonVehicleUrl(self, callback):
        url = yield self._data.urlMacros.parse(self._getUrl(urlType=MarathonConfig.REWARD_VEHICLE_URL))
        callback(url)

    @async
    @process
    def getMarathonVehicleUrlIgb(self, callback):
        url = yield self._data.urlMacros.parse(self._getUrl(urlType=MarathonConfig.REWARD_VEHICLE_URL_IGB))
        callback(url)

    @async
    @process
    def getMarathonStyleUrlIgb(self, callback):
        url = yield self._data.urlMacros.parse(self._getUrl(urlType=MarathonConfig.REWARD_STYLE_URL_IGB))
        callback(url)

    def hasIgbLink(self):
        return bool(self._getUrl(urlType=MarathonConfig.REWARD_VEHICLE_URL_IGB))

    def getFinishSaleTime(self):
        return self._lobbyContext.getServerSettings().getMarathonConfig()[MarathonConfig.FINISH_SALE_TIME]

    def getHangarFlag(self):
        return self._resource.getHangarFlag()

    def isEnabled(self):
        return self._data.isEnabled and not self._bootcamp.isInBootcamp()

    def isFlagVisible(self):
        return self._data.isFlagVisible

    def isAvailable(self):
        return self._data.isAvailable

    def getQuestsData(self, prefix=None, postfix=None):
        return self.__getProgress('quests', prefix, postfix)

    def getTokensData(self, prefix=None, postfix=None):
        return self.__getProgress('tokens', prefix, postfix)

    def getMarathonProgress(self):
        tokens = self.getTokensData(prefix=self._data.tokenPrefix, postfix=self._data.completedTokenPostfix)
        tokenPrefixLen = len(self._data.tokenPrefix)
        res = []
        for tokenNames in tokens.keys():
            name = str(tokenNames[tokenPrefixLen:])
            res.append(int(filter(str.isdigit, name)))

        currentStep = sorted(res)[-1] if res else 0
        return (currentStep, self._data.questsInChain)

    def getMarathonPostProgress(self):
        tokens = self.getTokensData(prefix=self._data.tokenPrefix, postfix=self._data.styleTokenPostfix)
        progress = tokens.values()[0][1] if tokens and tokens.values()[0] else 0
        return progress

    def getState(self):
        return self._data.state

    def getTooltipHeader(self):
        return self._resource.getHangarFlagTooltip()

    def getMarathonFlagState(self, vehicle):
        return {'flagHeaderIcon': self.__getHangarFlagHeaderIcon(),
         'flagStateIcon': self.__getHangarFlagStateIcon(vehicle),
         'flagMain': self.getHangarFlag(),
         'tooltip': self.__getTooltip(),
         'enable': self.isAvailable(),
         'visible': self.isFlagVisible() and self.isEnabled()}

    def checkForWarnings(self, vehicle):
        if self.prbEntity.getEntityType() != constants.ARENA_GUI_TYPE.RANDOM:
            return MarathonWarning.WRONG_BATTLE_TYPE
        return MarathonWarning.WRONG_VEH_TYPE if vehicle.level < self._data.minVehicleLevel else ''

    def isRewardObtained(self):
        return self._data.rewardObtained

    def isPostRewardObtained(self):
        return self._data.postRewardObtained

    def getMarathonQuests(self):
        return self._eventsCache.getHiddenQuests(self.__marathonFilterFunc)

    def getExtraTimeToBuy(self):
        return '' if self._data.state != MarathonState.FINISHED else self._resource.getExtraTimeToBuy()

    def getMarathonDiscount(self):
        passQuests, allQuests = self.getMarathonProgress()
        return int(passQuests * 100) / allQuests if passQuests and self._data.questsInChain else 0

    def getMarathonPostProgressionDiscount(self):
        progress = self.getMarathonPostProgress()
        return progress * self._data.styleTokenDiscount

    def setState(self):
        if not self._data.group:
            self._data.setState(MarathonState.UNKNOWN)
            return
        if self._data.suspendFlag:
            self._data.setState(MarathonState.SUSPENDED)
            return
        groupStartTimeLeft, groupFinishTimeLeft = self._data.getGroupTimeInterval()
        if groupStartTimeLeft > ZERO_TIME or groupFinishTimeLeft <= ZERO_TIME:
            self._data.setState(MarathonState.DISABLED)
            return
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self._data.getQuestTimeInterval()
        if firstQuestStartTimeLeft > ZERO_TIME:
            self._data.setState(MarathonState.NOT_STARTED)
        elif firstQuestStartTimeLeft <= ZERO_TIME < firstQuestFinishTimeLeft:
            self._data.setState(MarathonState.IN_PROGRESS)
        elif firstQuestFinishTimeLeft <= ZERO_TIME < groupFinishTimeLeft:
            self._data.setState(MarathonState.FINISHED)

    def updateQuestsData(self):
        currentStep, _ = self.getMarathonProgress()
        self._data.setQuest(self._eventsCache.getHiddenQuests(self.__marathonFilterFunc), currentStep)
        self._data.setGroup(self._eventsCache.getGroups(self.__marathonFilterFunc))
        tokensData = self.getTokensData(prefix=self._data.tokenPrefix)
        self._data.setRewardObtained(tokensData)
        self._data.setPostRewardObtained(tokensData)
        self._remainingRewards = self._getRemainingRewards()
        self._remainingPackedRewards = self._packRewards(self._remainingRewards)

    def getClosestStatusUpdateTime(self):
        if self._data.state not in MarathonState.ENABLED_STATE:
            return 0
        if self._data.state == MarathonState.FINISHED:
            _, timeLeft = self._data.getGroupTimeInterval()
            return timeLeft
        timeLeft, timeRight = self._data.getQuestTimeInterval()
        return (timeLeft if self._data.state == MarathonState.NOT_STARTED else timeRight) + 1

    def showRewardVideo(self):
        videoShownKey = self.__getRewardShownMarkKey(MARATHON_VIDEO_WAS_SHOWN_PREFIX)
        if self.isRewardObtained() and self._data.doesShowRewardVideo and not AccountSettings.getUIFlag(videoShownKey):
            showMarathonReward(self._data.vehicleID, videoShownKey)

    def showRewardScreen(self):
        if not self._data.doesShowRewardScreen or self._data.state in MarathonState.DISABLED_STATE:
            return
        isUIFlag = AccountSettings.getUIFlag(self.__getRewardShownMarkKey(MARATHON_REWARD_WAS_SHOWN_PREFIX))
        if self.isRewardObtained() and not isUIFlag:
            showBrowserOverlayView(self._getUrl() + self._data.marathonCompleteUrlAdd, alias=VIEW_ALIAS.BROWSER_OVERLAY, callbackOnLoad=partial(self.__setScreenWasShown, MARATHON_REWARD_WAS_SHOWN_PREFIX))

    def getVehiclePreviewTitleTooltip(self):
        if self._data.state not in MarathonState.ENABLED_STATE:
            return self._resource.getEmptyTooltip()
        return self._resource.getTitleNotStartedTooltip() if self._data.state == MarathonState.NOT_STARTED else self._resource.getTitleTooltip(self.getFinishSaleTime(), self.getMarathonDiscount())

    def getPreviewBuyBtnData(self):
        hasIgbLink = self.hasIgbLink()
        if self._data.state == MarathonState.IN_PROGRESS or self._data.state == MarathonState.FINISHED:
            discount = self.getMarathonDiscount()
            if discount:
                return self._resource.getBuyBtnDiscountData(discount, hasIgbLink)
            return self._resource.getBuyBtnEnabledData(hasIgbLink)
        return self._resource.getBuyBtnDisabledData(hasIgbLink)

    def getRewardsForQuestNumber(self, questNumber):
        rewardsQuests = self._getQuestsWithRewards()
        hiddenQuests = self._eventsCache.getHiddenQuests()
        questID = rewardsQuests[questNumber]
        rewards = hiddenQuests.get(questID).getBonuses()
        return rewards

    def getStyleQuestReward(self):
        quests = self._eventsCache.getHiddenQuests(self.__styleQuestFilterFunc)
        if not quests:
            return []
        styleQuest = quests.values()[0]
        return styleQuest.getBonuses()

    def _getRemainingRewards(self):
        finished, _ = self.getMarathonProgress()
        rewardsQuests = self._getQuestsWithRewards()
        remainingQuests = rewardsQuests[finished:]
        hiddenQuests = self._eventsCache.getHiddenQuests()
        bonuses = []
        for questID in remainingQuests:
            quest = hiddenQuests.get(questID)
            bonuses.extend(quest.getBonuses())

        merged = mergeBonuses(bonuses)
        return merged

    def getVehicleCrewReward(self):
        hiddenQuests = self._eventsCache.getHiddenQuests()
        vehiclesReward = None
        for questID in self._getQuestsWithRewards():
            quest = hiddenQuests.get(questID)
            if quest:
                bonuses = quest.getBonuses()
                vehiclesReward = next((reward for reward in bonuses if isinstance(reward, VehiclesBonus)), None)
            if vehiclesReward:
                break

        return getVehicleCrewReward(vehiclesReward)

    def _packRewards(self, rewards):
        packed = []
        for bonus in rewards:
            packed.extend(bonus.wrapToItemsPack(1))

        return packed

    def _getQuestsWithRewards(self):
        hiddenQuests = self._eventsCache.getHiddenQuests(self.__rewardQuestsFilterFunc)
        return natsorted(hiddenQuests)

    def __rewardQuestsFilterFunc(self, quest):
        questID = quest.getID()
        return questID.startswith(self.prefix) and self.rewardPostfix in questID

    def _getUrl(self, urlType=MarathonConfig.URL):
        baseUrl = self._lobbyContext.getServerSettings().getMarathonConfig().get(urlType, MarathonConfig.EMPTY_PATH)
        if not baseUrl:
            _logger.warning('Marathon url from marathon_config.xml is absent or invalid: %s', baseUrl)
        return baseUrl

    def __getRewardShownMarkKey(self, key):
        return '_'.join([key, self._data.tokenPrefix])

    def __setScreenWasShown(self, key):
        AccountSettings.setUIFlag(self.__getRewardShownMarkKey(key), True)

    def __marathonFilterFunc(self, q):
        return q.getID().startswith(self._data.prefix)

    def __styleQuestFilterFunc(self, q):
        return q.getID().startswith('post_reward')

    def __getProgress(self, progressType, prefix=None, postfix=None):
        progress = {}
        prefix = prefix or ''
        postfix = postfix or ''
        if progressType == 'quests':
            progress = self._eventsCache.questsProgress.getQuestsData()
        if progressType == 'tokens':
            progress = self._eventsCache.questsProgress.getTokensData()
        return {k:v for k, v in progress.iteritems() if k.startswith(prefix) and k.endswith(postfix)}

    def __getHangarFlagHeaderIcon(self):
        for key, imgPath in self._data.icons.mapFlagHeaderIcon.iteritems():
            if self._data.state in key:
                return imgPath

    def __getHangarFlagStateIcon(self, vehicle):
        if self._data.state not in MarathonState.ENABLED_STATE:
            return ''
        if self.isRewardObtained():
            return self._data.icons.okIcon
        if self._data.state == MarathonState.NOT_STARTED:
            return self._data.icons.timeIcon
        if self._data.state == MarathonState.FINISHED:
            return self._data.icons.saleIcon
        if self.checkForWarnings(vehicle):
            return self._data.icons.alertIcon
        _, firstQuestFinishTimeLeft = self._data.getQuestTimeInterval()
        return self._data.icons.iconFlag if firstQuestFinishTimeLeft > ONE_DAY else self._data.icons.timeIcon

    def __getTooltip(self):
        return self._data.flagTooltip if self.isAvailable() else self._data.disabledFlagTooltip
