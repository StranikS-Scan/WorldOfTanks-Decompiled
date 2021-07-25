# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PerkContextClientImpl.py
import weakref
from helpers import dependency
from visual_script.misc import ASPECT
from skeletons.gui.shared import IItemsCache

class VehicleProxy(object):

    def __init__(self, vehicleID):
        self.vehicleID = vehicleID


class PerkContextClientImpl(object):
    itemsCache = dependency.descriptor(IItemsCache)
    ASPECT = ASPECT.CLIENT

    def __init__(self, perksControllerWeakRef, perkID, perkLevel, scopeID):
        self.perkID = perkID
        self.perkLevel = perkLevel
        self.scopeID = scopeID
        self.vehicleID = perksControllerWeakRef.vehicleID
        self._vehicleProxy = VehicleProxy(self.vehicleID)

    @property
    def controller(self):
        from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
        vehicleID = self.vehicle.vehicleID
        if g_detachmentTankSetupVehicle.item and g_detachmentTankSetupVehicle.item.descriptor.type.compactDescr == vehicleID:
            return g_detachmentTankSetupVehicle.item.getPerksController()
        vehicle = self.itemsCache.items.getItemByCD(vehicleID)
        perksController = vehicle.getPerksController()
        if perksController is None:
            vehicle.initPerksController(vehicle.getLinkedDetachmentID())
            return vehicle.getPerksController()
        else:
            return perksController

    @property
    def vehicle(self):
        return weakref.proxy(self._vehicleProxy)

    def addFactorModifier(self, factor, value):
        self.controller.modifyFactor(factor, self.scopeID, self.perkID, value)

    def removeFactorModifiers(self, factor, numMods):
        if numMods > 0:
            self.controller.removeNumFactorModifiers(factor, self.scopeID, self.perkID, numMods)
        else:
            self.controller.dropFactorModifiers(factor, self.scopeID, self.perkID)

    def dropAllPerkModifiers(self):
        self.controller.dropAllPerkModifiers(self.scopeID, self.perkID)

    def setCanSeeDamagedDevices(self, *_):
        pass

    def startPerkNotify(self):
        self.controller.startPerkNotify(self.scopeID, self.perkID)

    def addAuraModifier(self, *_):
        pass

    def startAura(self, *_):
        pass

    def setAuraRange(self, *_):
        pass

    def notifyOnClient(self, *_):
        pass

    def notifyOnClientRibbon(self, *_):
        pass

    def setAmmoChangeFactorForVehicle(self, *_):
        pass
