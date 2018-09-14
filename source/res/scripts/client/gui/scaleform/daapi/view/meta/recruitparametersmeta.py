# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RecruitParametersMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RecruitParametersMeta(BaseDAAPIComponent):

    def onNationChanged(self, nationID):
        self._printOverrideError('onNationChanged')

    def onVehicleClassChanged(self, vehClass):
        self._printOverrideError('onVehicleClassChanged')

    def onVehicleChanged(self, vehID):
        self._printOverrideError('onVehicleChanged')

    def onTankmanRoleChanged(self, roleID):
        self._printOverrideError('onTankmanRoleChanged')

    def as_setVehicleClassDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleClassData(data)

    def as_setVehicleDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setVehicleData(data)

    def as_setTankmanRoleDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setTankmanRoleData(data)

    def as_setNationsDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setNationsData(data)
