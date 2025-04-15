# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/easy_tank_equip_controller.py
import Event
from typing import Optional, TYPE_CHECKING
from constants import Configs
from helpers import dependency
from helpers.server_settings import EasyTankEquipConfig
from skeletons.gui.game_control import IEasyTankEquipController
from skeletons.gui.lobby_context import ILobbyContext
from gui.game_control.wotlda.easy_tank_equip_provider import _EasyTankEquipProvider
if TYPE_CHECKING:
    from gui.game_control.wotlda.loadout_model import BaseOptDeviceLoadoutModel

class EasyTankEquipController(IEasyTankEquipController):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__em = Event.EventManager()
        self.onUpdated = Event.Event(self.__em)
        self._dataProvider = _EasyTankEquipProvider()
        super(EasyTankEquipController, self).__init__()

    @property
    def config(self):
        return self.__lobbyContext.getServerSettings().getEasyTankEquip() if self.__lobbyContext else EasyTankEquipConfig()

    def fini(self):
        self.__em.clear()
        self.__removeListeners()
        self._dataProvider.stop()
        super(EasyTankEquipController, self).fini()

    def onDisconnected(self):
        self.__removeListeners()
        self._dataProvider.clear()
        super(EasyTankEquipController, self).onDisconnected()

    def onAccountBecomeNonPlayer(self):
        self.__removeListeners()
        super(EasyTankEquipController, self).onAccountBecomeNonPlayer()

    def onLobbyInited(self, event):
        super(EasyTankEquipController, self).onLobbyInited(event)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        if not self.config.enabled:
            return
        self._dataProvider.updateCacheData()

    def onLobbyStarted(self, ctx):
        if not self.config.enabled:
            return
        self._dataProvider.start()

    def getLoadoutByVehicleID(self, vehicleID):
        return self._dataProvider.getLoadoutByVehicleID(vehicleID)

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        if Configs.EASY_TANK_EQUIP_CONFIG.value in diff:
            if self.config.enabled:
                self._dataProvider.start()
            else:
                self._dataProvider.clear()
            self.onUpdated()
