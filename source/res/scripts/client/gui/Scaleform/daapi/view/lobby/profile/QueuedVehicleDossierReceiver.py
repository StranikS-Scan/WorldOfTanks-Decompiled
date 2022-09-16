# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/QueuedVehicleDossierReceiver.py
from Event import Event
from adisp import adisp_process
from debug_utils import LOG_ERROR
from helpers import dependency
from skeletons.gui.shared import IItemsCache
MIN_INTERVAL_BETWEEN_INVOKES = 300

class QueuedVehicleDossierReceiver(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(QueuedVehicleDossierReceiver, self).__init__()
        self.__isUnderRequesting = False
        self.__queuedVehicleData = None
        self.__lastInvokeTime = 0
        self.onDataReceived = Event()
        return

    def invoke(self, databaseID, vehicleID):
        if self.__isUnderRequesting:
            self.__queuedVehicleData = (databaseID, vehicleID)
        else:
            self.__requestData(databaseID, vehicleID)

    @adisp_process
    def __requestData(self, databaseID, vehicleID):
        self.__isUnderRequesting = True
        vehDossier = yield self.itemsCache.items.requestUserVehicleDossier(int(databaseID), vehicleID)
        if vehDossier:
            self.onDataReceived(databaseID, vehicleID)
        else:
            LOG_ERROR("Couldn't receive vehicle dossier! Vehicle id: " + vehicleID + ', User id: ' + databaseID)
        self.__isUnderRequesting = False
        if self.__queuedVehicleData is not None:
            dbId = self.__queuedVehicleData[0]
            vehId = self.__queuedVehicleData[1]
            self.__queuedVehicleData = None
            self.invoke(dbId, vehId)
        return

    def dispose(self):
        self.__queuedVehicleData = None
        return
