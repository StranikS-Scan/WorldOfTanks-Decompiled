# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/states.py
from frameworks.state_machine import State, StateFlags
from frameworks.state_machine import StringEventTransition
from skeletons.gameplay import GameplayStateID
from skeletons.gameplay import PlayerEventID
from skeletons.gameplay import ReplayEventID

class OfflineState(State):
    __slots__ = ()

    def __init__(self):
        super(OfflineState, self).__init__(stateID=GameplayStateID.OFFLINE, flags=StateFlags.INITIAL | StateFlags.SINGULAR)

    @property
    def login(self):
        return self.getChildByIndex(0)

    def configure(self):
        login = State(stateID=GameplayStateID.LOGIN, flags=StateFlags.INITIAL | StateFlags.SINGULAR)
        self.addChildState(login)


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

    def configure(self):
        loading = State(stateID=GameplayStateID.BATTLE_REPLAY_LOADING, flags=StateFlags.SINGULAR | StateFlags.INITIAL)
        differs = State(stateID=GameplayStateID.BATTLE_REPLAY_VERSION_DIFFERS)
        starting = State(stateID=GameplayStateID.BATTLE_REPLAY_STARTING)
        nextReplay = State(stateID=GameplayStateID.BATTLE_REPLAY_NEXT)
        loading.addTransition(StringEventTransition(ReplayEventID.REPLAY_VERSION_CONFIRMATION), target=differs)
        nextReplay.addTransition(StringEventTransition(ReplayEventID.REPLAY_VERSION_CONFIRMATION), target=differs)
        differs.addTransition(StringEventTransition(ReplayEventID.REPLAY_VERSION_CONFIRMED), target=starting)
        self.addChildState(loading)
        self.addChildState(differs)
        self.addChildState(starting)
        self.addChildState(nextReplay)


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
