# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/app_loader/observers.py
import weakref
from functools import partial
import typing
import BattleReplay
from constants import ARENA_GUI_TYPE, ACCOUNT_KICK_REASONS
from frameworks.state_machine import BaseStateObserver
from frameworks.state_machine import SingleStateObserver
from frameworks.state_machine import StateEvent
from frameworks.state_machine import StateObserversContainer
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader import spaces
from helpers import dependency
from skeletons.connection_mgr import DisconnectReason
from skeletons.gameplay import GameplayStateID, IGameplayLogic
from skeletons.gui.app_loader import GuiGlobalSpaceID
_BATTLE_OBSERVER_OVERRIDE_HANDLERS = set()

def registerBattleObserverOverrideHandler(handler):
    _BATTLE_OBSERVER_OVERRIDE_HANDLERS.add(handler)


def extendBattleObserverList(battle, proxy):
    result = tuple(battle)
    for handler in _BATTLE_OBSERVER_OVERRIDE_HANDLERS:
        predicate, observers = handler(proxy)
        makePredicatedObservers(predicate, *observers)
        makePredicatedObservers(partial(lambda prd: not prd(), predicate), *battle)
        result += tuple(observers)

    return result


def makePredicatedObservers(predicate, *observers):
    for observer in observers:
        observer.addPredicate(predicate)

    return observers


class PredicativeSingleStateObserver(SingleStateObserver):
    __slots__ = ('_predicates',)

    def __init__(self, stateID):
        super(PredicativeSingleStateObserver, self).__init__(stateID)
        self._predicates = set()

    def addPredicate(self, predicate):
        self._predicates.add(predicate)

    def removePredicate(self, predicate):
        self._predicates.discard(predicate)

    def onStateChanged(self, stateID, flag, event=None):
        if not self._allPredicatesMatch():
            return
        super(PredicativeSingleStateObserver, self).onStateChanged(stateID, flag, event)

    def _allPredicatesMatch(self):
        return all((p() for p in self._predicates))


class AppLoaderObserver(PredicativeSingleStateObserver):
    __slots__ = ('_proxy',)

    def __init__(self, stateID, proxy):
        super(AppLoaderObserver, self).__init__(stateID)
        self._proxy = proxy

    def clear(self):
        self._proxy = None
        super(AppLoaderObserver, self).clear()
        return


class BattleStateResetObserver(AppLoaderObserver):

    def getStateIDs(self):
        return super(BattleStateResetObserver, self).getStateIDs() + (GameplayStateID.ACCOUNT,)

    def onStateChanged(self, stateID, flag, event=None):
        if stateID == GameplayStateID.ACCOUNT:
            self.resetBattleState()
        else:
            super(BattleStateResetObserver, self).onStateChanged(stateID, flag, event)

    def resetBattleState(self):
        pass


class WaitingObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        self._proxy.changeSpace(spaces.WaitingSpace())


class CreateLobbyObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        if self._proxy.getDefBattleApp() is not None:
            self._proxy.destroyBattle()
        if self._proxy.getDefLobbyApp() is None:
            self._proxy.createLobby()
        return


class LoginObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        action = None
        if event is not None:
            disconnectReason = event.getArgument('disconnectReason', DisconnectReason.REQUEST)
            if disconnectReason in (DisconnectReason.EVENT, DisconnectReason.KICK, DisconnectReason.ERROR):
                action = spaces.DisconnectDialogAction(event.getArgument('kickReason', ''), event.getArgument('kickReasonType', ACCOUNT_KICK_REASONS.UNKNOWN), event.getArgument('expiryTime'))
        if self._proxy.getSpaceID() == GuiGlobalSpaceID.LOGIN:
            self._proxy.setupSpace(action=action)
        self._proxy.changeSpace(spaces.LoginSpace(action=action))
        return


class LobbyObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        self._proxy.destroyBattle()
        self._proxy.createLobby()
        self._proxy.changeSpace(spaces.LobbySpace())


class SwitchToBattleObserver(BattleStateResetObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        self._destroyLobby()
        if event is not None:
            arenaGuiType = event.getArgument('arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)
        else:
            arenaGuiType = ARENA_GUI_TYPE.UNKNOWN
        self._createBattle(arenaGuiType=arenaGuiType)
        return

    def _destroyLobby(self):
        self._proxy.destroyLobby()

    def _createBattle(self, arenaGuiType):
        self._proxy.createBattle(arenaGuiType=arenaGuiType)


class BattleLoadingObserver(BattleStateResetObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        if event is not None:
            arenaGuiType = event.getArgument('arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)
        else:
            arenaGuiType = ARENA_GUI_TYPE.UNKNOWN
        self._proxy.changeSpace(spaces.BattleLoadingSpace(arenaGuiType=arenaGuiType))
        return


class BattlePageObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        if event is not None:
            arenaGuiType = event.getArgument('arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)
        else:
            arenaGuiType = ARENA_GUI_TYPE.UNKNOWN
        self._proxy.changeSpace(spaces.BattleSpace(arenaGuiType=arenaGuiType))
        return

    def onExitState(self, event=None):
        self._proxy.destroyBattle()


class SwitchToLobbyObserver(AppLoaderObserver):
    __slots__ = ('_triggerID', '_doCreate')

    def __init__(self, stateID, triggerID, proxy):
        super(SwitchToLobbyObserver, self).__init__(stateID, proxy)
        self._triggerID = triggerID
        self._doCreate = False

    def getStateIDs(self):
        return super(SwitchToLobbyObserver, self).getStateIDs() + (self._triggerID,)

    def onStateChanged(self, stateID, flag, event=None):
        if not self._allPredicatesMatch():
            return
        if self._triggerID == stateID and flag:
            self._doCreate = True
        if self._stateID == stateID and flag and self._doCreate:
            self._doCreate = False
            self._createLobby()

    def _createLobby(self):
        self._proxy.createLobby()


class ReplayEnteringOnlineObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        print 'ReplayEnteringOnlineObserver.onEnterState: event=%s' % str(event)
        self._proxy.destroyLobby()


class ReplayExitingOnlineObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        print 'ReplayExitingOnlineObserver.onEnterState: event=%s' % str(event)
        self._proxy.destroyBattle()


class ReplayVersionDiffersObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        self._proxy.createLobby()
        self._proxy.changeSpace(spaces.LoginSpace(action=spaces.ReplayVersionDiffersDialogAction()))


class ReplayCreateBattleObserver(SwitchToBattleObserver):
    __slots__ = ('__isInvoked',)

    def __init__(self, stateID, proxy):
        super(ReplayCreateBattleObserver, self).__init__(stateID, proxy)
        self.__isInvoked = False

    def resetBattleState(self):
        self.__isInvoked = False

    def onEnterState(self, event=None):
        if not self.__isInvoked:
            self.__isInvoked = True
            super(ReplayCreateBattleObserver, self).onEnterState(event=event)


class ReplayBattleLoadingObserver(BattleLoadingObserver):
    __slots__ = ('__toggleID', '__isToggled')

    def __init__(self, stateID, toggleID, proxy):
        super(ReplayBattleLoadingObserver, self).__init__(stateID, proxy)
        self.__toggleID = toggleID
        self.__isToggled = False

    def getStateIDs(self):
        return super(ReplayBattleLoadingObserver, self).getStateIDs() + (self.__toggleID,)

    def resetBattleState(self):
        self.__isToggled = False

    def onStateChanged(self, stateID, flag, event=None):
        if self.__toggleID == stateID:
            if flag:
                self.__isToggled = True
        else:
            super(ReplayBattleLoadingObserver, self).onStateChanged(stateID, flag, event)

    def onEnterState(self, event=None):
        if event is not None:
            arenaGuiType = event.getArgument('arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)
        else:
            arenaGuiType = ARENA_GUI_TYPE.UNKNOWN
        if self.__isToggled:
            self._proxy.changeSpace(spaces.ReplayLoadingSpace(arenaGuiType=arenaGuiType))
        else:
            self._proxy.changeSpace(spaces.BattleLoadingSpace(arenaGuiType=arenaGuiType))
        return


class ReplayBattlePageObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        if event is not None:
            arenaGuiType = event.getArgument('arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)
        else:
            arenaGuiType = ARENA_GUI_TYPE.UNKNOWN
        self._proxy.changeSpace(spaces.ReplayBattleSpace(arenaGuiType=arenaGuiType))
        return


class ReplayFinishObserver(PredicativeSingleStateObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        action = spaces.ReplayFinishDialogAction()
        action.doAction()


class ReplayRewindObserver(AppLoaderObserver):
    __slots__ = ()

    def onEnterState(self, event=None):
        app = self._proxy.getDefBattleApp()
        if app is not None:
            topWindowContainer = app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
            if topWindowContainer is not None:
                pyView = topWindowContainer.getView({POP_UP_CRITERIA.VIEW_ALIAS: 'simpleDialog'})
                if pyView is not None:
                    topWindowContainer.removeView(pyView)
                    pyView.destroy()
        return


class NormalAppTracker(StateObserversContainer):
    __slots__ = ()

    def __init__(self, proxy):
        common = (CreateLobbyObserver(GameplayStateID.OFFLINE, proxy),
         LoginObserver(GameplayStateID.LOGIN, proxy),
         LobbyObserver(GameplayStateID.ACCOUNT_SHOW_GUI, proxy),
         ReplayEnteringOnlineObserver(GameplayStateID.SERVER_REPLAY_ENTERING, proxy),
         ReplayExitingOnlineObserver(GameplayStateID.SERVER_REPLAY_EXITING, proxy))
        battle = makePredicatedObservers(lambda : not BattleReplay.isPlaying(), SwitchToBattleObserver(GameplayStateID.AVATAR_ENTERING, proxy), BattleLoadingObserver(GameplayStateID.AVATAR_ARENA_INFO, proxy), BattleLoadingObserver(GameplayStateID.AVATAR_SHOW_GUI, proxy), BattlePageObserver(GameplayStateID.AVATAR_ARENA_LOADED, proxy), SwitchToLobbyObserver(GameplayStateID.ACCOUNT_ENTERING, GameplayStateID.AVATAR_EXITING, proxy))
        battle = extendBattleObserverList(battle, proxy)
        replay = makePredicatedObservers(BattleReplay.isPlaying, ReplayCreateBattleObserver(GameplayStateID.AVATAR_ENTERING, proxy), ReplayBattleLoadingObserver(GameplayStateID.AVATAR_ARENA_INFO, GameplayStateID.AVATAR_ARENA_LOADED, proxy), ReplayBattleLoadingObserver(GameplayStateID.AVATAR_SHOW_GUI, GameplayStateID.AVATAR_ARENA_LOADED, proxy), ReplayBattlePageObserver(GameplayStateID.AVATAR_ARENA_LOADED, proxy), ReplayFinishObserver(GameplayStateID.BATTLE_REPLAY_FINISHED), ReplayRewindObserver(GameplayStateID.BATTLE_REPLAY_REWIND, proxy))
        observers = common + battle + replay
        super(NormalAppTracker, self).__init__(*observers)


class ReplayAppTracker(StateObserversContainer):
    __slots__ = ()

    def __init__(self, proxy):
        super(ReplayAppTracker, self).__init__(ReplayVersionDiffersObserver(GameplayStateID.BATTLE_REPLAY_VERSION_DIFFERS, proxy), ReplayCreateBattleObserver(GameplayStateID.AVATAR_ENTERING, proxy), ReplayBattleLoadingObserver(GameplayStateID.AVATAR_ARENA_INFO, GameplayStateID.AVATAR_ARENA_LOADED, proxy), ReplayBattleLoadingObserver(GameplayStateID.AVATAR_SHOW_GUI, GameplayStateID.AVATAR_ARENA_LOADED, proxy), ReplayBattlePageObserver(GameplayStateID.AVATAR_ARENA_LOADED, proxy), ReplayFinishObserver(GameplayStateID.BATTLE_REPLAY_FINISHED), ReplayRewindObserver(GameplayStateID.BATTLE_REPLAY_REWIND, proxy))


class GameplayStatesObserver(BaseStateObserver):
    gameplay = dependency.descriptor(IGameplayLogic)
    __slots__ = ('__proxy', '__tracker')

    def __init__(self, appLoader):
        self.__proxy = weakref.proxy(appLoader)
        self.__tracker = None
        return

    def init(self):
        self.gameplay.addStateObserver(self)

    def fini(self):
        self.gameplay.removeStateObserver(self)
        self.__proxy = None
        self.__clearTracker()
        return

    def getStateIDs(self):
        return (GameplayStateID.OFFLINE, GameplayStateID.BATTLE_REPLAY)

    def onStateChanged(self, stateID, flag, event=None):
        if not flag or self.__tracker is not None:
            return
        else:
            if stateID == GameplayStateID.BATTLE_REPLAY:
                self.__tracker = ReplayAppTracker(self.__proxy)
            else:
                self.__tracker = NormalAppTracker(self.__proxy)
            self.gameplay.addStateObserver(self.__tracker)
            return

    def __clearTracker(self):
        if self.__tracker is not None:
            self.gameplay.removeStateObserver(self.__tracker)
            self.__tracker = None
        return
