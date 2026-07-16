# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_vehicle_selection_controller.py
from __future__ import absolute_import
import BigWorld
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.system_factory import collectIgnoredModeForAutoSelectVehicle
from last_stand.gui import vehicleComparisonKey
from last_stand.gui.ls_account_settings import getSettings, AccountSettingsKeys, setSettings
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_vehicle_selection_controller import ILSVehicleSelectionController
from last_stand_common.last_stand_constants import LAST_STAND_ARENA_BONUS_TYPES
from skeletons.gui.shared import IItemsCache

class LSVehicleSelectionController(ILSVehicleSelectionController, IGlobalListener):
    _lsCtrl = dependency.descriptor(ILSController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(LSVehicleSelectionController, self).__init__()
        self.__active = False
        self.__returnFromLSBattle = False

    def onLobbyInited(self, event):
        super(LSVehicleSelectionController, self).onLobbyInited(event)
        self.startGlobalListening()

    def onAvatarBecomePlayer(self):
        super(LSVehicleSelectionController, self).onAvatarBecomePlayer()
        arena = getattr(BigWorld.player(), 'arena', None)
        bonusType = arena.bonusType if arena is not None else None
        self.__returnFromLSBattle = bonusType in LAST_STAND_ARENA_BONUS_TYPES
        self.stopGlobalListening()
        return

    def onDisconnected(self):
        self.__returnFromLSBattle = False
        self.stopGlobalListening()
        self.deactivate()
        super(LSVehicleSelectionController, self).onDisconnected()

    def onPrbEntitySwitched(self):
        if not any((self.prbEntity.getModeFlags() & flag for flag in collectIgnoredModeForAutoSelectVehicle())):
            g_currentVehicle.selectVehicle(AccountSettings.getFavorites(CURRENT_VEHICLE))

    def activate(self):
        if self.__active:
            return
        self.__active = True
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.selectModeVehicle()

    def deactivate(self):
        if not self.__active:
            return
        self.__active = False
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged

    def selectModeVehicle(self, vehInvID=0):
        if not vehInvID:
            vehInvID = self.__getFavoriteVehInvID()
        if vehInvID:
            setSettings(AccountSettingsKeys.FAVORITES_VEHICLE, vehInvID)
            g_currentVehicle.selectVehicle(vehInvID)
        else:
            g_currentVehicle.selectNoVehicle()

    def selectVehicle(self, vehInvID):
        if self.__active:
            self.selectModeVehicle(vehInvID)

    @prbEntityProperty
    def prbEntity(self):
        pass

    def __getFavoriteVehInvID(self):
        modeVehicles = self._lsCtrl.getSuitableVehicles()
        favVehInvID = getSettings(AccountSettingsKeys.FAVORITES_VEHICLE)
        if favVehInvID and self._itemsCache.items.getVehicle(favVehInvID) is None:
            favVehInvID = 0
        if self.__consumeReturnFromBattle():
            favVehicle = self._itemsCache.items.getVehicle(favVehInvID) if favVehInvID else None
            if favVehicle is not None and favVehicle.intCD in modeVehicles:
                return favVehInvID
        if g_currentVehicle.intCD in modeVehicles:
            return g_currentVehicle.invID
        elif favVehInvID:
            return favVehInvID
        else:
            vehicles = sorted(modeVehicles.values(), key=vehicleComparisonKey)
            return vehicles[0].invID if vehicles else 0

    def __consumeReturnFromBattle(self):
        result = self.__returnFromLSBattle
        self.__returnFromLSBattle = False
        return result

    def __onCurrentVehicleChanged(self):
        g_eventDispatcher.updateUI()
