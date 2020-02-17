# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileTechniqueWindow.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.profile.QueuedVehicleDossierReceiver import QueuedVehicleDossierReceiver
from gui.Scaleform.daapi.view.lobby.profile.ProfileTechnique import ProfileTechnique

class ProfileTechniqueWindow(ProfileTechnique):

    def __init__(self, *args):
        super(ProfileTechniqueWindow, self).__init__(*args)
        self.__dataReceiver = QueuedVehicleDossierReceiver()
        self.__currentlyRequestingVehicleId = None
        self.__dataReceiver.onDataReceived += self.__requestedDataReceived
        return

    def _populate(self):
        super(ProfileTechniqueWindow, self)._populate()
        self.as_setTabsDataS([{'id': 'all',
          'label': backport.text(R.strings.profile.profile.tabs.title.allTime()),
          'linkage': 'RegularItemsTabViewUI',
          'selected': True,
          'enabled': True,
          'tooltip': backport.text(R.strings.profile.profile.tabs.tooltip.forAllTime())}, {'id': 'season',
          'label': backport.text(R.strings.profile.profile.tabs.title.season()),
          'linkage': 'RegularItemsTabViewUI',
          'selected': False,
          'enabled': True,
          'tooltip': backport.text(R.strings.profile.profile.tabs.tooltip.forTime(), time='--')}])

    def requestData(self, vehicleId):
        self.as_responseVehicleDossierS(None)
        self.__currentlyRequestingVehicleId = int(vehicleId)
        self.__dataReceiver.invoke(self._databaseID, self.__currentlyRequestingVehicleId)
        return

    def invokeUpdate(self):
        super(ProfileTechniqueWindow, self).invokeUpdate()
        if self._selectedVehicleIntCD is not None:
            self._receiveVehicleDossier(self._selectedVehicleIntCD, self._databaseID)
        return

    def _dispose(self):
        self.__dataReceiver.onDataReceived -= self.__requestedDataReceived
        self.__dataReceiver.dispose()
        self.__dataReceiver = None
        super(ProfileTechniqueWindow, self)._dispose()
        return

    def _setRatingButton(self):
        self.as_setRatingButtonS({'enabled': False,
         'visible': False})

    def __requestedDataReceived(self, databaseID, vehicleID):
        if self.__currentlyRequestingVehicleId == vehicleID:
            self._receiveVehicleDossier(vehicleID, databaseID)
