# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/screencast_controller.py
import BigWorld
from gui.battle_control import g_sessionProvider
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.game_control.controllers import Controller
from gui.shared.utils import getPlayerDatabaseID

class ScreenCastController(Controller, IArenaVehiclesController):
    """Handle player database ID and set controller
    WOTD-67437
    """
    __slots__ = ('_isSet', '_isBattleCtrlInit', '_dbID')

    def __init__(self, proxy):
        super(ScreenCastController, self).__init__(proxy)
        self._isSet = False
        self._isBattleCtrlInit = False
        self._dbID = 0

    def fini(self):
        """Clear control
        """
        if self._isBattleCtrlInit:
            g_sessionProvider.removeArenaCtrl(self)

    def onAvatarBecomePlayer(self):
        """Listener for event onAvatarBecomePlayer
        """
        if not self._isBattleCtrlInit:
            g_sessionProvider.addArenaCtrl(self)
            self._isBattleCtrlInit = True
            self.__checkDbID()

    def onAccountBecomePlayer(self):
        """Listener for event onAccountBecomePlayer
        """
        if self._isBattleCtrlInit:
            g_sessionProvider.removeArenaCtrl(self)
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
