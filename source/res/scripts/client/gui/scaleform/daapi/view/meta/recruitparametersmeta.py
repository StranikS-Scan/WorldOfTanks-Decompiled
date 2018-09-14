# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RecruitParametersMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RecruitParametersMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def onNationChanged(self, nationID):
        self._printOverrideError('onNationChanged')

    def onVehicleClassChanged(self, vehClass):
        self._printOverrideError('onVehicleClassChanged')

    def onVehicleChanged(self, vehID):
        self._printOverrideError('onVehicleChanged')

    def onTankmanRoleChanged(self, roleID):
        self._printOverrideError('onTankmanRoleChanged')

    def as_setVehicleClassDataS(self, data):
        """
        :param data: Represented by RecruitParametersVO (AS)
        """
        return self.flashObject.as_setVehicleClassData(data) if self._isDAAPIInited() else None

    def as_setVehicleDataS(self, data):
        """
        :param data: Represented by RecruitParametersVO (AS)
        """
        return self.flashObject.as_setVehicleData(data) if self._isDAAPIInited() else None

    def as_setTankmanRoleDataS(self, data):
        """
        :param data: Represented by RecruitParametersVO (AS)
        """
        return self.flashObject.as_setTankmanRoleData(data) if self._isDAAPIInited() else None

    def as_setNationsDataS(self, data):
        """
        :param data: Represented by RecruitParametersVO (AS)
        """
        return self.flashObject.as_setNationsData(data) if self._isDAAPIInited() else None
