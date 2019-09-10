# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_event_dp.py
import logging
import time
from collections import namedtuple
from functools import partial
import Event
import constants
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MARATHON_REWARD_WAS_SHOWN_PREFIX, MARATHON_VIDEO_WAS_SHOWN_PREFIX
from adisp import async, process
from gui import GUI_SETTINGS
from gui.Scaleform import MENU
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.marathon.marathon_reward_helper import showMarathonReward
from gui.marathon.marathon_constants import MARATHON_STATE, MARATHON_WARNING, ZERO_TIME, MARATHON_FLAG_TOOLTIP_HEADERS
from gui.prb_control import prbEntityProperty
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.formatters import text_styles
from helpers import dependency, i18n
from helpers.time_utils import ONE_DAY, getTimeStructInLocal, ONE_HOUR
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
MarathonEventTooltipData = namedtuple('MarathonEventTooltipData', ('header', 'body', 'bodyExtra', 'errorBattleType', 'errorVehType', 'extraStateSteps', 'extraStateDiscount', 'extraStateCompleted', 'stateStart', 'stateEnd', 'stateProgress', 'stateComplete', 'daysShort', 'hoursShort'))
MarathonEventIconsData = namedtuple('MarathonEventIconsData', ('tooltipHeader', 'libraryOkIcon', 'okIcon', 'timeIcon', 'timeIconGlow', 'alertIcon', 'iconFlag', 'libraryInProgress', 'saleIcon', 'mapFlagHeaderIcon'))

class IMarathonEvent(object):
    onDataChanged = None

    def init(self):
        pass

    def fini(self):
        pass


class MarathonEventDataProvider(object):

    @property
    def prefix(self):
        pass

    @property
    def tokenPrefix(self):
        pass

    @property
    def urlName(self):
        pass

    @property
    def marathonCompleteUrlAdd(self):
        pass

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.marathons()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_MARATHONS

    @property
    def tabTooltipDisabled(self):
        return QUESTS.MISSIONS_TAB_MARATHONS

    @property
    def vehiclePrefix(self):
        pass

    @property
    def vehicleID(self):
        pass

    @property
    def suspendPrefix(self):
        pass

    @property
    def completedTokenPostfix(self):
        pass

    @property
    def awardTokens(self):
        pass

    @property
    def questsInChain(self):
        pass

    @property
    def minVehicleLevel(self):
        pass

    @property
    def tooltipHeaderType(self):
        return MARATHON_FLAG_TOOLTIP_HEADERS.COUNTDOWN

    @property
    def showFlagTooltipBottom(self):
        return True

    @property
    def flagTooltip(self):
        return TOOLTIPS_CONSTANTS.MARATHON_QUESTS_PREVIEW

    @property
    def disabledFlagTooltip(self):
        return TOOLTIPS.MARATHON_OFF

    @property
    def tooltips(self):
        return MarathonEventTooltipData(header=R.strings.tooltips.marathon.header(), body=R.strings.tooltips.marathon.body(), bodyExtra=R.strings.tooltips.marathon.body.extra(), errorBattleType=R.strings.tooltips.marathon.error.battle_type(), errorVehType=R.strings.tooltips.marathon.error.veh_type(), extraStateSteps=R.strings.tooltips.marathon.extra_state.steps(), extraStateDiscount=R.strings.tooltips.marathon.extra_state.discount(), extraStateCompleted=R.strings.tooltips.marathon.extra_state.discount(), stateStart=R.strings.tooltips.marathon.state.start(), stateEnd=R.strings.tooltips.marathon.state.end(), stateProgress=R.strings.tooltips.marathon.extra_state(), stateComplete=R.strings.tooltips.marathon.state.complete(), daysShort=R.strings.tooltips.template.days.short(), hoursShort=R.strings.tooltips.template.hours.short())

    @property
    def icons(self):
        return MarathonEventIconsData(tooltipHeader=backport.image(R.images.gui.maps.icons.quests.marathonTooltipHeader()), libraryOkIcon=backport.image(R.images.gui.maps.icons.library.marathon.ok_icon()), okIcon=backport.image(R.images.gui.maps.icons.library.marathon.ok_icon()), timeIcon=backport.image(R.images.gui.maps.icons.library.marathon.time_icon()), timeIconGlow=backport.image(R.images.gui.maps.icons.library.time_icon()), alertIcon=backport.image(R.images.gui.maps.icons.library.marathon.alert_icon()), iconFlag=backport.image(R.images.gui.maps.icons.library.marathon.icon_flag()), libraryInProgress=backport.image(R.images.gui.maps.icons.library.inProgressIcon()), saleIcon=backport.image(R.images.gui.maps.icons.library.marathon.sale_icon()), mapFlagHeaderIcon={MARATHON_STATE.ENABLED_STATE: backport.image(R.images.gui.maps.icons.library.marathon.cup_icon()),
         MARATHON_STATE.DISABLED_STATE: backport.image(R.images.gui.maps.icons.library.marathon.cup_disable_icon())})

    def doesShowInPostBattle(self):
        return True

    def doesShowRewardVideo(self):
        return True

    def doesShowRewardScreen(self):
        return True

    def doesShowMissionsTab(self):
        return True


class MarathonEvent(IMarathonEvent, MarathonEventDataProvider):
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(MarathonEvent, self).__init__()
        self.__isEnabled = False
        self.__isAvailable = False
        self.__rewardObtained = False
        self.__state = ''
        self.__suspendFlag = False
        self.__quest = None
        self.__group = None
        self.__urlMacros = URLMacros()
        self.__baseUrl = GUI_SETTINGS.lookup(self.urlName)
        return

    @async
    @process
    def getUrl(self, callback):
        if self.__baseUrl is None:
            _logger.error('Requesting URL for marathon when base URL is not specified')
            url = yield lambda callback: callback('')
            callback(url)
        else:
            url = yield self.__urlMacros.parse(self.__baseUrl)
            callback(url)
        return

    def doesShowMissionsTab(self):
        return self.isEnabled()

    def getHangarFlag(self, state=None):
        return backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_italy())

    @prbEntityProperty
    def prbEntity(self):
        return None

    def isEnabled(self):
        return self.__isEnabled and not self._bootcamp.isInBootcamp()

    def isAvailable(self):
        return self.__isAvailable

    def getQuestsData(self, prefix=None, postfix=None):
        return self.__getProgress('quests', prefix, postfix)

    def getTokensData(self, prefix=None, postfix=None):
        return self.__getProgress('tokens', prefix, postfix)

    def getMarathonProgress(self, byCompletedTokensCount=False):
        tokens = self.getTokensData(prefix=self.tokenPrefix, postfix=self.completedTokenPostfix)
        if byCompletedTokensCount:
            return (len(tokens), self.questsInChain)
        tokenPrefixLen = len(self.tokenPrefix)
        res = []
        for tokenNames in tokens.keys():
            name = str(tokenNames[tokenPrefixLen:])
            res.append(int(filter(str.isdigit, name)))

        currentStep = sorted(res)[-1] if res else 0
        return (currentStep, self.questsInChain)

    def getState(self):
        return self.__state

    def getTooltipHeader(self):
        if self.tooltipHeaderType == MARATHON_FLAG_TOOLTIP_HEADERS.PROGRESS:
            return self.getFormattedDaysStatus()
        if self.tooltipHeaderType == MARATHON_FLAG_TOOLTIP_HEADERS.COUNTDOWN:
            return self.getFormattedRemainingTime()
        return self.getFormattedStartFinishText() if self.tooltipHeaderType == MARATHON_FLAG_TOOLTIP_HEADERS.TEXT else ('', '')

    def getMarathonFlagState(self, vehicle):
        return {'flagHeaderIcon': self.__getHangarFlagHeaderIcon(),
         'flagStateIcon': self.__getHangarFlagStateIcon(vehicle),
         'flagMain': self.getHangarFlag(self.__state),
         'tooltip': self.__getTooltip(),
         'enable': self.isAvailable(),
         'visible': self.isEnabled()}

    def checkForWarnings(self, vehicle):
        wrongBattleType = self.prbEntity.getEntityType() != constants.ARENA_GUI_TYPE.RANDOM
        if wrongBattleType:
            return MARATHON_WARNING.WRONG_BATTLE_TYPE
        wrongVehicleLevel = vehicle.level < self.minVehicleLevel
        return MARATHON_WARNING.WRONG_VEH_TYPE if wrongVehicleLevel else ''

    def isRewardObtained(self):
        return self.__rewardObtained

    def getMarathonQuests(self):
        return self._eventsCache.getHiddenQuests(self.__marathonFilterFunc)

    def getFormattedDaysStatus(self):
        icon = self.icons.libraryInProgress
        text = self.__getProgressInDays(self.__getTimeFromGroupStart())
        return (icon, text)

    def getFormattedRemainingTime(self):
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
        if self.__state == MARATHON_STATE.NOT_STARTED:
            icon = self.icons.timeIconGlow
            text = self.__getTillTimeStart(firstQuestStartTimeLeft)
        elif self.__state == MARATHON_STATE.IN_PROGRESS:
            text = self.__getTillTimeEnd(firstQuestFinishTimeLeft)
            if firstQuestFinishTimeLeft > ONE_DAY:
                icon = self.icons.libraryInProgress
            else:
                icon = self.icons.timeIconGlow
        else:
            icon = self.icons.libraryInProgress
            text = text_styles.main(backport.text(self.tooltips.stateComplete))
        return (icon, text)

    def getFormattedStartFinishText(self):
        startDate, finishDate = self.__getGroupStartFinishTime()
        startDateStruct = getTimeStructInLocal(startDate)
        finishDateStruct = getTimeStructInLocal(finishDate)
        startDateText = text_styles.main(backport.text(TOOLTIPS.MARATHON_DATE, day=startDateStruct.tm_mday, month=i18n.makeString(MENU.datetime_months(startDateStruct.tm_mon)), hour=startDateStruct.tm_hour, minutes=i18n.makeString('%02d', startDateStruct.tm_min)))
        finishDateText = text_styles.main(backport.text(TOOLTIPS.MARATHON_DATE, day=finishDateStruct.tm_mday, month=i18n.makeString(MENU.datetime_months(finishDateStruct.tm_mon)), hour=finishDateStruct.tm_hour, minutes=i18n.makeString('%02d', finishDateStruct.tm_min)))
        text = text_styles.main(backport.text(TOOLTIPS.MARATHON_SUBTITLE, startDate=startDateText, finishDate=finishDateText))
        return ('', text)

    def getExtraDaysToBuy(self):
        if self.__state == MARATHON_STATE.FINISHED:
            _, groupFinishTimeLeft = self.__getGroupTimeInterval()
            if groupFinishTimeLeft < ONE_DAY:
                groupFinishTimeLeft += ONE_DAY
            fmtText = text_styles.neutral(backport.text(self.tooltips.daysShort, value=str(int(groupFinishTimeLeft // ONE_DAY))))
            return fmtText

    def getMarathonDiscount(self):
        passQuests, allQuests = self.getMarathonProgress()
        return int(passQuests * 100) / allQuests if passQuests and self.questsInChain else 0

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
            sortedQuests = sorted(quests.itervalues(), key=self.__findEarliestQuest)
            for q in quests:
                if self.suspendPrefix in q:
                    self.__suspendFlag = True
                    break

            self.__quest = sortedQuests[0]
        else:
            self.__quest = None
        groups = self._eventsCache.getGroups(self.__marathonFilterFunc)
        if groups:
            sortedGroups = sorted(groups)
            self.__group = groups[sortedGroups[0]]
        else:
            self.__group = None
        tokens = self.getTokensData(prefix=self.tokenPrefix)
        rewardObtained = False
        for key, (_, count) in tokens.iteritems():
            if count > 0 and key in self.awardTokens:
                rewardObtained = True
                break

        self.__setRewardObtained(rewardObtained)
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
        if self.isRewardObtained() and self.doesShowRewardVideo() and not AccountSettings.getUIFlag(self.__getRewardShownMarkKey(MARATHON_VIDEO_WAS_SHOWN_PREFIX)):
            showMarathonReward(self.vehicleID)

    def showRewardScreen(self):
        if not self.doesShowRewardScreen():
            return
        if self.__state in MARATHON_STATE.DISABLED_STATE:
            return
        if self.isRewardObtained() and not AccountSettings.getUIFlag(self.__getRewardShownMarkKey(MARATHON_REWARD_WAS_SHOWN_PREFIX)):
            showBrowserOverlayView(self.__baseUrl + self.marathonCompleteUrlAdd, alias=VIEW_ALIAS.BROWSER_OVERLAY, callbackOnLoad=partial(self.__setScreenWasShown, MARATHON_REWARD_WAS_SHOWN_PREFIX))

    def __getRewardShownMarkKey(self, key):
        return '_'.join([key, self.tokenPrefix])

    def __setScreenWasShown(self, key):
        AccountSettings.setUIFlag(self.__getRewardShownMarkKey(key), True)

    def __setRewardObtained(self, obtained):
        self.__rewardObtained = obtained

    def __findEarliestQuest(self, quest):
        return quest.getStartTimeLeft()

    def __marathonFilterFunc(self, q):
        return q.getID().startswith(self.prefix)

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
        for key, imgPath in self.icons.mapFlagHeaderIcon.iteritems():
            if self.__state in key:
                return imgPath

    def __getHangarFlagStateIcon(self, vehicle):
        if self.__state not in MARATHON_STATE.ENABLED_STATE:
            return ''
        if self.isRewardObtained():
            return self.icons.okIcon
        if self.__state == MARATHON_STATE.NOT_STARTED:
            return self.icons.timeIcon
        if self.__state == MARATHON_STATE.IN_PROGRESS:
            warning = self.checkForWarnings(vehicle)
            if warning:
                return self.icons.alertIcon
            _, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
            if firstQuestFinishTimeLeft > ONE_DAY:
                return self.icons.iconFlag
            if firstQuestFinishTimeLeft <= ONE_DAY:
                return self.icons.timeIcon
        return self.icons.saleIcon if self.__state == MARATHON_STATE.FINISHED else ''

    def __getTillTimeEnd(self, value):
        return self.__getFormattedTillTimeString(value, self.tooltips.stateEnd)

    def __getTillTimeStart(self, value):
        return self.__getFormattedTillTimeString(value, self.tooltips.stateStart, extraFmt=True)

    def __getProgressInDays(self, value):
        return self.__getTextInDays(value, self.tooltips.stateProgress)

    def __getTextInDays(self, timeValue, keyNamespace):
        gmtime = time.gmtime(timeValue)
        text = text_styles.stats(backport.text(self.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
        return text_styles.main(backport.text(keyNamespace, value=text))

    def __getFormattedTillTimeString(self, timeValue, keyNamespace, isRoundUp=True, extraFmt=False):
        gmtime = time.gmtime(timeValue)
        if isRoundUp and gmtime.tm_sec > 0:
            timeValue += ONE_HOUR
            gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            gmtime = time.gmtime(timeValue - ONE_DAY)
            text = text_styles.stats(backport.text(self.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
            return text_styles.main(backport.text(keyNamespace, value=text))
        if extraFmt:
            text = text_styles.stats(backport.text(self.tooltips.hoursShort, value=str(time.struct_time(gmtime).tm_hour)))
            return text_styles.main(backport.text(keyNamespace, value=text))
        text = backport.text(self.tooltips.hoursShort, value=str(time.struct_time(gmtime).tm_hour))
        return text_styles.tutorial(backport.text(keyNamespace, value=text))

    def __getTooltip(self):
        return self.flagTooltip if self.isAvailable() else self.disabledFlagTooltip

    def __getTimeFromGroupStart(self):
        return self.__group.getTimeFromStartTillNow() if self.__group else ZERO_TIME

    def __getGroupTimeInterval(self):
        return (self.__group.getStartTimeLeft(), self.__group.getFinishTimeLeft()) if self.__group else (ZERO_TIME, ZERO_TIME)

    def __getQuestTimeInterval(self):
        return (self.__quest.getStartTimeLeft(), self.__quest.getFinishTimeLeft()) if self.__quest else (ZERO_TIME, ZERO_TIME)

    def __getGroupStartFinishTime(self):
        return (self.__group.getStartTimeRaw(), self.__group.getFinishTimeRaw()) if self.__group else (ZERO_TIME, ZERO_TIME)
