# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/crosshair/plugins.py
import typing
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import GunMarkersInvalidatePlugin
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO

def createPlugins():
    return {'gunMarkersInvalidate': HBGunMarkersInvalidatePlugin}


class HBGunMarkersInvalidatePlugin(GunMarkersInvalidatePlugin, IArenaVehiclesController):
    __slots__ = ('__playerVehicleCD',)

    def __init__(self, parentObj):
        super(HBGunMarkersInvalidatePlugin, self).__init__(parentObj)
        self.__playerVehicleCD = None
        return

    def start(self):
        super(HBGunMarkersInvalidatePlugin, self).start()
        self.sessionProvider.addArenaCtrl(self)

    def stop(self):
        self.__playerVehicleCD = None
        self.sessionProvider.removeArenaCtrl(self)
        super(HBGunMarkersInvalidatePlugin, self).stop()
        return

    def updateVehiclesInfo(self, updated, arenaDP):
        for _, vInfoVO in updated:
            if vInfoVO.isPlayerVehicle():
                self.__updateCurrentVehicle(vInfoVO)
                break

    def __updateCurrentVehicle(self, vInfoVO):
        prevPlayerVehicleCD, self.__playerVehicleCD = self.__playerVehicleCD, vInfoVO.vehicleType.compactDescr
        if prevPlayerVehicleCD and prevPlayerVehicleCD != self.__playerVehicleCD:
            self.__invalidateGunMarkers(vInfoVO)

    def __invalidateGunMarkers(self, vInfoVO):
        repository = self.sessionProvider.shared
        if not repository.vehicleState.isInPostmortem:
            markersInfo = repository.crosshair.getGunMarkersSetInfo()
            self._parentObj.invalidateGunMarkers(markersInfo, vInfoVO)
