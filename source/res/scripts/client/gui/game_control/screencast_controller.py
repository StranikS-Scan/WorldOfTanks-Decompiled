# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/screencast_controller.py
import BigWorld
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.shared.utils import getPlayerDatabaseID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IScreenCastController

class ScreenCastController(IScreenCastController, IArenaVehiclesController):
    """Handle player database ID and set controller
    WOTD-67437
    """
    __slots__ = ('_isSet', '_isBattleCtrlInit', '_dbID')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ScreenCastController, self).__init__()
        self._isSet = False
        self._isBattleCtrlInit = False
        self._dbID = 0

    def fini(self):
        """Clear control
        """
        if self._isBattleCtrlInit:
            self.sessionProvider.removeArenaCtrl(self)

    def onAvatarBecomePlayer(self):
        """Listener for event onAvatarBecomePlayer
        """
        if not self._isBattleCtrlInit:
            self.sessionProvider.addArenaCtrl(self)
            self._isBattleCtrlInit = True
            self.__checkDbID()

    def onAccountBecomePlayer(self):
        """Listener for event onAccountBecomePlayer
        """
        if self._isBattleCtrlInit:
            self.sessionProvider.removeArenaCtrl(self)
            self._isBattleCtrlInit = False

    def invalidateArenaInfo(self):
        """Listener for event invalidateArenaInfo
        """
        self.__checkDbID()

    def invalidateVehiclesInfo(self, _):
        """Listener for event invalidateVehiclesInfo
        """
        self.__checkDbID()

    def onLobbyInited(self, event):
        """Listener for event onLobbyInited
        """
        self.__checkDbID()

    def onDisconnected(self):
        """Listener for event onDisconnected
        """
        self._dbID = 0
        self._isSet = False
        BigWorld.Screener.setUserId(0)

    def __checkDbID(self):
        """Check for database id, if we got one, set controller
        """
        if self._dbID == 0:
            self._dbID = getPlayerDatabaseID()
            self.__update()

    def __update(self):
        """Update controller data, if we have player database id
        """
        if self._dbID != 0 and not self._isSet:
            BigWorld.Screener.setUserId(self._dbID)
            self._isSet = True
