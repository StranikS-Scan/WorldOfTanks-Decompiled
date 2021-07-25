# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/detachment_setup_vehicle.py
import typing
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.shared import IItemsCache
from items.components.detachment_constants import NO_DETACHMENT_ID
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class _DetachmentTankSetupVehicle(object):
    __slots__ = ('__vehicle', '__vehicleToCompare', '__backupedBonusPerks', '__currentDetachmentID', '__comparableInstructors')
    _itemsCache = dependency.descriptor(IItemsCache)
    _detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self):
        super(_DetachmentTankSetupVehicle, self).__init__()
        self.__vehicle = None
        self.__vehicleToCompare = None
        self.__backupedBonusPerks = None
        self.__comparableInstructors = []
        self.__currentDetachmentID = NO_DETACHMENT_ID
        return

    def setCurrentDetachment(self, detachmentID=NO_DETACHMENT_ID):
        self.__currentDetachmentID = detachmentID

    @property
    def currentDetachmentID(self):
        return self.__currentDetachmentID

    @property
    def comparableInstructors(self):
        return self.__comparableInstructors

    def addComparableInstructorID(self, instrInvID):
        self.__comparableInstructors.append(instrInvID)

    def removeComparableInstructorID(self, instrInvID):
        if instrInvID in self.__comparableInstructors:
            self.__comparableInstructors.remove(instrInvID)

    def getPerkPointsWithExtraBonus(self, perkID):
        detachment = self._detachmentCache.getDetachment(self.__currentDetachmentID)
        return detachment.build.get(perkID, 0) + self.__backupedBonusPerks[perkID] if detachment and perkID in self.__backupedBonusPerks else None

    def setVehicleBonusPerks(self, bonusPerks, comparableInstructor=False, callback=None):
        if not self.defaultItem:
            return
        else:
            if not callback and bonusPerks is not None:
                self.__backupedBonusPerks = bonusPerks.copy()
            if bonusPerks or comparableInstructor:
                self.setCompareVehicle(self._itemsCache.items.getVehicleCopy(self.defaultItem))
                self.__vehicleToCompare.initPerksController(self.__currentDetachmentID, bonusPerks=bonusPerks, comparableInstructors=self.__comparableInstructors if comparableInstructor else [])
                perksController = self.__vehicleToCompare.getPerksController()
                if not perksController.isEnabled() and callback:
                    perksController.recalc(True)
                    perksController.setOnStartCallback(callback)
            else:
                self.setCompareVehicle(None)
            return

    def setBonusDetachment(self, detachmentID):
        if self.defaultItem:
            self.setCompareVehicle(self._itemsCache.items.getVehicleCopy(self.defaultItem))
            self.__vehicleToCompare.initPerksController(detachmentID)
        else:
            self.setCompareVehicle(None)
        return

    def setCompareVehicle(self, value, runPerks=False):
        if self.__vehicleToCompare:
            self.__vehicleToCompare.stopPerksController()
        self.__vehicleToCompare = value
        if runPerks:
            self.__vehicleToCompare.initPerksController(self.defaultItem.getLinkedDetachmentID())

    def restoreCurrentVehicle(self):
        if g_currentVehicle.isPresent():
            currentDetachmentID = g_currentVehicle.item.getLinkedDetachmentID()
            self.setCurrentDetachment(currentDetachmentID)
            self.setVehicle(g_currentVehicle.item)

    def restoreCompareVehicle(self):
        if not self.defaultItem:
            return
        else:
            self.setVehicleBonusPerks(self.__backupedBonusPerks)
            if not self.__vehicleToCompare:
                return
            perksController = self.__vehicleToCompare.getPerksController()
            if not perksController.isEnabled():
                perksController.recalc(True)
                perksController.setOnStartCallback(None)
            return

    def setVehicle(self, value):
        self.__backupedBonusPerks = {}
        if self.__vehicle:
            self.__vehicle.stopPerksController()
        self.setCompareVehicle(None)
        self.__vehicle = self._itemsCache.items.getItemByCD(value.descriptor.type.compactDescr) if value else None
        if self.__vehicle:
            self.__vehicle.initPerksController(self.__currentDetachmentID)
        return

    def getBackupedBonusPerks(self):
        return self.__backupedBonusPerks

    def calculateForVehicle(self, vehicle, callback, useLinkedDetachment=False):
        if useLinkedDetachment:
            currentDetachmentID = vehicle.getLinkedDetachmentID()
            g_detachmentTankSetupVehicle.setCurrentDetachment(currentDetachmentID)
        g_detachmentTankSetupVehicle.setVehicle(vehicle)
        perksController = g_detachmentTankSetupVehicle.item.getPerksController()
        if not perksController.isEnabled():
            perksController.recalc(True)
            perksController.setOnStartCallback(callback)
            return True
        return False

    def updateVehicle(self):
        self.setVehicle(self.__vehicle)

    @property
    def item(self):
        return self.vehicleToCompare or self.defaultItem

    @property
    def vehicleToCompare(self):
        return self.__vehicleToCompare

    @property
    def defaultItem(self):
        return self.__vehicle if self.__vehicle and self.__vehicle.getPerksController() else g_currentVehicle.item

    def isPresent(self):
        return self.__vehicle is not None

    def dispose(self):
        if self.__vehicle:
            self.__vehicle.stopPerksController()
        self.__vehicle = None
        self.setCompareVehicle(None)
        return


g_detachmentTankSetupVehicle = _DetachmentTankSetupVehicle()
