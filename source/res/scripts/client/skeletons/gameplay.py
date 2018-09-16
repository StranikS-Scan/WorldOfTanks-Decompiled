# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gameplay.py


class GameplayStateID(object):
    START = 'game.start'
    STOP = 'game.stop'
    OFFLINE = 'game.offline'
    ONLINE = 'game.online'
    BATTLE_REPLAY = 'game.replay'
    ACCOUNT = 'online.account'
    AVATAR = 'online.avatar'
    GAME_LOADING = 'offline.game_loading'
    INTRO_VIDEO = 'offline.intro_video'
    LOGIN = 'offline.login'
    ACCOUNT_ENTERING = 'account.entering'
    ACCOUNT_SHOW_GUI = 'account.show_gui'
    ACCOUNT_EXITING = 'account.exiting'
    AVATAR_ENTERING = 'avatar.entering'
    AVATAR_SHOW_GUI = 'avatar.show_gui'
    AVATAR_ARENA_INFO = 'avatar.arena.info'
    AVATAR_ARENA_LOADED = 'avatar.arena.loaded'
    AVATAR_EXITING = 'avatar.exiting'
    BATTLE_REPLAY_LOADING = 'replay.loading'
    BATTLE_REPLAY_VERSION_DIFFERS = 'replay.version.differs'
    BATTLE_REPLAY_STARTING = 'replay.starting'
    BATTLE_REPLAY_PLAYING = 'replay.playing'
    BATTLE_REPLAY_REWIND = 'replay.rewind'
    BATTLE_REPLAY_FINISHED = 'replay.finished'
    BATTLE_REPLAY_NEXT = 'replay.next'


class GUIEventID(object):
    INTRO_VIDEO_FINISHED = 'gui.intro_video.finished'


class PlayerEventID(object):
    ACCOUNT_BECOME_PLAYER = 'player.account.entering'
    ACCOUNT_SHOW_GUI = 'player.account.show_gui'
    ACCOUNT_BECOME_NON_PLAYER = 'player.account.exiting'
    AVATAR_BECOME_PLAYER = 'player.avatar.entering'
    AVATAR_ARENA_INFO = 'player.avatar.arena.info'
    AVATAR_SHOW_GUI = 'player.avatar.show_gui'
    AVATAR_ARENA_LOADING = 'player.avatar.arena.loading'
    AVATAR_ARENA_LOADED = 'player.avatar.arena.loaded'
    AVATAR_BECOME_NON_PLAYER = 'player.avatar.exiting'
    NON_PLAYER_BECOME_PLAYER = 'player.non_player'


class ReplayEventID(object):
    REPLAY_VERSION_CONFIRMATION = 'replay.version.confirmation'
    REPLAY_VERSION_CONFIRMED = 'replay.version.confirmed'
    REPLAY_REWIND = 'replay.rewind'
    REPLAY_FINISHED = 'replay.finished'
    REPLAY_NEXT = 'replay.next'


class IGameplayLogic(object):
    __slots__ = ()

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def postStateEvent(self, eventID, **kwargs):
        raise NotImplementedError

    def addStateObserver(self, observer):
        raise NotImplementedError

    def removeStateObserver(self, observer):
        raise NotImplementedError

    def goToLoginByRQ(self):
        raise NotImplementedError

    def goToLoginByEvent(self):
        raise NotImplementedError

    def goToLoginByKick(self, reason, isBan, expiryTime):
        raise NotImplementedError

    def goToLoginByError(self, reason):
        raise NotImplementedError

    @staticmethod
    def quitFromGame():
        raise NotImplementedError

    def tick(self):
        raise NotImplementedError
