# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/AvatarVehiclesInfoBase.py
import BigWorld
from collections import namedtuple
VehInfoDiffBufferEntry = namedtuple('VehInfoDiffBufferEntry', ('new', 'prev'))

class AvatarVehiclesInfoBase(BigWorld.DynamicScriptComponent):
    SET_VEH_INFO_FMT = 'setVehInfo_{}'

    def __init__(self):
        super(AvatarVehiclesInfoBase, self).__init__()
        self._isOwnedByPlayer = self.avatar.id == self.entity.avatarID
        self.__arena = self.avatar.arena
        self.__diffBuffer = {}
        if self._isOwnedByPlayer:
            self.__arena.updateVehiclesList(self.vehiclesInfo)

    @property
    def avatar(self):
        return BigWorld.player()

    def setNested_vehiclesInfo(self, changePath, prev):
        if not self._isOwnedByPlayer:
            return
        elif changePath[1] != '__generation':
            self.__diffBuffer[changePath[1]] = VehInfoDiffBufferEntry(self.vehiclesInfo[changePath[0]][changePath[1]], prev)
            return
        else:
            vehInfoIndex = changePath[0]
            vehInfo = self.vehiclesInfo[vehInfoIndex]
            self._updateVehicleInfo(vehInfo, self.__diffBuffer)
            for attrName, diff in self.__diffBuffer.items():
                if diff.prev is None or diff.new is None:
                    continue
                setter = getattr(self, self.SET_VEH_INFO_FMT.format(attrName), None)
                if setter is not None:
                    setter(vehInfo, self.__diffBuffer.pop(attrName))

            if self.__diffBuffer:
                self._onVehicleUpdated(vehInfo)
            self.__diffBuffer.clear()
            return

    def setSlice_vehiclesInfo(self, changePath, prev):
        if not self._isOwnedByPlayer:
            return
        begin, end = changePath[0]
        for vehInfo in self.vehiclesInfo[begin:end]:
            self.__arena.addVehInfo(vehInfo)

    def setVehInfo_isAlive(self, vehInfo, diff):
        vehID = vehInfo['vehicleID']
        self.__arena.updateVehicleIsAlive(vehID, vehInfo['compDescr'], self.avatar.playerVehicleID == vehID)

    def setVehInfo_isTeamKiller(self, vehInfo, diff):
        self.__arena.updateVehicleIsTeamKiller(vehInfo['vehicleID'])

    def setVehInfo_isAvatarReady(self, vehInfo, diff):
        self.__arena.updateVehicleIsAvatarReady(vehInfo['vehicleID'])

    def _updateVehicleInfo(self, vehInfo, diffBuffer):
        self.__arena.updateVehicleInfo(vehInfo['vehicleID'], {name:vehInfo[name] for name in diffBuffer})

    def _onVehicleUpdated(self, vehInfo):
        self.__arena.onVehicleUpdated(vehInfo['vehicleID'])
