# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechniqueWindow.py
from gui.Scaleform.daapi.view.lobby.profile.QueuedVehicleDossierReceiver import QueuedVehicleDossierReceiver
from gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique import ProfileTechnique

class ProfileTechniqueWindow(ProfileTechnique):

    def __init__(self, *args):
        super(ProfileTechniqueWindow, self).__init__(*args)
        self.__dataReceiver = QueuedVehicleDossierReceiver()
        self.__currentlyRequestingVehicleId = None
        self.__dataReceiver.onDataReceived += self.__requestedDataReceived
        return

    def __requestedDataReceived(self, databaseID, vehicleID):
        if self.__currentlyRequestingVehicleId == vehicleID:
            self._receiveVehicleDossier(vehicleID, databaseID)

    def requestData(self, data):
        self.as_responseVehicleDossierS(None)
        self.__currentlyRequestingVehicleId = data.vehicleId
        self.__dataReceiver.invoke(self._databaseID, self.__currentlyRequestingVehicleId)
        return

    def _dispose(self):
        self.__dataReceiver.onDataReceived -= self.__requestedDataReceived
        self.__dataReceiver.dispose()
        self.__dataReceiver = None
        super(ProfileTechniqueWindow, self)._dispose()
        return
