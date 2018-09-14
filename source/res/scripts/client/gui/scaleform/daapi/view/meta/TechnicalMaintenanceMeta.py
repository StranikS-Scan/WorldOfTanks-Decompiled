# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TechnicalMaintenanceMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class TechnicalMaintenanceMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def getEquipment(self, id1, currency1, id2, currency2, id3, currency3, installSlotIndex):
        self._printOverrideError('getEquipment')

    def repair(self):
        self._printOverrideError('repair')

    def setRefillSettings(self, vehicleCompact, repair, shells, equipment):
        self._printOverrideError('setRefillSettings')

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        self._printOverrideError('fillVehicle')

    def updateEquipmentCurrency(self, equipmentIndex, currency):
        self._printOverrideError('updateEquipmentCurrency')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setEquipmentS(self, installed, setup, modules):
        return self.flashObject.as_setEquipment(installed, setup, modules) if self._isDAAPIInited() else None

    def as_onAmmoInstallS(self):
        return self.flashObject.as_onAmmoInstall() if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_resetEquipmentS(self, equipmentCD):
        return self.flashObject.as_resetEquipment(equipmentCD) if self._isDAAPIInited() else None
