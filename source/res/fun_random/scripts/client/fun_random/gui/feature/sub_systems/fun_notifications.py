# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_notifications.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import FUN_RANDOM_NOTIFICATIONS
from fun_random.gui.feature.fun_constants import FunNotificationSubModeState, FunTimersShifts
from fun_random.gui.feature.models.notifications import FunNotificationCtx, FunNotification, FunStopSubModesNotification, FunNewSubModesNotification, FunNewProgressionNotification, FunSwitchOnSubModesNotification, FunSwitchOffSubModesNotification
from fun_random.gui.feature.util.fun_wrappers import ifNotificationsAllowed, ifNotificationsEnabled, skipNoSubModesAction
from gui.impl.gen import R
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IFunRandomController, IBootcampController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from fun_random.helpers.server_settings import FunRandomConfig

def _modeSelectorPredicate(view):
    return view.layoutID == R.views.lobby.mode_selector.ModeSelectorView()


_NOTIFICATIONS_AGGREGATORS = (FunStopSubModesNotification, FunNewSubModesNotification)
_NOTIFICATIONS_BUILDERS = (FunStopSubModesNotification,
 FunNewSubModesNotification,
 FunNewProgressionNotification,
 FunSwitchOnSubModesNotification,
 FunSwitchOffSubModesNotification)

def _defineSubModeState(subMode, now):
    if not subMode.hasAnySeason():
        return FunNotificationSubModeState.UNDEFINED
    elif subMode.getCurrentSeason(now) is None:
        if subMode.getNextSeason(now) is None:
            return FunNotificationSubModeState.AFTER_SEASON
        if subMode.getPreviousSeason(now) is None:
            return FunNotificationSubModeState.BEFORE_SEASON
        return FunNotificationSubModeState.BETWEEN_SEASONS
    else:
        return FunNotificationSubModeState.FROZEN if subMode.isFrozen() else FunNotificationSubModeState.AVAILABLE


class FunNotifications(IFunRandomController.IFunNotifications, Notifiable):
    __gui = dependency.descriptor(IGuiLoader)
    __bootcampCtrl = dependency.descriptor(IBootcampController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, progressions, subModesHolder):
        super(FunNotifications, self).__init__()
        self.__isNotificationsAllowed = False
        self.__notificationsQueue = []
        self.__subModesStates = {}
        self.__funRandomSettings = None
        self.__progressions = progressions
        self.__subModes = subModesHolder
        self.addNotificator(SimpleNotifier(self.__getNotificationsTimer, self.__processNotifications))
        return

    def fini(self):
        self.clearNotification()
        self.__progressions = self.__subModes = None
        return

    def clear(self):
        self.__clearNotificationsQueue()
        self.__subModesStates.clear()

    def isNotificationsAllowed(self):
        return self.__isNotificationsAllowed

    def isNotificationsEnabled(self):
        isFunRandomEnabled = self.__funRandomSettings and self.__funRandomSettings.isEnabled
        return isFunRandomEnabled and not self.__bootcampCtrl.isInBootcamp()

    def addToQueue(self, notification):
        self.__notificationsQueue.append(notification)

    @skipNoSubModesAction
    def markSeenAsFrozen(self, subModesIDs):
        settings = AccountSettings.getNotifications(FUN_RANDOM_NOTIFICATIONS)
        FunNotification.updateStoredSubModes(self.__subModes, subModesIDs, settings, isFrozen=True)
        AccountSettings.setNotifications(FUN_RANDOM_NOTIFICATIONS, settings)

    @ifNotificationsEnabled
    @ifNotificationsAllowed(useQueue=True)
    def pushNotification(self, notification):
        self.__pushNotification(notification)

    def startNotificationPushing(self):
        self.__processNotifications()
        self.__isNotificationsAllowed = True
        self.__processNotificationsQueue()
        self.startNotification()

    def stopNotificationPushing(self):
        self.__isNotificationsAllowed = False
        self.stopNotification()

    def updateSettings(self, settings):
        self.__funRandomSettings = settings
        self.__processNotifications()

    def __isModeSelectorOpen(self):
        return bool(self.__gui.windowsManager.findViews(_modeSelectorPredicate))

    def __getNotificationsTimer(self):
        subModesTimestamps = (subMode.getClosestStateChangeTime() for subMode in self.__subModes.getSubModes())
        subModesTimers = tuple((time_utils.getTimeDeltaFromNowInLocal(timestamp) for timestamp in subModesTimestamps))
        timers = tuple((timer for timer in subModesTimers + (self.__progressions.getProgressionTimer(),) if timer > 0))
        return min(timers) + FunTimersShifts.NOTIFICATIONS if timers else 0

    def __clearNotificationsQueue(self):
        del self.__notificationsQueue[:]

    def __defineSubModesStates(self):
        now = time_utils.getCurrentTimestamp()
        return {subMode.getSubModeID():_defineSubModeState(subMode, now) for subMode in self.__subModes.getSubModes()}

    def __processNotifications(self):
        prevStates, newStates = self.__subModesStates, self.__defineSubModesStates()
        allSubModesIDs = set.union(set(prevStates.keys()), set(newStates.keys()))
        transactions = ((sID, prevStates.get(sID), newStates.get(sID)) for sID in allSubModesIDs)
        transactions = tuple(((sID, pState or FunNotificationSubModeState.UNDEFINED, nState or FunNotificationSubModeState.UNDEFINED) for sID, pState, nState in transactions if pState != nState))
        ctx = FunNotificationCtx(self.__isModeSelectorOpen() or self.__subModes.getDesiredSubMode(), self.__subModes, self.__progressions.getActiveProgression(), transactions, newStates, AccountSettings.getNotifications(FUN_RANDOM_NOTIFICATIONS))
        notifications = []
        for builder in _NOTIFICATIONS_BUILDERS:
            notifications.extend(builder.buildNotifications(ctx))

        for notification in notifications:
            self.pushNotification(notification)

        AccountSettings.setNotifications(FUN_RANDOM_NOTIFICATIONS, ctx.settings)
        self.__subModesStates = newStates

    def __processNotificationsQueue(self):
        aggregatedNotifications = self.__notificationsQueue[:]
        for aggregator in _NOTIFICATIONS_AGGREGATORS:
            aggregatedNotifications = aggregator.aggregateNotifications(aggregatedNotifications)

        for notification in aggregatedNotifications:
            self.__pushNotification(notification)

        self.__clearNotificationsQueue()

    @ifNotificationsEnabled
    @ifNotificationsAllowed(useQueue=False)
    def __pushNotification(self, notification):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(notification, SCH_CLIENT_MSG_TYPE.FUN_RANDOM_NOTIFICATIONS)
