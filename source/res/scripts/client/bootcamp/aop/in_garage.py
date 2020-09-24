# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/aop/in_garage.py
from frameworks.wulf import WindowLayer
from helpers import aop, getClientLanguage
from helpers.i18n import makeString
from gui import makeHtmlString
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.battle_selector_item import SelectorItem
from gui.Scaleform.daapi.view.dialogs.SystemMessageMeta import SESSION_CONTROL_TYPE, SessionControlAuxData
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control.AOGAS import AOGAS_NOTIFY_PERIOD
from gui.game_control.GameSessionController import GameSessionController
from constants import PREBATTLE_TYPE_NAMES
from bootcamp.aop import common
from soft_exception import SoftException
_MS_IN_SEC = 1000
_BC_MESSAGE_VIEW_TYPE = WindowLayer.TOP_WINDOW

def weave(weaver, stateInGarage):
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
    weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverGetTabData)
    weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverGetInitialTabIndex)
    weaver.weave(pointcut=_PointcutOnOptionalDeviceSelectPopoverPreventCloseAfterMessage)
    weaver.weave(pointcut=_PointcutOverrideAOGASMessageTimeout)
    if getClientLanguage() == 'ko':
        weaver.weave(pointcut=_PointcutOverrideKoreaParentalControl)
    weaver.weave(pointcut=_PointcutDisableRankedBattleEvents)


class PointcutBattleSelectorHintText(aop.Pointcut):

    def __init__(self):
        super(PointcutBattleSelectorHintText, self).__init__('gui.Scaleform.daapi.view.lobby.header.battle_selector_items', '_BattleSelectorItems', 'update', aspects=(_AspectBattleSelectorHintText,))


class _PointcutBrowserControllerDisable(aop.Pointcut):

    def __init__(self):
        super(_PointcutBrowserControllerDisable, self).__init__('gui.game_control.BrowserController', 'BrowserController', 'load', aspects=(common.AspectAvoidAsync(),))


class _PointcutPrbDisableEntitySelect(aop.Pointcut):

    def __init__(self):
        super(_PointcutPrbDisableEntitySelect, self).__init__('gui.prb_control.entities.bootcamp.pre_queue.entity', 'BootcampEntity', 'doSelectAction', aspects=(common.AspectAvoidWithConstantRet(SelectResult(True)),))


class _PointcutPrbDisableAcceptButton(aop.Pointcut):

    def __init__(self):
        super(_PointcutPrbDisableAcceptButton, self).__init__('gui.prb_control.invites', 'InvitesManager', 'canAcceptInvite', aspects=(common.AspectAvoidWithConstantRet(False),))


class _PointcutPrbInvitationText(aop.Pointcut):

    def __init__(self):
        super(_PointcutPrbInvitationText, self).__init__('gui.prb_control.formatters.invites', 'PrbInviteHtmlTextFormatter', 'getNote', aspects=(_AspectPrbInvitationNote,))


class _PointcutOnOptionalDeviceSelectPopoverGetTabData(aop.Pointcut):

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverGetTabData, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', 'OptionalDeviceSelectPopover', '_getTabsData', aspects=(_AspectOnOptionalDeviceSelectPopoverGetTabData,))


class _PointcutOnOptionalDeviceSelectPopoverGetInitialTabIndex(aop.Pointcut):

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverGetInitialTabIndex, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', 'OptionalDeviceSelectPopover', '_getInitialTabIndex', aspects=(common.AspectAvoidWithConstantRet(0),))


class _PointcutOnOptionalDeviceSelectPopoverPreventCloseAfterMessage(aop.Pointcut):

    def __init__(self):
        super(_PointcutOnOptionalDeviceSelectPopoverPreventCloseAfterMessage, self).__init__('gui.Scaleform.daapi.view.lobby.shared.fitting_select_popover', 'OptionalDeviceSelectPopover', 'destroy', aspects=(_AspectOnOptionalDeviceSelectPopoverPreventCloseAfterMessage,))


class _PointcutNoFittingPopover(aop.Pointcut):

    def __init__(self):
        super(_PointcutNoFittingPopover, self).__init__('gui.Scaleform.managers.PopoverManager', 'PopoverManager', 'fireEvent')


class _PointcutDisableModuleClickSound(aop.Pointcut):

    def __init__(self):
        super(_PointcutDisableModuleClickSound, self).__init__('gui.Scaleform.managers.SoundManager', 'SoundManager', 'playControlSound', aspects=(common.AspectDisableControlSound(('press', 'over'), ('ammunitionModule',)),))


class _PointcutSysMessagesClient(aop.Pointcut):

    def __init__(self):
        super(_PointcutSysMessagesClient, self).__init__('gui.Scaleform.SystemMessagesInterface', 'SystemMessagesInterface', '^pushMessage$')


class _PointcutSysMessagesServer(aop.Pointcut):

    def __init__(self):
        super(_PointcutSysMessagesServer, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', '^onReceive(Personal)?SysMessage$')


class _PointcutUnreadMessages(aop.Pointcut):

    def __init__(self):
        super(_PointcutUnreadMessages, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', '^_handleUnreadMessage$', aspects=(_AspectUnreadMessages,))


class _PointcutFriendRequest(aop.Pointcut):

    def __init__(self):
        super(_PointcutFriendRequest, self).__init__('notification.listeners', 'FriendshipRqsListener', '^(start|stop)$')


class _PointcutShowModuleInfo(aop.Pointcut):

    def __init__(self):
        super(_PointcutShowModuleInfo, self).__init__('gui.shared', 'event_dispatcher', 'showModuleInfo')


class _PointcutOverrideAOGASMessageTimeout(aop.Pointcut):

    def __init__(self):
        super(_PointcutOverrideAOGASMessageTimeout, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', 'pushClientMessage', aspects=(_AspectOverrideAOGASMessageTimeout,))


class _PointcutOverrideKoreaParentalControl(aop.Pointcut):

    def __init__(self):
        super(_PointcutOverrideKoreaParentalControl, self).__init__('messenger.proto.bw.ServiceChannelManager', 'ServiceChannelManager', 'pushClientMessage', aspects=(_AspectOverrideKoreaParentalControl,))


class _PointcutDisableRankedBattleEvents(aop.Pointcut):

    def __init__(self):
        super(_PointcutDisableRankedBattleEvents, self).__init__('gui.game_control.ranked_battles_controller', 'RankedBattlesController', 'isAvailable', aspects=(common.AspectAvoidWithConstantRet(False),))


class _AspectPrbInvitationNote(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        battle_type = PREBATTLE_TYPE_NAMES[cd.args[0].type]
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': makeString('#bootcamp:invitation/note/{0}'.format(battle_type))})


class _AspectOnOptionalDeviceSelectPopoverGetTabData(aop.Aspect):

    def atReturn(self, cd):
        tabData = cd.returned.get('tabData', None)
        if tabData and len(tabData) > 1:
            cd.returned['tabData'] = tabData[:1]
        return


class _AspectOnOptionalDeviceSelectPopoverPreventCloseAfterMessage(aop.Aspect):

    def atCall(self, cd):
        manager = cd.self.app.containerManager
        container = manager.getContainer(_BC_MESSAGE_VIEW_TYPE)
        window = None
        if container:
            window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW})
        if window:
            cd.avoid()
        return


class _AspectBattleSelectorHintText(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return _BattleSelectorHint(BOOTCAMP.GAME_MODE, PREBATTLE_ACTION_NAME.BOOTCAMP, 0)


class _AspectUnreadMessages(aop.Aspect):

    def atCall(self, cd):
        settings = cd.findArg(3, 'settings')
        if settings is not None and isinstance(settings.auxData, SessionControlAuxData):
            return
        else:
            cd.avoid()
            return


class _AspectOverrideAOGASMessageTimeout(aop.Aspect):
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

    def atCall(self, cd):
        auxData = cd.findArg(3, 'auxData')
        if not isinstance(auxData, SessionControlAuxData):
            return
        if auxData.type != SESSION_CONTROL_TYPE.KOREA_PARENTAL_CONTROL:
            return
        newTimeout = GameSessionController.NOTIFY_PERIOD * _MS_IN_SEC
        return cd.changeArgs((3, 'auxData', SessionControlAuxData(auxData.type, newTimeout)))


class _BattleSelectorHint(SelectorItem):

    def getSmallIcon(self):
        return RES_ICONS.MAPS_ICONS_BOOTCAMP_EMPTYBATTLESELECTORICON

    def isSelectorBtnEnabled(self):
        return True

    def _update(self, state):
        raise SoftException('This method should not be reached in this context')
