# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/models/notifications.py
import typing
from account_helpers.AccountSettings import FUN_RANDOM_NOTIFICATIONS_FROZEN, FUN_RANDOM_NOTIFICATIONS_SUB_MODES, FUN_RANDOM_NOTIFICATIONS_PROGRESSIONS
from fun_random.gui.feature.fun_constants import FunNotificationSubModeState, FunNotificationType
from gui.shared.utils.decorators import ReprInjector
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.models.progressions import FunProgression
    from skeletons.gui.game_control import IFunRandomController

class FunNotificationCtx(object):
    __slots__ = ('isInFunRandom', 'subModes', 'progression', 'transactions', 'newStates', 'settings')

    def __init__(self, isInFunRandom, subModes, progression, transactions, newStates, settings):
        self.isInFunRandom = isInFunRandom
        self.progression, self.subModes = progression, subModes
        self.transactions, self.newStates = transactions, newStates
        self.settings = settings


@ReprInjector.simple(('notificationType', 'notificationType'))
class FunNotification(object):
    __slots__ = ('notificationType',)

    def __init__(self, notificationType):
        self.notificationType = notificationType

    @classmethod
    def aggregateNotifications(cls, notifications):
        return notifications

    @classmethod
    def buildNotifications(cls, ctx):
        return []

    @classmethod
    def updateStoredSubModes(cls, subModes, subModesIDs, settings, isRemove=False, isFrozen=False):
        updater = set.difference_update if isRemove else set.update
        key = FUN_RANDOM_NOTIFICATIONS_FROZEN if isFrozen else FUN_RANDOM_NOTIFICATIONS_SUB_MODES
        updater(settings[key], cls._getSettingsKeys(subModes, subModesIDs))

    @classmethod
    def _isNewProgression(cls, ctx):
        progression, seen = ctx.progression, ctx.settings[FUN_RANDOM_NOTIFICATIONS_PROGRESSIONS]
        return bool(progression and progression.isNotifiable and progression.config.name not in seen)

    @classmethod
    def _getSettingsKeys(cls, subModes, subModesIDs):
        subModesObjects = (subModes.getSubMode(subModeID) for subModeID in subModesIDs)
        return (sm.getSettings().client.settingsKey for sm in subModesObjects if sm)

    @classmethod
    def _markProgressionAsSeen(cls, progression, settings):
        settings[FUN_RANDOM_NOTIFICATIONS_PROGRESSIONS].add(progression.config.name if progression else '')


@ReprInjector.withParent(('subModesIDs', 'subModesIDs'), ('isNewProgression', 'isNewProgression'))
class FunStopSubModesNotification(FunNotification):
    __slots__ = ('subModesIDs', 'isNewProgression')
    _FINISH_STATES = (FunNotificationSubModeState.BETWEEN_SEASONS, FunNotificationSubModeState.AFTER_SEASON)
    _STOP_NOTIFICATIONS = (FunNotificationType.STOP_SUB_MODES, FunNotificationType.STOP_ALL_SUB_MODES)
    _PROGRESSION_NOTIFICATION = FunNotificationType.NEW_PROGRESSION

    def __init__(self, notificationType, subModesIDs=(), isNewProgression=False):
        super(FunStopSubModesNotification, self).__init__(notificationType)
        self.isNewProgression = isNewProgression
        self.subModesIDs = subModesIDs

    @classmethod
    def aggregateNotifications(cls, notifications):
        stopNotifications = tuple((n for n in notifications if n.notificationType in cls._STOP_NOTIFICATIONS))
        if not stopNotifications:
            return notifications
        excludeProgression = tuple((n for n in notifications if n.notificationType != cls._PROGRESSION_NOTIFICATION))
        if len(excludeProgression) != len(notifications):
            stopNotifications[0].isNewProgression = True
            notifications = excludeProgression
        return notifications

    @classmethod
    def buildNotifications(cls, ctx):
        notifications = []
        if not ctx.isInFunRandom:
            return notifications
        finishSubModesIDs = tuple((sID for sID, pState, nState in ctx.transactions if pState == FunNotificationSubModeState.AVAILABLE and nState in cls._FINISH_STATES))
        if finishSubModesIDs:
            notificationType = FunNotificationType.STOP_SUB_MODES
            if all((state == FunNotificationSubModeState.AFTER_SEASON for state in ctx.newStates.itervalues())):
                notificationType = FunNotificationType.STOP_ALL_SUB_MODES
            notifications.append(cls(notificationType, finishSubModesIDs, cls._isNewProgression(ctx)))
            cls._markProgressionAsSeen(ctx.progression, ctx.settings)
        return notifications


@ReprInjector.withParent(('subModesIDs', 'subModesIDs'), ('isNewProgression', 'isNewProgression'))
class FunNewSubModesNotification(FunNotification):
    __slots__ = ('subModesIDs', 'isNewProgression')
    _PROGRESSION_NOTIFICATION = FunNotificationType.NEW_PROGRESSION
    _NEW_STATES = (FunNotificationSubModeState.AVAILABLE, FunNotificationSubModeState.FROZEN)
    _NEW_NOTIFICATION = FunNotificationType.NEW_SUB_MODES

    def __init__(self, notificationType, subModesIDs=(), isNewProgression=False):
        super(FunNewSubModesNotification, self).__init__(notificationType)
        self.isNewProgression = isNewProgression
        self.subModesIDs = subModesIDs

    @classmethod
    def aggregateNotifications(cls, notifications):
        newNotifications = tuple((n for n in notifications if n.notificationType == cls._NEW_NOTIFICATION))
        if not newNotifications:
            return notifications
        excludeProgression = tuple((n for n in notifications if n.notificationType != cls._PROGRESSION_NOTIFICATION))
        if len(excludeProgression) != len(notifications):
            newNotifications[0].isNewProgression = True
            notifications = excludeProgression
        return notifications

    @classmethod
    def buildNotifications(cls, ctx):
        availableIDs = tuple((sID for sID, _, nState in ctx.transactions if nState in cls._NEW_STATES))
        newSubModesIDs = tuple((sID for sID, sKey in zip(availableIDs, cls._getSettingsKeys(ctx.subModes, availableIDs)) if sKey not in ctx.settings[FUN_RANDOM_NOTIFICATIONS_SUB_MODES]))
        notifications = []
        if newSubModesIDs:
            notifications.append(cls(FunNotificationType.NEW_SUB_MODES, newSubModesIDs, cls._isNewProgression(ctx)))
            cls.updateStoredSubModes(ctx.subModes, newSubModesIDs, ctx.settings)
            cls._markProgressionAsSeen(ctx.progression, ctx.settings)
        return notifications


class FunNewProgressionNotification(FunNotification):

    @classmethod
    def buildNotifications(cls, ctx):
        notifications = []
        if ctx.progression is None or not cls._isNewProgression(ctx):
            return notifications
        else:
            notifications.append(cls(FunNotificationType.NEW_PROGRESSION))
            cls._markProgressionAsSeen(ctx.progression, ctx.settings)
            return notifications


@ReprInjector.withParent(('subModesIDs', 'subModesIDs'))
class FunSwitchOnSubModesNotification(FunNotification):
    __slots__ = ('subModesIDs',)
    _AVAILABLE_STATE = FunNotificationSubModeState.AVAILABLE

    def __init__(self, notificationType, subModesIDs=()):
        super(FunSwitchOnSubModesNotification, self).__init__(notificationType)
        self.subModesIDs = subModesIDs

    @classmethod
    def buildNotifications(cls, ctx):
        availableIDs = tuple((sID for sID, _, nState in ctx.transactions if nState == cls._AVAILABLE_STATE))
        unfrozenSubModesIDs = tuple((sID for sID, sKey in zip(availableIDs, cls._getSettingsKeys(ctx.subModes, availableIDs)) if sKey in ctx.settings[FUN_RANDOM_NOTIFICATIONS_FROZEN]))
        notifications = []
        if unfrozenSubModesIDs:
            notifications.append(cls(FunNotificationType.SWITCH_ON_SUB_MODES, unfrozenSubModesIDs))
            cls.updateStoredSubModes(ctx.subModes, unfrozenSubModesIDs, ctx.settings, isRemove=True, isFrozen=True)
        return notifications


@ReprInjector.withParent(('subModesIDs', 'subModesIDs'))
class FunSwitchOffSubModesNotification(FunNotification):
    __slots__ = ('subModesIDs',)
    _AVAILABLE_STATE = FunNotificationSubModeState.AVAILABLE
    _FROZEN_STATE = FunNotificationSubModeState.FROZEN

    def __init__(self, notificationType, subModesIDs=()):
        super(FunSwitchOffSubModesNotification, self).__init__(notificationType)
        self.subModesIDs = subModesIDs

    @classmethod
    def buildNotifications(cls, ctx):
        notifications = []
        if not ctx.isInFunRandom:
            return notifications
        frozenSubModesIDs = tuple((sID for sID, pState, nState in ctx.transactions if pState == cls._AVAILABLE_STATE and nState == cls._FROZEN_STATE))
        if frozenSubModesIDs:
            notifications.append(cls(FunNotificationType.SWITCH_OFF_SUB_MODES, frozenSubModesIDs))
            cls.updateStoredSubModes(ctx.subModes, frozenSubModesIDs, ctx.settings, isFrozen=True)
        return notifications
