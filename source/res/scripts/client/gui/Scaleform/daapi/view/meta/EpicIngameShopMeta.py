# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicIngameShopMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EpicIngameShopMeta(BaseDAAPIComponent):

    def getEquipment(self, id1, currency1, id2, currency2, id3, currency3, installSlotIndex, vehicleID):
        self._printOverrideError('getEquipment')

    def showModuleInfo(self, moduleId):
        self._printOverrideError('showModuleInfo')

    def fillVehicle(self, vehicleID, shells, equipment):
        self._printOverrideError('fillVehicle')

    def resetState(self, vehicleID):
        self._printOverrideError('resetState')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setEquipmentS(self, installed, setup, modules):
        return self.flashObject.as_setEquipment(installed, setup, modules) if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None

    def as_resetEquipmentS(self, equipmentCD):
        return self.flashObject.as_resetEquipment(equipmentCD) if self._isDAAPIInited() else None
