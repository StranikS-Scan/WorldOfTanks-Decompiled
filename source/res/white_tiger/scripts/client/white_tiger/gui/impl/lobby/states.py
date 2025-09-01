# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/states.py
import typing
from gui.Scaleform.daapi.view.lobby.battle_queue.states import CommonBattleQueueState
from gui.Scaleform.framework import ScopeTemplates
from gui.prb_control import prbEntityProperty
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.utils.functions import getViewName
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from frameworks.state_machine import StateFlags
from gui.lobby_state_machine.states import GuiImplViewLobbyState, SFViewLobbyState, LobbyState, SubScopeSubLayerState, LobbyStateFlags, LobbyStateDescription, SubScopeTopLayerState
from gui.Scaleform.framework.entities.View import ViewKey
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_HANGAR_ALIASES import WHITE_TIGER_HANGAR_ALIASES
from white_tiger.gui.impl.lobby.welcome_screen_view import WelcomeScreenView
from white_tiger.gui.impl.lobby.feature import WHITE_TIGER_LOCK_SOURCE_NAME
from white_tiger.gui.sounds.sound_constants import WT_PROGRESSION_VIEW_SOUND_SPACE
from gui.lobby_state_machine.transitions import HijackTransition
from gui.impl.lobby.hangar.states import HangarState
from frameworks.state_machine.transitions import TransitionType
from sound_gui_manager import ViewSoundExtension
from WeakMethod import WeakMethodProxy
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

def registerStates(machine):
    machine.addState(WTHangarState())
    machine.addState(WhiteTigerWelcomeState())
    machine.addState(WhiteTigerPostBattleResultState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(WTHangarState), transitionType=TransitionType.EXTERNAL)
    machine.addNavigationTransitionFromParent(machine.getStateByCls(WhiteTigerWelcomeState), transitionType=TransitionType.EXTERNAL)
    machine.addNavigationTransitionFromParent(machine.getStateByCls(WhiteTigerPostBattleResultState), transitionType=TransitionType.EXTERNAL)


@SubScopeSubLayerState.parentOf
class WTHangarState(SFViewLobbyState):
    STATE_ID = WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_HANGAR
    VIEW_KEY = ViewKey(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_HANGAR)
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(WTHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(WTDefaultHangarState(flags=StateFlags.INITIAL))
        lsm.addState(WhiteTigerProgressionState())
        lsm.addState(WhiteTigerQueueScreenState())

    def registerTransitions(self):
        lsm = self.getMachine()
        parent = self.getParent()
        hangar = lsm.getStateByCls(WTDefaultHangarState)
        parent.addNavigationTransition(hangar, record=True)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._hijackTransitionCondition)), hangar)
        preBattleQueue = lsm.getStateByCls(WhiteTigerQueueScreenState)
        hangar.addNavigationTransition(preBattleQueue)
        parent.addTransition(HijackTransition(CommonBattleQueueState, WeakMethodProxy(self._hijackTransitionCondition)), preBattleQueue)
        children = self.getChildrenStates()
        for state in children:
            lsm.addNavigationTransitionFromParent(state)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))

    def _hijackTransitionCondition(self, event):
        return self.__wtCtrl.isEventPrbActive() and self.__wtCtrl.isAvailable()


@WTHangarState.parentOf
class WTDefaultHangarState(LobbyState):
    STATE_ID = '{root}'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(WTDefaultHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))

    def _onEntered(self, event):
        lockNotificationManager(lock=True, source=WHITE_TIGER_LOCK_SOURCE_NAME, releasePostponed=True)
        super(WTDefaultHangarState, self)._onEntered(event)
        lockNotificationManager(lock=False, source=WHITE_TIGER_LOCK_SOURCE_NAME, releasePostponed=True)


@WTHangarState.parentOf
class WhiteTigerProgressionState(LobbyState):
    STATE_ID = 'progression'
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __soundExtension = ViewSoundExtension(WT_PROGRESSION_VIEW_SOUND_SPACE)

    def registerTransitions(self):
        lsm = self.getMachine()
        subScopeSubLayer = lsm.getStateByCls(SubScopeSubLayerState)
        subScopeSubLayer.addNavigationTransition(self, record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))

    def _onEntered(self, event):
        self.__soundExtension.initSoundManager()
        self.__soundExtension.startSoundSpace()
        super(WhiteTigerProgressionState, self)._onEntered(event)

    def _onExited(self):
        self.__economicsCtrl.notifyProgressSeen()
        self.__soundExtension.destroySoundManager()
        super(WhiteTigerProgressionState, self)._onExited()


@SubScopeTopLayerState.parentOf
class WhiteTigerWelcomeState(GuiImplViewLobbyState):
    STATE_ID = 'welcomeScreen'
    VIEW_KEY = ViewKey(WelcomeScreenView.LAYOUT_ID)

    def __init__(self):
        super(WhiteTigerWelcomeState, self).__init__(WelcomeScreenView, scope=ScopeTemplates.LOBBY_TOP_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))


@SubScopeTopLayerState.parentOf
class WhiteTigerQueueScreenState(SFViewLobbyState):
    STATE_ID = WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_QUEUE_SCREEN
    VIEW_KEY = ViewKey(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_QUEUE_SCREEN)

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))

    def _onExited(self):
        if self.prbEntity and self.prbEntity.isInQueue() and self.prbEntity.getPermissions().canExitFromQueue():
            self.prbEntity.exitFromQueue()
        super(WhiteTigerQueueScreenState, self)._onExited()


@SubScopeSubLayerState.parentOf
class WhiteTigerPostBattleResultState(SFViewLobbyState):
    STATE_ID = 'whiteTigerPBS'
    VIEW_KEY = ViewKey(WHITE_TIGER_HANGAR_ALIASES.WHITE_TIGER_BATTLE_RESULT)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(WhiteTigerPostBattleResultState, self).__init__(flags=flags)
        self.__cachedArenaId = {}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.white_tiger_lobby.headerButtons.battle.types.white_tiger()))

    def _onEntered(self, event):
        self.__cachedArenaId = event.params['arenaUniqueID']
        super(WhiteTigerPostBattleResultState, self)._onEntered(event)

    def getViewKey(self, params=None):
        arenaUniqueID = self.__cachedArenaId
        alias = super(WhiteTigerPostBattleResultState, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))
