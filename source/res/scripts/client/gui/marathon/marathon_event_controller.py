# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_event_controller.py
import time
import Event
import Windowing
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MARATHON_REWARD_VIDEO_WAS_SHOWN, MARATHON_REWARD_SCREEN_WAS_SHOWN
from adisp import process, async
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.app_loader import sf_lobby
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.marathon.marathon_reward_helper import showMarathonReward
from gui.marathon.marathon_constants import MARATHONS_DATA, MARATHON_STATE, MARATHON_WARNING, PROGRESS_TOOLTIP_HEADER, COUNTDOWN_TOOLTIP_HEADER, ZERO_TIME, TEXT_TOOLTIP_HEADER, MARATHON_COMPLETE_URL_ADD
from gui.prb_control import prbEntityProperty
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency, isPlayerAccount
from helpers.time_utils import ONE_DAY, ONE_HOUR, getTimeStructInLocal
from skeletons.gui.game_control import IMarathonEventsController, IBootcampController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class MarathonEventsController(IMarathonEventsController, Notifiable):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(MarathonEventsController, self).__init__()
        self.__isLobbyInited = False
        self.__isInHangar = False
        self.__eventManager = Event.EventManager()
        self.onFlagUpdateNotify = Event.Event(self.__eventManager)
        self.__marathons = [ MarathonEvent(data) for data in MARATHONS_DATA ]

    @sf_lobby
    def app(self):
        pass

    def addMarathon(self, data):
        self.__marathons.append(MarathonEvent(data))

    def delMarathon(self, prefix):
        self.__marathons.remove(self.__findByPrefix(prefix))

    def getMarathon(self, prefix):
        return self.__findByPrefix(prefix)

    def getMarathons(self):
        return self.__marathons

    def getPrimaryMarathon(self):
        return self.__marathons[0] if self.__marathons else None

    def getFirstAvailableMarathon(self):
        for marathon in self.__marathons:
            if marathon.isAvailable():
                return marathon

        return None

    def getPrefix(self, eventID):
        for marathon in self.__marathons:
            if eventID.startswith(marathon.prefix):
                return marathon.prefix

        return None

    def getVisibleInPostBattleQuests(self):
        result = {}
        for marathon in self.__marathons:
            if marathon.isShowInPostBattle():
                result.update(marathon.getMarathonQuests())

        return result

    def getQuestsData(self, prefix=None, postfix=None):
        return self.getPrimaryMarathon().getQuestsData(prefix, postfix) if self.isAnyActive() else {}

    def getTokensData(self, prefix=None, postfix=None):
        return self.getPrimaryMarathon().getTokensData(prefix, postfix) if self.isAnyActive() else {}

    def isAnyActive(self):
        return any((marathon.isAvailable() for marathon in self.__marathons))

    def fini(self):
        self.__stop()
        super(MarathonEventsController, self).fini()

    def onDisconnected(self):
        super(MarathonEventsController, self).onDisconnected()
        self.__stop()

    def onAvatarBecomePlayer(self):
        super(MarathonEventsController, self).onAvatarBecomePlayer()
        self.__stop()

    def onLobbyInited(self, event):
        if not isPlayerAccount():
            return
        self.__isLobbyInited = True

    def onLobbyStarted(self, ctx):
        super(MarathonEventsController, self).onLobbyStarted(ctx)
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._eventsCache.onProgressUpdated += self.__onSyncCompleted
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.__onSyncCompleted()

    def __onWindowAccessibilityChanged(self, isAccessible):
        self.__tryShowRewardVideo()

    def __tryShowRewardScreen(self):
        if self.__isLobbyInited and self.__isInHangar:
            for marathon in self.__marathons:
                marathon.showRewardScreen()

    def __tryShowRewardVideo(self):
        for marathon in self.__marathons:
            marathon.showRewardVideo()

    def __onViewLoaded(self, pyView, _):
        if self.__isLobbyInited:
            if pyView.alias == VIEW_ALIAS.LOBBY_HANGAR:
                self.__isInHangar = True
                self.__tryShowRewardScreen()
            elif pyView.viewType == ViewTypes.LOBBY_SUB:
                self.__isInHangar = False

    def __onSyncCompleted(self, *args):
        self.__checkEvents()
        self.__tryShowRewardVideo()
        self.__tryShowRewardScreen()
        self.__reloadNotification()

    def __checkEvents(self):
        for marathon in self.__marathons:
            marathon.updateQuestsData()
            marathon.setState()

    def __updateFlagState(self):
        self.__checkEvents()
        self.__tryShowRewardScreen()
        self.onFlagUpdateNotify()

    def __getClosestStatusUpdateTime(self):
        if self.__marathons:
            return min([ marathon.getClosestStatusUpdateTime() for marathon in self.__marathons ])

    def __reloadNotification(self):
        self.clearNotification()
        timePeriod = self.__getClosestStatusUpdateTime()
        if timePeriod:
            self.addNotificator(PeriodicNotifier(self.__getClosestStatusUpdateTime, self.__updateFlagState))
            self.startNotification()

    def __stop(self):
        self.clearNotification()
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._eventsCache.onProgressUpdated -= self.__onSyncCompleted
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.__isLobbyInited = False

    def __findByPrefix(self, prefix):
        for marathon in self.__marathons:
            if marathon.prefix == prefix:
                return marathon

        return None


class MarathonEvent(object):
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, data):
        super(MarathonEvent, self).__init__()
        self.__data = data
        self.__isEnabled = False
        self.__isAvailable = False
        self.__vehInInventory = False
        self.__rewardObtained = False
        self.__state = ''
        self.__suspendFlag = False
        self.__quest = None
        self.__group = None
        self.__urlMacros = URLMacros()
        self.__baseUrl = GUI_SETTINGS.lookup(data.url)
        return

    @property
    def prefix(self):
        return self.__data.prefix

    @property
    def data(self):
        return self.__data

    @prbEntityProperty
    def prbEntity(self):
        return None

    @async
    @process
    def getUrl(self, callback):
        if self.__baseUrl is None:
            LOG_ERROR('Requesting URL for marathon when base URL is not specified')
            yield lambda clb: clb(None)
        else:
            url = yield self.__urlMacros.parse(self.__baseUrl)
            callback(url)
        return

    def isEnabled(self):
        return self.__isEnabled and not self._bootcamp.isInBootcamp()

    def isAvailable(self):
        return self.__isAvailable

    def getTooltipData(self):
        return self.__data.tooltips

    def getIconsData(self):
        return self.__data.icons

    def getQuestsData(self, prefix=None, postfix=None):
        return self.__getProgress('quests', prefix, postfix)

    def getTokensData(self, prefix=None, postfix=None):
        return self.__getProgress('tokens', prefix, postfix)

    def getMarathonProgress(self, byCompletedTokensCount=False):
        tokens = self.getTokensData(prefix=self.data.tokenPrefix, postfix=self.data.completedTokenPostfix)
        if byCompletedTokensCount:
            return (len(tokens), self.data.questsInChain)
        tokenPrefixLen = len(self.data.tokenPrefix)
        res = []
        for tokenNames in tokens.keys():
            name = str(tokenNames[tokenPrefixLen:])
            res.append(int(filter(str.isdigit, name)))

        currentStep = sorted(res)[-1] if res else 0
        return (currentStep, self.data.questsInChain)

    def getState(self):
        return self.__state

    def getTooltipHeader(self):
        if self.data.tooltipHeaderType == PROGRESS_TOOLTIP_HEADER:
            return self.getFormattedDaysStatus()
        if self.data.tooltipHeaderType == COUNTDOWN_TOOLTIP_HEADER:
            return self.getFormattedRemainingTime()
        return self.getFormattedStartFinishText() if self.data.tooltipHeaderType == TEXT_TOOLTIP_HEADER else ('', '')

    def getMarathonFlagState(self, vehicle):
        return {'flagHeaderIcon': self.__getHangarFlagHeaderIcon(),
         'flagStateIcon': self.__getHangarFlagStateIcon(vehicle),
         'flagMain': self.__getHangarFlagMain(),
         'tooltip': self.__getTooltip(),
         'enable': self.isAvailable(),
         'visible': self.isEnabled()}

    def checkForWarnings(self, vehicle):
        if self.prbEntity is None:
            return ''
        else:
            wrongBattleType = self.prbEntity.getEntityType() != constants.ARENA_GUI_TYPE.RANDOM
            if wrongBattleType:
                return MARATHON_WARNING.WRONG_BATTLE_TYPE
            wrongVehicleLevel = vehicle.level < self.data.minVehicleLevel
            return MARATHON_WARNING.WRONG_VEH_TYPE if wrongVehicleLevel else ''

    def setVehicleObtained(self, obtained):
        self.__vehInInventory = obtained

    def setRewardObtained(self, obtained):
        self.__rewardObtained = obtained

    def isVehicleObtained(self):
        return self.__vehInInventory

    def isRewardObtained(self):
        return self.__rewardObtained

    def getMarathonQuests(self):
        return self._eventsCache.getHiddenQuests(self.__marathonFilterFunc)

    def getFormattedDaysStatus(self):
        icon = backport.image(R.images.gui.maps.icons.library.inProgressIcon())
        text = self.__getProgressInDays(self.__getTimeFromGroupStart())
        return (icon, text)

    def getFormattedRemainingTime(self):
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
        if self.__state == MARATHON_STATE.NOT_STARTED:
            icon = self.data.icons.timeIconGlow
            text = self.__getTillTimeStart(firstQuestStartTimeLeft)
        elif self.__state == MARATHON_STATE.IN_PROGRESS:
            text = self.__getTillTimeEnd(firstQuestFinishTimeLeft)
            if firstQuestFinishTimeLeft > ONE_DAY:
                icon = self.data.icons.iconFlag
            else:
                icon = self.data.icons.timeIconGlow
        else:
            icon = self.data.icons.timeIconGlow
            text = text_styles.tutorial(backport.text(R.strings.tooltips.marathon.state.complete()))
        return (icon, text)

    def getFormattedStartFinishText(self):
        startDateStruct, finishDateStruct = self.getGroupStartFinishDates()
        startDateText = text_styles.main(backport.text(R.strings.tooltips.marathon.date(), day=startDateStruct.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(startDateStruct.tm_mon)), hour=startDateStruct.tm_hour, minutes=backport.text('%02d', startDateStruct.tm_min)))
        finishDateText = text_styles.main(backport.text(R.strings.tooltips.marathon.date(), day=finishDateStruct.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(finishDateStruct.tm_mon)), hour=finishDateStruct.tm_hour, minutes=backport.text('%02d', finishDateStruct.tm_min)))
        text = text_styles.main(backport.text(R.strings.tooltips.marathon.subtitle(), startDate=startDateText, finishDate=finishDateText))
        return ('', text)

    def getGroupStartFinishDates(self):
        startDate, finishDate = self.__getGroupStartFinishTime()
        startDateStruct = getTimeStructInLocal(startDate)
        finishDateStruct = getTimeStructInLocal(finishDate)
        return (startDateStruct, finishDateStruct)

    def getExtraDaysToBuy(self):
        if self.__state == MARATHON_STATE.FINISHED:
            _, groupFinishTimeLeft = self.__getGroupTimeInterval()
            if groupFinishTimeLeft < ONE_DAY:
                groupFinishTimeLeft += ONE_DAY
            fmtText = text_styles.stats(backport.text(self.data.tooltips.daysShort, value=str(int(groupFinishTimeLeft // ONE_DAY))))
            return fmtText

    def getMarathonDiscount(self):
        passQuests, allQuests = self.getMarathonProgress()
        return int(passQuests * 100) / allQuests if passQuests and self.data.questsInChain else 0

    def getBonusData(self):
        bonusTokenCount = self.__getBonusTokenCount()
        bonusQuests = self._eventsCache.getHiddenQuests(self.__bonusFilterFunc)
        bonusQuest = bonusQuests.get(self.data.bonusQuestPrefix + str(bonusTokenCount), None)
        totalXP = 0
        tankmanXP = 0
        if bonusQuest is not None and bonusTokenCount > 0:
            totalXPbonus = next(iter(bonusQuest.getBonuses('xpFactor')), None)
            tankmanXPbonus = next(iter(bonusQuest.getBonuses('tankmenXPFactor')), None)
            totalXP = self.__convertFactorToPercent(totalXPbonus)
            tankmanXP = self.__convertFactorToPercent(tankmanXPbonus)
        return {'totalXP': self.__getFormattedExpBonus(totalXP),
         'tankmanXP': self.__getFormattedExpBonus(tankmanXP),
         'missionCounter': str(bonusTokenCount),
         'tooltip': self.__getBonusTooltip()}

    def isBonusWidgetVisible(self):
        if self.prbEntity is None:
            return False
        else:
            wrongBattleType = self.prbEntity.getEntityType() != constants.ARENA_GUI_TYPE.RANDOM
            if wrongBattleType:
                return False
            return False if self.__state in MARATHON_STATE.DISABLED_STATE else True

    def isShowInPostBattle(self):
        return self.__data.showInPostBattle

    def setState(self):
        if not self.__group:
            self.__isEnabled = False
            self.__isAvailable = False
            self.__state = MARATHON_STATE.UNKNOWN
            return self.__state
        if self.__suspendFlag:
            self.__state = MARATHON_STATE.SUSPENDED
            self.__isEnabled = True
            self.__isAvailable = False
            return self.__state
        groupStartTimeLeft, groupFinishTimeLeft = self.__getGroupTimeInterval()
        zeroTime = ZERO_TIME
        if groupStartTimeLeft > zeroTime or groupFinishTimeLeft <= zeroTime:
            self.__isEnabled = False
            self.__isAvailable = False
            self.__state = MARATHON_STATE.DISABLED
            return self.__state
        if groupStartTimeLeft <= zeroTime < groupFinishTimeLeft:
            self.__isEnabled = True
            self.__isAvailable = True
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
        if firstQuestStartTimeLeft > zeroTime:
            self.__state = MARATHON_STATE.NOT_STARTED
        elif firstQuestStartTimeLeft <= zeroTime < firstQuestFinishTimeLeft:
            self.__state = MARATHON_STATE.IN_PROGRESS
        elif firstQuestFinishTimeLeft <= zeroTime < groupFinishTimeLeft:
            self.__state = MARATHON_STATE.FINISHED
        return self.__state

    def updateQuestsData(self):
        self.__suspendFlag = False
        quests = self._eventsCache.getHiddenQuests(self.__marathonFilterFunc)
        if quests:
            tokenPrefixLen = len(self.data.tokenPrefix)
            sortedIndexList = sorted(quests, key=lambda questName: int(filter(str.isdigit, str(questName[tokenPrefixLen:]))))
            for q in sortedIndexList:
                if self.data.suspend in q:
                    self.__suspendFlag = True
                    break

            self.__quest = quests[sortedIndexList[0]]
        else:
            self.__quest = None
        groups = self._eventsCache.getGroups(self.__marathonFilterFunc)
        if groups:
            sortedGroups = sorted(groups)
            self.__group = groups[sortedGroups[0]]
        else:
            self.__group = None
        tokens = self.getTokensData(prefix=self.data.tokenPrefix).keys()
        self.setVehicleObtained(any((t in tokens for t in self.data.vehicleAwardTokens)))
        self.setRewardObtained(any((t in tokens for t in self.data.awardTokens)))
        return

    def getClosestStatusUpdateTime(self):
        if self.__state == MARATHON_STATE.NOT_STARTED:
            timeLeft, _ = self.__getQuestTimeInterval()
            return timeLeft + 1
        if self.__state == MARATHON_STATE.IN_PROGRESS:
            _, timeLeft = self.__getQuestTimeInterval()
            return timeLeft + 1
        if self.__state == MARATHON_STATE.FINISHED:
            _, timeLeft = self.__getGroupTimeInterval()
            return timeLeft

    def showRewardVideo(self):
        if self.isVehicleObtained() and self.data.showRewardVideo and not AccountSettings.getFilter(MARATHON_REWARD_VIDEO_WAS_SHOWN) and Windowing.isWindowAccessible():
            showMarathonReward(self.data.vehicleID)

    def showRewardScreen(self):
        if (self.__state == MARATHON_STATE.FINISHED or self.isRewardObtained()) and self.data.showRewardScreen and not AccountSettings.getFilter(MARATHON_REWARD_SCREEN_WAS_SHOWN):
            showBrowserOverlayView(self.__baseUrl + MARATHON_COMPLETE_URL_ADD, alias=VIEW_ALIAS.BROWSER_OVERLAY, callbackOnLoad=self.__setScreenWasShown)

    def __setScreenWasShown(self):
        AccountSettings.setFilter(MARATHON_REWARD_SCREEN_WAS_SHOWN, True)

    def __getBonusTokenCount(self):
        bonusToken = self._eventsCache.questsProgress.getToken(self.data.bonusToken)
        return bonusToken.count

    def __convertFactorToPercent(self, factor):
        return (factor.getValue() - 1) * 100 if factor is not None else 0

    def __getFormattedExpBonus(self, exp):
        roundedExp = int(exp)
        result = str(roundedExp) + backport.text(R.strings.common.common.percent())
        return result if roundedExp == 0 else backport.text(R.strings.common.common.plus()) + result

    def __marathonFilterFunc(self, q):
        return q.getID().startswith(self.prefix)

    def __bonusFilterFunc(self, q):
        return q.getID().startswith(self.data.bonusQuestPrefix)

    def __getProgress(self, progressType, prefix=None, postfix=None):
        progress = {}
        if progressType == 'quests':
            progress = self._eventsCache.questsProgress.getQuestsData()
        elif progressType == 'tokens':
            progress = self._eventsCache.questsProgress.getTokensData()
        if prefix:
            progress = {k:v for k, v in progress.iteritems() if k.startswith(prefix)}
        if postfix:
            progress = {k:v for k, v in progress.iteritems() if k.endswith(postfix)}
        return progress

    def __getHangarFlagHeaderIcon(self):
        if not self.data.showFlagIcons:
            return ''
        for key, imgPath in self.data.icons.mapFlagHeaderIcon.iteritems():
            if self.__state in key:
                return imgPath

    def __getHangarFlagMain(self):
        return self.data.icons.mainHangarFlag

    def __getHangarFlagStateIcon(self, vehicle):
        if not self.data.showFlagIcons:
            return ''
        warning = self.checkForWarnings(vehicle)
        if self.__state not in MARATHON_STATE.ENABLED_STATE:
            return ''
        if self.__state == MARATHON_STATE.NOT_STARTED:
            return self.data.icons.timeIcon
        if self.__state == MARATHON_STATE.IN_PROGRESS:
            if warning:
                return self.data.icons.alertIcon
            if self.isRewardObtained():
                return self.data.icons.doubleOkIcon
            if self.isVehicleObtained():
                return self.data.icons.okIcon
            _, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
            if firstQuestFinishTimeLeft > ONE_DAY:
                return self.data.icons.iconFlag
            if firstQuestFinishTimeLeft <= ONE_DAY:
                return self.data.icons.timeIcon
        if self.__state == MARATHON_STATE.FINISHED:
            if warning == MARATHON_WARNING.WRONG_BATTLE_TYPE:
                return self.data.icons.alertIcon
            return self.data.icons.timeIcon

    def __getTillTimeEnd(self, value):
        return self.__getFormattedTillTimeString(value, self.data.tooltips.stateEnd)

    def __getTillTimeStart(self, value):
        return self.__getFormattedTillTimeString(value, self.data.tooltips.stateStart, extraFmt=True)

    def __getProgressInDays(self, value):
        return self.__getTextInDays(value, self.data.tooltips.stateProgress)

    def __getTextInDays(self, timeValue, keyNamespace):
        gmtime = time.gmtime(timeValue)
        text = text_styles.stats(backport.text(self.data.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
        return text_styles.main(backport.text(keyNamespace, value=text))

    def __getFormattedTillTimeString(self, timeValue, keyNamespace, isRoundUp=True, extraFmt=False):
        gmtime = time.gmtime(timeValue)
        if isRoundUp and gmtime.tm_sec > 0:
            timeValue += ONE_HOUR
            gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            gmtime = time.gmtime(timeValue - ONE_DAY)
            text = text_styles.stats(backport.text(self.data.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
            return text_styles.main(backport.text(keyNamespace, value=text))
        if extraFmt:
            text = text_styles.stats(backport.text(self.data.tooltips.hoursShort, value=str(time.struct_time(gmtime).tm_hour)))
            return text_styles.main(backport.text(keyNamespace, value=text))
        text = backport.text(self.data.tooltips.hoursShort, value=str(time.struct_time(gmtime).tm_hour))
        return text_styles.tutorial(backport.text(keyNamespace, value=text))

    def __getTooltip(self):
        return TOOLTIPS_CONSTANTS.MARATHON_QUESTS_PREVIEW if self.isAvailable() else TOOLTIPS.MARATHON_OFF

    def __getBonusTooltip(self):
        return TOOLTIPS_CONSTANTS.QUEST_BONUS_INFO if self.isAvailable() else TOOLTIPS.MARATHON_OFF

    def __getTimeFromGroupStart(self):
        return self.__group.getTimeFromStartTillNow() if self.__group else ZERO_TIME

    def __getGroupTimeInterval(self):
        return (self.__group.getStartTimeLeft(), self.__group.getFinishTimeLeft()) if self.__group else (ZERO_TIME, ZERO_TIME)

    def __getQuestTimeInterval(self):
        return (self.__quest.getStartTimeLeft(), self.__quest.getFinishTimeLeft()) if self.__quest else (ZERO_TIME, ZERO_TIME)

    def __getGroupStartFinishTime(self):
        return (self.__group.getStartTimeRaw(), self.__group.getFinishTimeRaw()) if self.__group else (ZERO_TIME, ZERO_TIME)
