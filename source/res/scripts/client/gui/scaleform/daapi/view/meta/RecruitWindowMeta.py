# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RecruitWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RecruitWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def updateVehicleClassDropdown(self, nation):
        """
        :param nation:
        :return :
        """
        self._printOverrideError('updateVehicleClassDropdown')

    def updateVehicleTypeDropdown(self, nation, vclass):
        """
        :param nation:
        :param vclass:
        :return :
        """
        self._printOverrideError('updateVehicleTypeDropdown')

    def updateRoleDropdown(self, nation, vclass, vtype):
        """
        :param nation:
        :param vclass:
        :param vtype:
        :return :
        """
        self._printOverrideError('updateRoleDropdown')

    def updateNationDropdown(self):
        """
        :return :
        """
        self._printOverrideError('updateNationDropdown')

    def buyTankman(self, nationID, typeID, role, studyType, slot):
        """
        :param nationID:
        :param typeID:
        :param role:
        :param studyType:
        :param slot:
        :return :
        """
        self._printOverrideError('buyTankman')

    def updateAllDropdowns(self, nationID, tankType, typeID, roleType):
        """
        :param nationID:
        :param tankType:
        :param typeID:
        :param roleType:
        :return :
        """
        self._printOverrideError('updateAllDropdowns')

    def as_setVehicleClassDropdownS(self, vehicleClassData):
        """
        :param vehicleClassData:
        :return :
        """
        return self.flashObject.as_setVehicleClassDropdown(vehicleClassData) if self._isDAAPIInited() else None

    def as_setVehicleTypeDropdownS(self, vehicleTypeData):
        """
        :param vehicleTypeData:
        :return :
        """
        return self.flashObject.as_setVehicleTypeDropdown(vehicleTypeData) if self._isDAAPIInited() else None

    def as_setRoleDropdownS(self, roleData):
        """
        :param roleData:
        :return :
        """
        return self.flashObject.as_setRoleDropdown(roleData) if self._isDAAPIInited() else None

    def as_setCreditsChangedS(self, credits):
        """
        :param credits:
        :return :
        """
        return self.flashObject.as_setCreditsChanged(credits) if self._isDAAPIInited() else None

    def as_setGoldChangedS(self, gold):
        """
        :param gold:
        :return :
        """
        return self.flashObject.as_setGoldChanged(gold) if self._isDAAPIInited() else None

    def as_initDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_initData(data) if self._isDAAPIInited() else None

    def as_setNationsS(self, nationsData):
        """
        :param nationsData:
        :return :
        """
        return self.flashObject.as_setNations(nationsData) if self._isDAAPIInited() else None

    def as_setAllDropdownsS(self, nationsData, vehicleClassData, vehicleTypeData, roleData):
        """
        :param nationsData:
        :param vehicleClassData:
        :param vehicleTypeData:
        :param roleData:
        :return :
        """
        return self.flashObject.as_setAllDropdowns(nationsData, vehicleClassData, vehicleTypeData, roleData) if self._isDAAPIInited() else None
