# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_event_controller.py
import time
import Event
import constants
from adisp import process, async
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMarcos
from gui.marathon.marathon_constants import MARATHONS_DATA, MARATHON_STATE, MAP_FLAG_HEADER_ICON, MARATHON_WARNING, PROGRESS_TOOLTIP_HEADER, COUNTDOWN_TOOLTIP_HEADER, ZERO_TIME
from gui.prb_control import prbEntityProperty
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_DAY, ONE_HOUR
from skeletons.gui.game_control import IMarathonEventsController, IBootcampController
from skeletons.gui.server_events import IEventsCache

class MarathonEventsController(IMarathonEventsController, Notifiable):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(MarathonEventsController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onFlagUpdateNotify = Event.Event(self.__eventManager)
        self.__marathons = [ MarathonEvent(data) for data in MARATHONS_DATA ]

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

    def onLobbyStarted(self, ctx):
        super(MarathonEventsController, self).onLobbyStarted(ctx)
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._eventsCache.onProgressUpdated += self.__onSyncCompleted
        self.__onSyncCompleted()

    def __onSyncCompleted(self, *args):
        self.__checkEvents()
        self.__reloadNotification()

    def __checkEvents(self):
        for marathon in self.__marathons:
            marathon.updateQuestsData()
            marathon.setState()

    def __updateFlagState(self):
        self.__checkEvents()
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
        self.__state = ''
        self.__suspendFlag = False
        self.__quest = None
        self.__group = None
        self.__urlMacros = URLMarcos()
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

    def getMarathonProgress(self, byCompletedTokensCount=True):
        tokens = self.getTokensData(prefix=self.prefix, postfix=self.data.completedTokenPostfix)
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
        else:
            return self.getFormattedRemainingTime() if self.data.tooltipHeaderType == COUNTDOWN_TOOLTIP_HEADER else None

    def getMarathonFlagState(self, vehicle):
        return {'flagHeaderIcon': self.__getHangarFlagHeaderIcon(),
         'flagStateIcon': self.__getHangarFlagStateIcon(vehicle),
         'flagMain': self.__getHangarFlagMain(),
         'tooltip': self.__getTooltip(),
         'enable': self.isAvailable(),
         'visible': self.isEnabled()}

    def checkForWarnings(self, _):
        wrongBattleType = self.prbEntity.getEntityType() != constants.ARENA_GUI_TYPE.RANDOM
        return MARATHON_WARNING.WRONG_BATTLE_TYPE if wrongBattleType else ''

    def isVehicleObtained(self):
        return self.__vehInInventory

    def getMarathonQuests(self):
        return self._eventsCache.getHiddenQuests(self.__marathonFilterFunc)

    def getFormattedDaysStatus(self):
        icon = RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON
        text = self.__getProgressInDays(self.__getTimeFromGroupStart())
        return (icon, text)

    def getFormattedRemainingTime(self):
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
        if self.__state == MARATHON_STATE.NOT_STARTED:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_TIME_ICON
            text = self.__getTillTimeStart(firstQuestStartTimeLeft)
        elif self.__state == MARATHON_STATE.IN_PROGRESS:
            text = self.__getTillTimeEnd(firstQuestFinishTimeLeft)
            if firstQuestFinishTimeLeft > ONE_DAY:
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON
            else:
                icon = RES_ICONS.MAPS_ICONS_LIBRARY_TIME_ICON
        else:
            icon = RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON
            text = text_styles.main(_ms(TOOLTIPS.MARATHON_STATE_COMPLETE))
        return (icon, text)

    def getExtraDaysToBuy(self):
        if self.__state == MARATHON_STATE.FINISHED:
            _, groupFinishTimeLeft = self.__getGroupTimeInterval()
            if groupFinishTimeLeft < ONE_DAY:
                groupFinishTimeLeft += ONE_DAY
            fmtText = text_styles.neutral(_ms(self.data.tooltips.daysShort, value=str(int(groupFinishTimeLeft // ONE_DAY))))
            return fmtText

    def getMarathonDiscount(self):
        passQuests, allQuests = self.getMarathonProgress()
        return int(passQuests * 100) / allQuests if passQuests and self.data.questsInChain else 0

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
            sortedIndexList = sorted(quests)
            for q in sortedIndexList:
                if self.data.suspend in q:
                    self.__suspendFlag = True
                    break

            self.__quest = quests[sortedIndexList[0]]
        groups = self._eventsCache.getGroups(self.__marathonFilterFunc)
        if groups:
            sortedGroups = sorted(groups)
            self.__group = groups[sortedGroups[0]]
        else:
            self.__group = None
        tokens = self.getTokensData(prefix=self.prefix).keys()
        self.__vehInInventory = any((t in tokens for t in self.data.awardTokens))
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

    def __marathonFilterFunc(self, q):
        return q.getID().startswith(self.prefix)

    def __getProgress(self, progressType, prefix=None, postfix=None):
        progress = self._eventsCache.questsProgress.getCacheValue(progressType, {})
        if prefix:
            progress = {k:v for k, v in progress.iteritems() if k.startswith(prefix)}
        if postfix:
            progress = {k:v for k, v in progress.iteritems() if k.endswith(postfix)}
        return progress

    def __getHangarFlagHeaderIcon(self):
        for key, imgPath in MAP_FLAG_HEADER_ICON.iteritems():
            if self.__state in key:
                return imgPath

    def __getHangarFlagMain(self):
        return self.data.icons.mainHangarFlag

    def __getHangarFlagStateIcon(self, vehicle):
        if self.__state not in MARATHON_STATE.ENABLED_STATE:
            return ''
        if self.__vehInInventory:
            return self.data.icons.okIcon
        if self.__state == MARATHON_STATE.NOT_STARTED:
            return self.data.icons.timeIcon
        if self.__state == MARATHON_STATE.IN_PROGRESS:
            warning = self.checkForWarnings(vehicle)
            if warning:
                return self.data.icons.alertIcon
            _, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
            if firstQuestFinishTimeLeft > ONE_DAY:
                return self.data.icons.iconFlag
            if firstQuestFinishTimeLeft <= ONE_DAY:
                return self.data.icons.timeIcon
        return self.data.icons.saleIcon if self.__state == MARATHON_STATE.FINISHED else ''

    def __getTillTimeEnd(self, value):
        return self.__getFormattedTillTimeString(value, self.data.tooltips.stateEnd)

    def __getTillTimeStart(self, value):
        return self.__getFormattedTillTimeString(value, self.data.tooltips.stateStart, extraFmt=True)

    def __getProgressInDays(self, value):
        return self.__getTextInDays(value, self.data.tooltips.stateProgress)

    def __getTextInDays(self, timeValue, keyNamespace):
        gmtime = time.gmtime(timeValue)
        text = text_styles.stats(_ms(self.data.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
        return text_styles.main(_ms(keyNamespace, value=text))

    def __getFormattedTillTimeString(self, timeValue, keyNamespace, isRoundUp=True, extraFmt=False):
        gmtime = time.gmtime(timeValue)
        if isRoundUp and gmtime.tm_sec > 0:
            timeValue += ONE_HOUR
            gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            gmtime = time.gmtime(timeValue - ONE_DAY)
            text = text_styles.stats(_ms(self.data.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
            return text_styles.main(_ms(keyNamespace, value=text))
        if extraFmt:
            text = text_styles.stats(_ms(self.data.tooltips.hoursShort, value=str(time.struct_time(gmtime).tm_hour)))
            return text_styles.main(_ms(keyNamespace, value=text))
        text = _ms(self.data.tooltips.hoursShort, value=str(time.struct_time(gmtime).tm_hour))
        return text_styles.tutorial(_ms(keyNamespace, value=text))

    def __getTooltip(self):
        return TOOLTIPS_CONSTANTS.MARATHON_QUESTS_PREVIEW if self.isAvailable() else TOOLTIPS.MARATHON_OFF

    def __getTimeFromGroupStart(self):
        return self.__group.getTimeFromStartTillNow() if self.__group else ZERO_TIME

    def __getGroupTimeInterval(self):
        if self.__group:
            return (self.__group.getStartTimeLeft(), self.__group.getFinishTimeLeft())
        zeroTime = ZERO_TIME
        return (zeroTime, zeroTime)

    def __getQuestTimeInterval(self):
        if self.__quest:
            return (self.__quest.getStartTimeLeft(), self.__quest.getFinishTimeLeft())
        zeroTime = ZERO_TIME
        return (zeroTime, zeroTime)
