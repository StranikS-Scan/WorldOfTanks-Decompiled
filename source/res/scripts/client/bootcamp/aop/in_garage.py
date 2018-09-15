# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/in_garage.py
""" AOP classes for altering some common logic according to Bootcamp's requirements.

    This module should contain aspects and pointcuts which
    must only be active while in bootcamp hangar (StateInGarage).
"""
from helpers import aop, getClientLanguage
from helpers.i18n import makeString
from gui import makeHtmlString
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem
from gui.Scaleform.daapi.view.dialogs.SystemMessageMeta import SESSION_CONTROL_TYPE, SessionControlAuxData
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control.AOGAS import AOGAS_NOTIFY_PERIOD
from gui.game_control.GameSessionController import GameSessionController
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from constants import PREBATTLE_TYPE_NAMES
from bootcamp.aop import common
_MS_IN_SEC = 1000
_SET_OPTIONAL_DEVICE_LESSON_NUM = 4

def weave(weaver, stateInGarage):
    """ Activates all pointcuts which must be always active in bootcamp hangar.
    :param weaver: AOP weaver to use for scoping
    :param stateInGarage: instance of class bootcamp.states.StateInGarage
    """
    weaver.weave(pointcut=_PointcutBrowserControllerDisable)
    weaver.weave(pointcut=_PointcutPrbDisableEntitySelect)
    weaver.weave(pointcut=_PointcutPrbInvitationText)
    weaver.weave(pointcut=_PointcutPrbDisableAcceptButton)
    weaver.weave(pointcut=_PointcutSysMessagesClient, avoid=True)
    weaver.weave(pointcut=_PointcutSysMessagesServer, avoid=True)
    weaver.weave(pointcut=_PointcutUnreadMessages)
    weaver.weave(pointcut=_PointcutFriendRequest, avoid=True)
    weaver.weave(pointcut=_PointcutShowModuleInfo, avoid=True)
    from bootcamp.Bootcamp import g_bootcamp
    if not g_bootcamp.isResearchFreeLesson():
        weaver.weave(pointcut=_PointcutNoFittingPopover, avoid=True)
        weaver.weave(pointcut=_PointcutDisableModuleClickSound)
    if g_bootcamp.getLessonNum() == _SET_OPTIONAL_DEVICE_LESSON_NUM:
        weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverDestroy)
        weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverSetModule)
    weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverGetTabData())
    weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverGetInitialTabIndex())
    weaver.weave(pointcut=_PointcutOverrideAOGASMessageTimeout)
    if getClientLanguage() == 'ko':
        weaver.weave(pointcut=_PointcutOverrideKoreaParentalControl)
    weaver.weave(pointcut=_PointcutDisableRankedBattleEvents)
    weaver.weave(pointcut=_PointcutDisableNewYearEventAvailability)
    weaver.weave(pointcut=_PointcutDisableNewYearEvent)
    weaver.weave(pointcut=_PointcutDisableNewYearStateUpdating)


class PointcutBattleSelectorHintText(aop.Pointcut):
    """ Forces "select battle mode" text in battle mode selector GUI.
        Should be activated / deactivated manually as necessary, not active across the whole Bootcamp hangar!
    """

    def __init__(self):
        super(PointcutBattleSelectorHintText, self).__init__('gui.Scaleform.daapi.view.lobby.header.battle_selector_items', '_BattleSelectorItems', 'update', aspects=(_AspectBattleSelectorHintText,))


class _PointcutBrowserControllerDisable(aop.Pointcut):
    """ Disables in-game browser. """

    def __init__(self):
        super(_PointcutBrowserControllerDisable, self).__init__('gui.game_control.BrowserController', 'BrowserController', 'load', aspects=(common.AspectAvoidAsync(),))


class _PointcutPrbDisableEntitySelect(aop.Pointcut):
    """ Disables actual switch to "random battle" mode,
        which the player has to select in the last Bootcamp lesson.
    """

    def __init__(self):
        super(_PointcutPrbDisableEntitySelect, self).__init__('gui.prb_control.entities.bootcamp.pre_queue.entity', 'BootcampEntity', 'doSelectAction', aspects=(common.AspectAvoidWithConstantRet(SelectResult(True)),))


class _PointcutPrbDisableAcceptButton(aop.Pointcut):
    """ Prohibits accepting invitations to any external prebattle entities from inside Bootcamp. """

    def __init__(self):
        super(_PointcutPrbDisableAcceptButton, self).__init__('gui.prb_control.invites', 'InvitesManager', 'canAcceptInvite', aspects=(common.AspectAvoidWithConstantRet(False),))


class _PointcutPrbInvitationText(aop.Pointcut):
    """ Disables invitation messages for any external prebattle entities while in Bootcamp. """

    def __init__(self):
        super(_PointcutPrbInvitationText, self).__init__('gui.prb_control.formatters.invites', 'PrbInviteHtmlTextFormatter', 'getNote', aspects=(_AspectPrbInvitationNote,))


class _PointcutOnOptionalDeviceSelectPopoverGetTabData(aop.Pointcut):
    """ Removes "Deluxe" tab from optional device selection popover. """

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverGetTabData, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', 'OptionalDeviceSelectPopover', '_getTabsData', aspects=(_AspectOnOptionalDeviceSelectPopoverGetTabData,))


class _PointcutOnOptionalDeviceSelectPopoverGetInitialTabIndex(aop.Pointcut):
    """ Selects tab #0 in optional device selection popover. """

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverGetInitialTabIndex, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', 'OptionalDeviceSelectPopover', '_getInitialTabIndex', aspects=(common.AspectAvoidWithConstantRet(0),))


class _PointcutOnOptionalDeviceSelectPopoverDestroy(aop.Pointcut):
    """ Prevents optional device selection popover from closing when bootcamp tutorial message window closes.
        Also makes sure that correct hint is restored when this popover is closed without selecting anything.
    """

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverDestroy, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', 'OptionalDeviceSelectPopover', 'destroy', aspects=(_AspectOnOptionalDeviceSelectPopoverDestroy,))


class _PointcutOnOptionalDeviceSelectPopoverSetModule(aop.Pointcut):
    """ Handles continuation of the Bootcamp flow after selecting an optional device. """

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverSetModule, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', '_BootCampLogicProvider', 'setModule', aspects=(_AspectOnOptionalDeviceSelectPopoverSetModule,))


class _PointcutNoFittingPopover(aop.Pointcut):
    """ Disables showing of selection popovers when clicking vehicle module buttons.
        Should be paired with _PointcutDisableModuleClickSound which disables the corresponding GUI sounds.
    """

    def __init__(self):
        super(_PointcutNoFittingPopover, self).__init__('gui.Scaleform.managers.PopoverManager', 'PopoverManager', 'fireEvent')


class _PointcutDisableModuleClickSound(aop.Pointcut):
    """ Disables click and hover sound effects for vehicle module buttons.
        Should be paired with _PointcutNoFittingPopover which disables the corresponding click functionality.
    """

    def __init__(self):
        super(_PointcutDisableModuleClickSound, self).__init__('gui.Scaleform.managers.SoundManager', 'SoundManager', 'playControlSound', aspects=(common.AspectDisableControlSound(('press', 'over'), ('ammunitionModule',)),))


class _PointcutSysMessagesClient(aop.Pointcut):
    """ Disables client system message notifications. """

    def __init__(self):
        super(_PointcutSysMessagesClient, self).__init__('gui.Scaleform.SystemMessagesInterface', 'SystemMessagesInterface', '^pushMessage$')


class _PointcutSysMessagesServer(aop.Pointcut):
    """ Disables server system message notifications. """

    def __init__(self):
        super(_PointcutSysMessagesServer, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', '^onReceive(Personal)?SysMessage$')


class _PointcutUnreadMessages(aop.Pointcut):
    """ Disables handling of most unread messages (that is, any except the ones we explicitly want to show).
        This is necessary because they can arrive while at a time when other blocking pointcuts are not yet active.
    """

    def __init__(self):
        super(_PointcutUnreadMessages, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', '^_handleUnreadMessage$', aspects=(_AspectUnreadMessages,))


class _PointcutFriendRequest(aop.Pointcut):
    """ Disables friend request notifications. """

    def __init__(self):
        super(_PointcutFriendRequest, self).__init__('notification.listeners', 'FriendshipRqsListener', '^(start|stop)$')


class _PointcutShowModuleInfo(aop.Pointcut):
    """ Disables showing vehicle module info in GUI. """

    def __init__(self):
        super(_PointcutShowModuleInfo, self).__init__('gui.shared', 'event_dispatcher', 'showModuleInfo')


class _PointcutOverrideAOGASMessageTimeout(aop.Pointcut):
    """ Overrides auto-closing timeout of AOGAS messages while in Bootcamp,
        because there is no notification center to review them.
    """

    def __init__(self):
        super(_PointcutOverrideAOGASMessageTimeout, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', 'pushClientMessage', aspects=(_AspectOverrideAOGASMessageTimeout,))


class _PointcutOverrideKoreaParentalControl(aop.Pointcut):
    """ Forces Korea parental control messages to be alerts (display as dialog that should be closed manually,
        because Bootcamp hangar doesn't have a notification center to review missed messages.
        Also sets a timeout to prevent indefinite accumulation of such messages in queue.
    """

    def __init__(self):
        super(_PointcutOverrideKoreaParentalControl, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', 'pushClientMessage', aspects=(_AspectOverrideKoreaParentalControl,))


class _PointcutDisableRankedBattleEvents(aop.Pointcut):
    """ Forces bootcamp to ignore ranked battle events from server. See WOTD-92296. """

    def __init__(self):
        super(_PointcutDisableRankedBattleEvents, self).__init__('gui.game_control.ranked_battles_controller', 'RankedBattlesController', 'isAvailable', aspects=(common.AspectAvoidWithConstantRet(False),))


class _PointcutDisableNewYearEventAvailability(aop.Pointcut):
    """ Forces bootcamp to ignore new year event. See WOTD-95729 """

    def __init__(self):
        super(_PointcutDisableNewYearEventAvailability, self).__init__('new_year.new_year_controller', 'NewYearController', 'isAvailable', aspects=(common.AspectAvoidWithConstantRet(False),))


class _PointcutDisableNewYearEvent(aop.Pointcut):
    """ Forces bootcamp to ignore new year event. See WOTD-95729 """

    def __init__(self):
        super(_PointcutDisableNewYearEvent, self).__init__('new_year.new_year_controller', 'NewYearController', 'isEnabled', aspects=(common.AspectAvoidWithConstantRet(False),))


class _PointcutDisableNewYearStateUpdating(aop.Pointcut):
    """ Forces bootcamp to ignore new year event. See WOTD-95729 """

    def __init__(self):
        super(_PointcutDisableNewYearStateUpdating, self).__init__('new_year.new_year_controller', 'NewYearController', '_updateState', aspects=(common.AspectAvoidWithConstantRet(False),))


class _AspectPrbInvitationNote(aop.Aspect):
    """ Aspect for _PointcutPrbInvitationText implementation. """

    def atCall(self, cd):
        cd.avoid()
        battle_type = PREBATTLE_TYPE_NAMES[cd.args[0].type]
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': makeString('#bootcamp:invitation/note/{0}'.format(battle_type))})


class _AspectOnOptionalDeviceSelectPopoverDestroy(aop.Aspect):
    """ Aspect for _PointcutOnOptionalDeviceSelectPopoverDestroy implementation. """

    def atCall(self, cd):
        manager = cd.self.app.containerManager
        container = manager.getContainer(ViewTypes.WINDOW)
        window = None
        if container:
            window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW})
        if window:
            cd.avoid()
        else:
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.runViewAlias('hangar')
        return


class _AspectOnOptionalDeviceSelectPopoverSetModule(aop.Aspect):
    """ Aspect for _PointcutOnOptionalDeviceSelectPopoverSetModule implementation. """

    def atReturn(self, cd):
        isRemove = cd.findArg(2, 'isRemove')
        if cd.self._slotType == FITTING_TYPES.OPTIONAL_DEVICE and not isRemove:
            from bootcamp.BootcampGarage import g_bootcampGarage
            g_bootcampGarage.runCustomAction('showElementsLessonV_Step1')


class _AspectOnOptionalDeviceSelectPopoverGetTabData(aop.Aspect):
    """ Aspect for _PointcutOnOptionalDeviceSelectPopoverGetTabData implementation. """

    def atReturn(self, cd):
        tabData = cd.returned.get('tabData', None)
        if tabData and len(tabData) > 1:
            cd.returned['tabData'] = tabData[:1]
        return


class _AspectBattleSelectorHintText(aop.Aspect):
    """ Aspect for PointcutBattleSelectorHintText implementation. """

    def atCall(self, cd):
        cd.avoid()
        return _BattleSelectorHint(BOOTCAMP.GAME_MODE, PREBATTLE_ACTION_NAME.BOOTCAMP, 0)


class _AspectUnreadMessages(aop.Aspect):
    """ Aspect for _PointcutUnreadMessages implementation.
        Blocks all messages except the ones from AOGAS or Korea parental control.
    """

    def atCall(self, cd):
        settings = cd.findArg(3, 'settings')
        if settings is not None and isinstance(settings.auxData, SessionControlAuxData):
            return
        else:
            cd.avoid()
            return


class _AspectOverrideAOGASMessageTimeout(aop.Aspect):
    """ Aspect for _PointcutOverrideAOGASMessageTimeout implementation.
    
        Timeouts are overridden to make sure that at least one AOGAS message
        always stays on screen until the player reads and closes it.
    
        At the same time, we don't want to simply disable the timeout,
        as this could potentially lead to an extremely long queue of mostly identical messages,
        which the player would then have to close one by one
        (e.g. if they've been AFK in Bootcamp for several hours past the AOGAS limit).
    """
    NEXT_NOTIFICATION_PERIOD_SEC = {'AOND_1': AOGAS_NOTIFY_PERIOD.AOND_2_3,
     'AOND_2': AOGAS_NOTIFY_PERIOD.AOND_2_3,
     'AOND_3': None,
     'AOND_MORE_3': AOGAS_NOTIFY_PERIOD.AOND_3_5,
     'AOND_MORE_5': AOGAS_NOTIFY_PERIOD.AOND_END,
     'RESET': AOGAS_NOTIFY_PERIOD.AOND_START}

    def atCall(self, cd):
        auxData = cd.findArg(3, 'auxData')
        if not isinstance(auxData, SessionControlAuxData):
            return
        elif auxData.type != SESSION_CONTROL_TYPE.AOGAS:
            return
        else:
            message = cd.findArg(0, 'message')
            newTimeout = self.NEXT_NOTIFICATION_PERIOD_SEC.get(message.name())
            if newTimeout is None:
                return
            newTimeout *= _MS_IN_SEC
            return cd.changeArgs((3, 'auxData', SessionControlAuxData(auxData.type, newTimeout)))


class _AspectOverrideKoreaParentalControl(aop.Aspect):
    """ Aspect for _PointcutOverrideKoreaParentalControl implementation.
    
        Logic and rationale is similar to _AspectOverrideAOGASMessageTimeout,
        but here we also have to force the message to become an alert.
    
    """

    def atCall(self, cd):
        auxData = cd.findArg(3, 'auxData')
        if not isinstance(auxData, SessionControlAuxData):
            return
        if auxData.type != SESSION_CONTROL_TYPE.KOREA_PARENTAL_CONTROL:
            return
        newTimeout = GameSessionController.NOTIFY_PERIOD * _MS_IN_SEC
        return cd.changeArgs((2, 'isAlert', True), (3, 'auxData', SessionControlAuxData(auxData.type, newTimeout)))


class _BattleSelectorHint(_SelectorItem):

    def getSmallIcon(self):
        return RES_ICONS.MAPS_ICONS_BOOTCAMP_EMPTYBATTLESELECTORICON

    def isSelectorBtnEnabled(self):
        return True
