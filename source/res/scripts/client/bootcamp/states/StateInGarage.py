# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/states/StateInGarage.py
from copy import deepcopy
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampLobbyHintsConfig import g_bootcampHintsConfig
from bootcamp.BootcampSettings import getGarageDefaults
from bootcamp.states import STATE
from bootcamp.states.AbstractState import AbstractState
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.prb_control.items import SelectResult
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.events import GUICommonEvent
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from PlayerEvents import g_playerEvents
from gui import makeHtmlString
from helpers import aop
from helpers.i18n import makeString as _ms
from constants import PREBATTLE_TYPE_NAMES

class BCPrbDisableSelect(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return SelectResult(True)


class BCPrbDisableAccept(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return False


class BCPrbInvitationNote(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        battle_type = PREBATTLE_TYPE_NAMES[cd.args[0].type]
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': _ms('#bootcamp:invitation/note/{0}'.format(battle_type))})


class BootcampPrbDisableEntitySelect(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.prb_control.entities.bootcamp.pre_queue.entity', 'BootcampEntity', 'doSelectAction', aspects=(BCPrbDisableSelect,))


class BootcampPrbDisableAcceptButton(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.prb_control.invites', 'InvitesManager', 'canAcceptInvite', aspects=(BCPrbDisableAccept,))


class BootcampPrbInvitationText(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.prb_control.formatters.invites', 'PrbInviteHtmlTextFormatter', 'getNote', aspects=(BCPrbInvitationNote,))


class BootcampSysMessagesPointcut(aop.Pointcut):

    def __init__(self):
        super(BootcampSysMessagesPointcut, self).__init__('gui.Scaleform.SystemMessagesInterface', 'SystemMessagesInterface', '^pushMessage$')


class BootcampFriendRequestPointcut(aop.Pointcut):

    def __init__(self):
        super(BootcampFriendRequestPointcut, self).__init__('notification.listeners', 'FriendshipRqsListener', '^(start|stop)$')


class StateInGarage(AbstractState):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, lessonNum, account, checkpoint):
        super(StateInGarage, self).__init__(STATE.IN_GARAGE)
        self.__lessonId = lessonNum
        self.__account = account
        self.__checkpoint = checkpoint
        self.__weaver = aop.Weaver()

    def _onBattleReady(self):
        pass

    def onLobbyLessonFinished(self):
        g_bootcampEvents.onBattleReady()

    def onLobbyInited(self, event):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.BOOTCAMP_LOBBY_HIGHLIGHTS, None, {'descriptors': g_bootcampHintsConfig.getItems()}), EVENT_BUS_SCOPE.LOBBY)
        return

    def handleKeyEvent(self, event):
        pass

    def _doActivate(self):
        self.__weaver.weave(pointcut=BootcampPrbDisableEntitySelect)
        self.__weaver.weave(pointcut=BootcampPrbInvitationText)
        self.__weaver.weave(pointcut=BootcampPrbDisableAcceptButton)
        self.__weaver.weave(pointcut=BootcampSysMessagesPointcut, avoid=True)
        self.__weaver.weave(pointcut=BootcampFriendRequestPointcut, avoid=True)
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_bootcampGarage.init(self.__lessonId, self.__account)
        g_bootcampGarage.setCheckpoint(self.__checkpoint)
        from bootcamp.Bootcamp import g_bootcamp
        g_bootcamp.setLobbySettings(deepcopy(getGarageDefaults()['panels']))
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.onLobbyInited)
        g_bootcampEvents.onBattleReady += self._onBattleReady
        g_bootcamp.setBootcampHangarSpace()
        g_playerEvents.onAccountShowGUI(self.lobbyContext.getGuiCtx())
        g_bootcampGarage.selectLessonVehicle()
        LOG_DEBUG_DEV_BOOTCAMP('Created tutorialGarage', self.__lessonId)

    def _doDeactivate(self):
        from bootcamp.BootcampGarage import g_bootcampGarage
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADED, self.onLobbyInited)
        g_bootcampEvents.onBattleReady -= self._onBattleReady
        g_bootcampGarage.stopLobbyAssistance()
        g_bootcampGarage.clear()
        self.__weaver.clear()
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_currentVehicle.destroy()
        g_currentPreviewVehicle.destroy()
        g_hangarSpace.destroy()
