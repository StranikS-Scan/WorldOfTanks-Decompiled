# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/listeners.py
import weakref
import BigWorld
from PlayerEvents import g_playerEvents
from constants import ARENA_GUI_TYPE
from frameworks.state_machine.events import StringEvent
from skeletons.gameplay import PlayerEventID, ReplayEventID

class PlayerEventsAdaptor(object):
    __slots__ = ('_machine',)

    def __init__(self, machine):
        super(PlayerEventsAdaptor, self).__init__()
        self._machine = weakref.proxy(machine)

    def startListening(self):
        g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer
        g_playerEvents.onServerReplayEntering += self.__onServerReplayEntering
        g_playerEvents.onServerReplayExiting += self.__onServerReplayExiting

    def stopListening(self):
        g_playerEvents.onAccountBecomePlayer -= self.__onAccountBecomePlayer
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer
        g_playerEvents.onServerReplayEntering -= self.__onServerReplayEntering
        g_playerEvents.onServerReplayExiting -= self.__onServerReplayExiting

    def __onAccountBecomePlayer(self):
        self._machine.post(StringEvent(PlayerEventID.ACCOUNT_BECOME_PLAYER))

    def __onAccountBecomeNonPlayer(self):
        self._machine.post(StringEvent(PlayerEventID.ACCOUNT_BECOME_NON_PLAYER))

    def __onAvatarBecomePlayer(self):
        self._machine.post(StringEvent(PlayerEventID.AVATAR_BECOME_PLAYER, arenaGuiType=getattr(BigWorld.player(), 'arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)))

    def __onAvatarBecomeNonPlayer(self):
        self._machine.post(StringEvent(PlayerEventID.AVATAR_BECOME_NON_PLAYER))

    def __onServerReplayEntering(self):
        self._machine.post(StringEvent(ReplayEventID.SERVER_REPLAY_ENTERING))

    def __onServerReplayExiting(self):
        self._machine.post(StringEvent(ReplayEventID.SERVER_REPLAY_EXITING))
