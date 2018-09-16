# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_event_controller.py
import time
import constants
import Event
from adisp import process, async
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMarcos
from gui.marathon.marathon_constants import MARATHON_STATE, MAP_FLAG_HEADER_ICON, MARATHON_PREFIX, ZERO_TIME, MARATHON_SUSPEND, MARATHON_WARNING, MARATHON_QUESTS_IN_CHAIN, MARATHON_COMPLETED_TOKEN_POSTFIX, MARATHON_AWARD_TOKENS
from gui.prb_control import prbEntityProperty
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers.time_utils import ONE_DAY, ONE_HOUR
from skeletons.gui.game_control import IMarathonEventController, IBootcampController
from skeletons.gui.server_events import IEventsCache
from helpers.i18n import makeString as _ms

def marathonFilterFunc(q):
    return q.getID().startswith(MARATHON_PREFIX)


class MarathonEventController(IMarathonEventController, Notifiable):
    _eventsCache = dependency.descriptor(IEventsCache)
    _bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(MarathonEventController, self).__init__()
        self.__isEnabled = False
        self.__isAvailable = False
        self.__vehInInventory = False
        self.__state = ''
        self.__suspendFlag = False
        self.__marathonQuest = None
        self.__marathonGroup = None
        self.__urlMacros = URLMarcos()
        self.__baseUrl = GUI_SETTINGS.lookup('marathonUrl')
        self.__eventManager = Event.EventManager()
        self.onFlagUpdateNotify = Event.Event(self.__eventManager)
        return

    def fini(self):
        self.__stop()
        super(MarathonEventController, self).fini()

    def onLobbyStarted(self, ctx):
        super(MarathonEventController, self).onLobbyStarted(ctx)
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self._eventsCache.onProgressUpdated += self.__onSyncCompleted
        self.__onSyncCompleted()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    @prbEntityProperty
    def prbEntity(self):
        return None

    @async
    @process
    def getURL(self, callback):
        if self.__baseUrl is None:
            LOG_ERROR('Requesting URL for marathon when base URL is not specified')
            yield lambda clb: clb(False)
        else:
            url = yield self.__urlMacros.parse(self.__baseUrl)
            callback(url)
        return

    def isEnabled(self):
        return self.__isEnabled and not self._bootcamp.isInBootcamp()

    def isAvailable(self):
        return self.__isAvailable

    def getQuestsData(self, prefix=None, postfix=None):
        return self.__getProgress('quests', prefix, postfix)

    def getTokensData(self, prefix=None, postfix=None):
        return self.__getProgress('tokens', prefix, postfix)

    def getMarathonProgress(self):
        tokens = self.getTokensData(prefix=MARATHON_PREFIX, postfix=MARATHON_COMPLETED_TOKEN_POSTFIX)
        tokenPrefixLen = len('event_marathon:IM18')
        res = []
        for tokenNames in tokens.keys():
            name = str(tokenNames[tokenPrefixLen:])
            res.append(int(filter(str.isdigit, name)))

        currentStep = sorted(res)[-1] if res else 0
        return (currentStep, MARATHON_QUESTS_IN_CHAIN)

    def getState(self):
        return self.__state

    def getMarathonFlagState(self, vehicle):
        return {'flagHeaderIcon': self.__getHangarFlagHeaderIcon(),
         'flagStateIcon': self.__getHangarFlagStateIcon(vehicle),
         'tooltip': self.__getTooltip(),
         'enable': self.isAvailable(),
         'visible': self.isEnabled()}

    def checkForWarnings(self, _):
        wrongBattleType = self.prbEntity.getEntityType() != constants.ARENA_GUI_TYPE.RANDOM
        return MARATHON_WARNING.WRONG_BATTLE_TYPE if wrongBattleType else ''

    def isVehicleObtained(self):
        return self.__vehInInventory

    def getMarathonQuests(self):
        return self._eventsCache.getHiddenQuests(marathonFilterFunc)

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
            fmtText = text_styles.neutral(_ms(TOOLTIPS.TEMPLATE_DAYS_SHORT, value=str(int(groupFinishTimeLeft // ONE_DAY))))
            return fmtText

    def getMarathonDiscount(self):
        passQuests, allQuests = self.getMarathonProgress()
        return int(passQuests * 100) / allQuests if passQuests and MARATHON_QUESTS_IN_CHAIN else 0

    def __onSyncCompleted(self, *args):
        self.__checkEvents()
        self.__reloadNotification()

    def __checkEvents(self):
        self.__updateQuestsData()
        self.__setState()

    def __setState(self):
        if not self.__marathonGroup:
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
        if groupStartTimeLeft > ZERO_TIME or groupFinishTimeLeft <= ZERO_TIME:
            self.__isEnabled = False
            self.__isAvailable = False
            self.__state = MARATHON_STATE.DISABLED
            return self.__state
        if groupStartTimeLeft <= ZERO_TIME < groupFinishTimeLeft:
            self.__isEnabled = True
            self.__isAvailable = True
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
        if firstQuestStartTimeLeft > ZERO_TIME:
            self.__state = MARATHON_STATE.NOT_STARTED
        elif firstQuestStartTimeLeft <= ZERO_TIME < firstQuestFinishTimeLeft:
            self.__state = MARATHON_STATE.IN_PROGRESS
        elif firstQuestFinishTimeLeft <= ZERO_TIME < groupFinishTimeLeft:
            self.__state = MARATHON_STATE.FINISHED
        return self.__state

    def __updateQuestsData(self):
        self.__suspendFlag = False
        quests = self._eventsCache.getHiddenQuests(marathonFilterFunc)
        if quests:
            sortedIndexList = sorted(quests)
            for q in sortedIndexList:
                if MARATHON_SUSPEND in q:
                    self.__suspendFlag = True
                    break

            self.__marathonQuest = quests[sortedIndexList[0]]
        groups = self._eventsCache.getGroups(marathonFilterFunc)
        if groups:
            sortedGroups = sorted(groups)
            self.__marathonGroup = groups[sortedGroups[0]]
        tokens = self.getTokensData(prefix=MARATHON_PREFIX).keys()
        self.__vehInInventory = any((t in tokens for t in MARATHON_AWARD_TOKENS))

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

    def __getHangarFlagStateIcon(self, vehicle):
        if self.__state not in MARATHON_STATE.ENABLED_STATE:
            return ''
        if self.__vehInInventory:
            return RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_OK_ICON
        if self.__state == MARATHON_STATE.NOT_STARTED:
            return RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_TIME_ICON
        if self.__state == MARATHON_STATE.IN_PROGRESS:
            warning = self.checkForWarnings(vehicle)
            if warning:
                return RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ALERT_ICON
            _, firstQuestFinishTimeLeft = self.__getQuestTimeInterval()
            if firstQuestFinishTimeLeft > ONE_DAY:
                return RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_ICON_FLAG
            if firstQuestFinishTimeLeft <= ONE_DAY:
                return RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_TIME_ICON
        return RES_ICONS.MAPS_ICONS_LIBRARY_MARATHON_SALE_ICON if self.__state == MARATHON_STATE.FINISHED else None

    def __getTillTimeEnd(self, value):
        return self.__getFormattedTillTimeString(value, TOOLTIPS.MARATHON_STATE_END)

    def __getTillTimeStart(self, value):
        return self.__getFormattedTillTimeString(value, TOOLTIPS.MARATHON_STATE_START, extraFmt=True)

    def __getFormattedTillTimeString(self, timeValue, keyNamespace, isRoundUp=True, extraFmt=False):
        gmtime = time.gmtime(timeValue)
        if isRoundUp and gmtime.tm_sec > 0:
            timeValue += ONE_HOUR
            gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            gmtime = time.gmtime(timeValue - ONE_DAY)
            text = text_styles.stats(_ms(TOOLTIPS.TEMPLATE_DAYS_SHORT, value=str(time.struct_time(gmtime).tm_yday)))
            return text_styles.main(_ms(keyNamespace, value=text))
        if extraFmt:
            text = text_styles.stats(_ms(TOOLTIPS.TEMPLATE_HOURS_SHORT, value=str(time.struct_time(gmtime).tm_hour)))
            return text_styles.main(_ms(keyNamespace, value=text))
        text = _ms(TOOLTIPS.TEMPLATE_HOURS_SHORT, value=str(time.struct_time(gmtime).tm_hour))
        return text_styles.tutorial(_ms(keyNamespace, value=text))

    def __getTooltip(self):
        return TOOLTIPS_CONSTANTS.MARATHON_QUESTS_PREVIEW if self.isAvailable() else TOOLTIPS.MARATHON_OFF

    def __getGroupTimeInterval(self):
        return (self.__marathonGroup.getStartTimeLeft(), self.__marathonGroup.getFinishTimeLeft()) if self.__marathonGroup else (ZERO_TIME, ZERO_TIME)

    def __getQuestTimeInterval(self):
        return (self.__marathonQuest.getStartTimeLeft(), self.__marathonQuest.getFinishTimeLeft()) if self.__marathonQuest else (ZERO_TIME, ZERO_TIME)

    def __stop(self):
        self.clearNotification()
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self._eventsCache.onProgressUpdated -= self.__onSyncCompleted

    def __getClosestStatusUpdateTime(self):
        if self.__state == MARATHON_STATE.NOT_STARTED:
            timeLeft, _ = self.__getQuestTimeInterval()
            return timeLeft + 1
        if self.__state == MARATHON_STATE.IN_PROGRESS:
            _, timeLeft = self.__getQuestTimeInterval()
            return timeLeft + 1
        if self.__state == MARATHON_STATE.FINISHED:
            _, timeLeft = self.__getGroupTimeInterval()
            return timeLeft

    def __updateFlagState(self):
        self.__checkEvents()
        self.onFlagUpdateNotify()

    def __reloadNotification(self):
        self.clearNotification()
        timePeriod = self.__getClosestStatusUpdateTime()
        if timePeriod:
            self.addNotificator(PeriodicNotifier(self.__getClosestStatusUpdateTime, self.__updateFlagState))
            self.startNotification()
