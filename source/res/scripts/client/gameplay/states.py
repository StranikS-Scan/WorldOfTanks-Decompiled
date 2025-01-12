# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/states.py
import logging
import enum
import typing
import BattleReplay
import BigWorld
import persistent_data_cache as pdc
import wg_async
from PlayerEvents import g_playerEvents
from constants import IS_DEVELOPMENT
from frameworks.state_machine import State, StateFlags, StringEvent
from frameworks.state_machine import StringEventTransition
from gui.game_loading import loading as gameLoading
from gui.game_loading.resources.consts import Milestones
from shared_utils import safeCancelCallback
from skeletons.gameplay import GameplayStateID, OfflineEventID
from skeletons.gameplay import PlayerEventID
from skeletons.gameplay import ReplayEventID
if typing.TYPE_CHECKING:
    from gameplay.machine import GameplayStateMachine
_logger = logging.getLogger(__name__)

@enum.unique
class SyncingProgress(enum.IntEnum):
    NOT_STARTED = 0
    SYNCING = 1
    COMPLETE = 2
    CANCELED = 3


class WaitingMainLoopState(State):
    __slots__ = ('_callbackId',)

    def __init__(self):
        super(WaitingMainLoopState, self).__init__(GameplayStateID.WAITING_MAIN_LOOP, flags=StateFlags.INITIAL | StateFlags.SINGULAR)
        self._callbackId = None
        return

    def clear(self):
        self._cancelWaiting()
        super(WaitingMainLoopState, self).clear()

    def _onEntered(self):
        super(WaitingMainLoopState, self)._onEntered()
        self._initWaiting()

    def _onExited(self):
        self._cancelWaiting()
        super(WaitingMainLoopState, self)._onExited()

    def _initWaiting(self):
        if self._callbackId is None:
            self._callbackId = BigWorld.callback(0.0, self._onCompleteEvent)
            _logger.debug('[%s] Waiting initialized.', self)
        else:
            _logger.error('[%s] Waiting already initialized.', self)
        return

    def _cancelWaiting(self):
        if self._callbackId is not None:
            safeCancelCallback(self._callbackId)
            self._callbackId = None
            _logger.debug('[%s] Waiting canceled.', self)
        return

    def _onCompleteEvent(self):
        self._cancelWaiting()
        machine = self.getMachine()
        if machine is not None:
            machine.post(StringEvent(OfflineEventID.MAIN_LOOP_INITIALIZED))
        else:
            _logger.error('[%s] not registered in state machine.', self)
        return


class SynchronizationState(State):
    __slots__ = ('_syncProgress', '_savePDC')
    _PDC_SAVING_TIMEOUT = 120.0 if not IS_DEVELOPMENT else None
    _GAME_LOADING_TIMEOUT = 15.0 if not IS_DEVELOPMENT else None

    def __init__(self, savePDC=True):
        super(SynchronizationState, self).__init__(GameplayStateID.SYNCHRONIZATION, flags=StateFlags.SINGULAR)
        self._syncProgress = SyncingProgress.NOT_STARTED
        self._savePDC = savePDC

    def clear(self):
        self._syncProgress = SyncingProgress.CANCELED
        super(SynchronizationState, self).clear()

    @staticmethod
    def _fireSavingPDCEvent():
        g_playerEvents.onLoadingMilestoneReached(Milestones.SAVING_PDC)

    @wg_async.wg_async
    def _onEntered(self):
        super(SynchronizationState, self)._onEntered()
        if self._syncProgress == SyncingProgress.NOT_STARTED:
            canceled = yield wg_async.wg_await(self._sync())
            if canceled:
                raise wg_async.AsyncReturn(None)
        else:
            _logger.error('[%s] Already %s.', self, self._syncProgress)
        self._onCompleteEvent()
        return

    @wg_async.wg_async
    def _sync(self):
        self._syncProgress = SyncingProgress.SYNCING
        _logger.debug('[%s] Loading started.', self)
        if self._savePDC:
            pdcEvents = pdc.getEventsDispatcher()
            if pdcEvents is not None:
                pdcEvents.onCacheDataSavingStarted += self._fireSavingPDCEvent
            yield wg_async.wg_await(pdc.save(timeout=self._PDC_SAVING_TIMEOUT))
            if pdcEvents is not None:
                pdcEvents.onCacheDataSavingStarted -= self._fireSavingPDCEvent
            if self._syncProgress != SyncingProgress.SYNCING:
                _logger.debug('[%s] PDC saved. Loading skipped -> %s.', self, self._syncProgress)
                raise wg_async.AsyncReturn(True)
        else:
            _logger.debug('[%s] PDC saving skipped.', self)
        gameLoadingWaiting = gameLoading.getLoader()
        gameLoadingWaiting.setGameLoadingComplete()
        yield wg_async.wg_await(gameLoadingWaiting.wait(timeout=self._GAME_LOADING_TIMEOUT))
        if self._syncProgress != SyncingProgress.SYNCING:
            _logger.debug('[%s] Waiting released. Loading skipped -> %s.', self, self._syncProgress)
            raise wg_async.AsyncReturn(True)
        self._syncProgress = SyncingProgress.COMPLETE
        _logger.debug('[%s] Loading completed.', self)
        raise wg_async.AsyncReturn(False)
        return

    def _onExited(self):
        self._syncProgress = SyncingProgress.CANCELED
        super(SynchronizationState, self)._onExited()

    def _onCompleteEvent(self):
        machine = self.getMachine()
        if machine is not None:
            machine.post(StringEvent(OfflineEventID.SYNCHRONIZED))
        else:
            _logger.error('[%s] not registered in state machine.', self)
        return


class OfflineState(State):
    __slots__ = ()

    def __init__(self):
        super(OfflineState, self).__init__(stateID=GameplayStateID.OFFLINE, flags=StateFlags.INITIAL | StateFlags.SINGULAR)

    @property
    def waitingMainLoop(self):
        return self.getChildByIndex(0)

    @property
    def synchronization(self):
        return self.getChildByIndex(1)

    @property
    def login(self):
        return self.getChildByIndex(2)

    def configure(self):
        waitingMainLoop = WaitingMainLoopState()
        synchronization = SynchronizationState()
        login = State(stateID=GameplayStateID.LOGIN, flags=StateFlags.SINGULAR)
        self.addChildState(waitingMainLoop)
        self.addChildState(synchronization)
        self.addChildState(login)
        waitingMainLoop.addTransition(StringEventTransition(OfflineEventID.MAIN_LOOP_INITIALIZED), target=synchronization)
        synchronization.addTransition(StringEventTransition(OfflineEventID.SYNCHRONIZED), target=login)


class OnlineState(State):
    __slots__ = ()

    def __init__(self):
        super(OnlineState, self).__init__(stateID=GameplayStateID.ONLINE)

    @property
    def account(self):
        return self.getChildByIndex(0)

    @property
    def avatar(self):
        return self.getChildByIndex(1)

    def configure(self, offline):
        account = AccountState(flags=StateFlags.INITIAL | StateFlags.SINGULAR)
        account.configure()
        avatar = AvatarState()
        avatar.configure()
        enteringReplay = State(stateID=GameplayStateID.SERVER_REPLAY_ENTERING)
        exitingReplay = State(stateID=GameplayStateID.SERVER_REPLAY_EXITING)
        rewindReplay = State(GameplayStateID.BATTLE_REPLAY_REWIND)
        finishReplay = State(GameplayStateID.BATTLE_REPLAY_FINISHED)
        self.addChildState(account)
        self.addChildState(avatar)
        self.addChildState(enteringReplay)
        self.addChildState(exitingReplay)
        self.addChildState(rewindReplay)
        self.addChildState(finishReplay)
        offline.addTransition(StringEventTransition(PlayerEventID.ACCOUNT_BECOME_PLAYER), target=account)
        offline.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_PLAYER), target=avatar)
        account.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_PLAYER), target=avatar)
        account.addTransition(StringEventTransition(ReplayEventID.SERVER_REPLAY_ENTERING), target=enteringReplay)
        enteringReplay.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_PLAYER), target=avatar)
        enteringReplay.addTransition(StringEventTransition(ReplayEventID.SERVER_REPLAY_EXITING), target=exitingReplay)
        avatar.addTransition(StringEventTransition(ReplayEventID.REPLAY_FINISHED), target=finishReplay)
        avatar.addTransition(StringEventTransition(ReplayEventID.SERVER_REPLAY_EXITING), target=exitingReplay)
        exitingReplay.addTransition(StringEventTransition(PlayerEventID.ACCOUNT_BECOME_PLAYER), target=account)
        avatar.addTransition(StringEventTransition(PlayerEventID.ACCOUNT_BECOME_PLAYER), target=account)
        avatar.addTransition(StringEventTransition(ReplayEventID.REPLAY_REWIND), target=rewindReplay)
        rewindReplay.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_PLAYER), target=avatar)
        rewindReplay.addTransition(StringEventTransition(ReplayEventID.SERVER_REPLAY_EXITING), target=exitingReplay)
        finishReplay.addTransition(StringEventTransition(ReplayEventID.REPLAY_REWIND), target=rewindReplay)
        finishReplay.addTransition(StringEventTransition(ReplayEventID.SERVER_REPLAY_EXITING), target=exitingReplay)
        self.addTransition(StringEventTransition(PlayerEventID.NON_PLAYER_BECOME_PLAYER), target=offline.login)


class AccountState(State):
    __slots__ = ()

    def __init__(self, flags=StateFlags.SINGULAR):
        super(AccountState, self).__init__(stateID=GameplayStateID.ACCOUNT, flags=flags)

    @property
    def entering(self):
        return self.getChildByIndex(0)

    @property
    def showGUI(self):
        return self.getChildByIndex(1)

    @property
    def exiting(self):
        return self.getChildByIndex(2)

    def configure(self):
        entering = State(stateID=GameplayStateID.ACCOUNT_ENTERING, flags=StateFlags.INITIAL | StateFlags.SINGULAR)
        showGUI = State(stateID=GameplayStateID.ACCOUNT_SHOW_GUI)
        exiting = State(stateID=GameplayStateID.ACCOUNT_EXITING)
        self.addChildState(entering)
        self.addChildState(showGUI)
        self.addChildState(exiting)
        entering.addTransition(StringEventTransition(PlayerEventID.ACCOUNT_SHOW_GUI), target=showGUI)
        showGUI.addTransition(StringEventTransition(PlayerEventID.ACCOUNT_BECOME_NON_PLAYER), target=exiting)
        exiting.addTransition(StringEventTransition(PlayerEventID.ACCOUNT_BECOME_PLAYER), target=entering)


class AvatarState(State):
    __slots__ = ()

    def __init__(self, flags=StateFlags.SINGULAR):
        super(AvatarState, self).__init__(stateID=GameplayStateID.AVATAR, flags=flags)

    @property
    def entering(self):
        return self.getChildByIndex(0)

    @property
    def arenaInfo(self):
        return self.getChildByIndex(1)

    @property
    def showGUI(self):
        return self.getChildByIndex(2)

    @property
    def arenaLoaded(self):
        return self.getChildByIndex(3)

    @property
    def exiting(self):
        return self.getChildByIndex(4)

    def configure(self):
        entering = State(stateID=GameplayStateID.AVATAR_ENTERING, flags=StateFlags.INITIAL | StateFlags.SINGULAR)
        arenaInfo = State(stateID=GameplayStateID.AVATAR_ARENA_INFO)
        showGUI = State(stateID=GameplayStateID.AVATAR_SHOW_GUI)
        arenaLoaded = State(stateID=GameplayStateID.AVATAR_ARENA_LOADED)
        exiting = State(stateID=GameplayStateID.AVATAR_EXITING)
        self.addChildState(entering)
        self.addChildState(arenaInfo)
        self.addChildState(showGUI)
        self.addChildState(arenaLoaded)
        self.addChildState(exiting)
        entering.addTransition(StringEventTransition(PlayerEventID.AVATAR_ARENA_INFO), target=arenaInfo)
        arenaInfo.addTransition(StringEventTransition(PlayerEventID.AVATAR_SHOW_GUI), target=showGUI)
        arenaInfo.addTransition(StringEventTransition(PlayerEventID.AVATAR_ARENA_LOADED), target=arenaLoaded)
        showGUI.addTransition(StringEventTransition(PlayerEventID.AVATAR_ARENA_LOADED), target=arenaLoaded)
        arenaLoaded.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_NON_PLAYER), target=exiting)


class BattleReplayLoadingState(State):
    __slots__ = ()

    def __init__(self):
        super(BattleReplayLoadingState, self).__init__(stateID=GameplayStateID.BATTLE_REPLAY_LOADING, flags=StateFlags.SINGULAR)

    def enter(self):
        super(BattleReplayLoadingState, self).enter()
        BattleReplay.g_replayCtrl.autoStartBattleReplay()


class BattleReplayInitState(State):
    __slots__ = ()

    def __init__(self):
        super(BattleReplayInitState, self).__init__(stateID=GameplayStateID.BATTLE_REPLAY, flags=StateFlags.INITIAL | StateFlags.SINGULAR)

    @property
    def loading(self):
        return self.getChildByIndex(0)

    @property
    def differs(self):
        return self.getChildByIndex(1)

    @property
    def starting(self):
        return self.getChildByIndex(2)

    @property
    def nextReplay(self):
        return self.getChildByIndex(3)

    @property
    def waitingMainLoop(self):
        return self.getChildByIndex(4)

    @property
    def synchronization(self):
        return self.getChildByIndex(5)

    def configure(self):
        waitingMainLoop = WaitingMainLoopState()
        synchronization = SynchronizationState(savePDC=False)
        loading = BattleReplayLoadingState()
        differs = State(stateID=GameplayStateID.BATTLE_REPLAY_VERSION_DIFFERS)
        starting = State(stateID=GameplayStateID.BATTLE_REPLAY_STARTING)
        nextReplay = State(stateID=GameplayStateID.BATTLE_REPLAY_NEXT)
        waitingMainLoop.addTransition(StringEventTransition(OfflineEventID.MAIN_LOOP_INITIALIZED), target=synchronization)
        synchronization.addTransition(StringEventTransition(OfflineEventID.SYNCHRONIZED), target=loading)
        loading.addTransition(StringEventTransition(ReplayEventID.REPLAY_VERSION_CONFIRMATION), target=differs)
        nextReplay.addTransition(StringEventTransition(ReplayEventID.REPLAY_VERSION_CONFIRMATION), target=differs)
        differs.addTransition(StringEventTransition(ReplayEventID.REPLAY_VERSION_CONFIRMED), target=starting)
        self.addChildState(loading)
        self.addChildState(differs)
        self.addChildState(starting)
        self.addChildState(nextReplay)
        self.addChildState(waitingMainLoop)
        self.addChildState(synchronization)


class BattleReplayPlayingState(State):
    __slots__ = ()

    def __init__(self):
        super(BattleReplayPlayingState, self).__init__(stateID=GameplayStateID.BATTLE_REPLAY_PLAYING)

    @property
    def avatar(self):
        return self.getChildByIndex(0)

    @property
    def finish(self):
        return self.getChildByIndex(1)

    @property
    def rewind(self):
        return self.getChildByIndex(2)

    def configure(self, initialization):
        avatar = AvatarState(flags=StateFlags.INITIAL | StateFlags.SINGULAR)
        avatar.configure()
        finish = State(GameplayStateID.BATTLE_REPLAY_FINISHED)
        rewind = State(GameplayStateID.BATTLE_REPLAY_REWIND)
        self.addChildState(avatar)
        self.addChildState(finish)
        self.addChildState(rewind)
        initialization.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_PLAYER), target=avatar)
        rewind.addTransition(StringEventTransition(PlayerEventID.AVATAR_BECOME_PLAYER), target=avatar)
        avatar.addTransition(StringEventTransition(ReplayEventID.REPLAY_FINISHED), target=finish)
        avatar.addTransition(StringEventTransition(ReplayEventID.REPLAY_REWIND), target=rewind)
        finish.addTransition(StringEventTransition(ReplayEventID.REPLAY_REWIND), target=rewind)
        avatar.exiting.addTransition(StringEventTransition(ReplayEventID.REPLAY_NEXT), target=initialization.nextReplay)
