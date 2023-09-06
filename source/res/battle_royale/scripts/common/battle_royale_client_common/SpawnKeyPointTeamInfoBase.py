# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/common/battle_royale_client_common/SpawnKeyPointTeamInfoBase.py
import Event

class SpawnKeyPointTeamInfoBase(object):

    def __init__(self):
        super(SpawnKeyPointTeamInfoBase, self).__init__()
        self.__placed = self.isVehiclePlaced()
        self.__em = em = Event.EventManager()
        self.onReceiveAvailableSpawnKeyPoints = Event.Event(em)
        self.onReceiveTeamSpawnKeyPoints = Event.Event(em)
        self.onReceiveSpawnKeyPointsCloseTime = Event.Event(em)
        self.onCloseChooseSpawnKeyPointsWindow = Event.Event(em)

    def _avatar(self):
        pass

    def onDestroy(self):
        self.__em.clear()

    def _doLog(self, msg):
        pass

    def set_availableSpawnKeyPoints(self, prev):
        self.onReceiveAvailableSpawnKeyPoints(self.availableSpawnKeyPoints)

    def set_teamSpawnKeyPoints(self, prev):
        if self.__placed:
            return
        self.__placed = self.isVehiclePlaced()
        if self.__placed:
            self.onCloseChooseSpawnKeyPointsWindow()
            return
        self.onReceiveTeamSpawnKeyPoints(self.teamSpawnKeyPoints)

    def set_spawnKeyPointsCloseTime(self, prev):
        self.onReceiveSpawnKeyPointsCloseTime(self.spawnKeyPointsCloseTime)

    @property
    def placed(self):
        return self.__placed

    def isVehiclePlaced(self):
        vehicleID = self._avatar().playerVehicleID
        for keyPoint in self.teamSpawnKeyPoints:
            if keyPoint.vehID == vehicleID:
                return keyPoint.placed

        return False
