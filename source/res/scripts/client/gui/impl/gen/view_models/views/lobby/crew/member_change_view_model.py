# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/member_change_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.crew.common.base_crew_view_model import BaseCrewViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel

class MemberChangeViewModel(BaseCrewViewModel):
    __slots__ = ('onResetFilters', 'onTankmanSelected', 'onRecruitSelected', 'onRecruitNewTankman', 'onTankmanRestore', 'onPlayRecruitVoiceover', 'onLoadCards')

    def __init__(self, properties=13, commands=11):
        super(MemberChangeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(2)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getHasCrew(self):
        return self._getBool(3)

    def setHasCrew(self, value):
        self._setBool(3, value)

    def getHasFilters(self):
        return self._getBool(4)

    def setHasFilters(self, value):
        self._setBool(4, value)

    def getRoleChangeDiscountPercent(self):
        return self._getNumber(5)

    def setRoleChangeDiscountPercent(self, value):
        self._setNumber(5, value)

    def getVehicle(self):
        return self._getString(6)

    def setVehicle(self, value):
        self._setString(6, value)

    def getNation(self):
        return self._getString(7)

    def setNation(self, value):
        self._setString(7, value)

    def getRequiredRole(self):
        return self._getString(8)

    def setRequiredRole(self, value):
        self._setString(8, value)

    def getItemsAmount(self):
        return self._getNumber(9)

    def setItemsAmount(self, value):
        self._setNumber(9, value)

    def getItemsOffset(self):
        return self._getNumber(10)

    def setItemsOffset(self, value):
        self._setNumber(10, value)

    def getTankmanList(self):
        return self._getArray(11)

    def setTankmanList(self, value):
        self._setArray(11, value)

    @staticmethod
    def getTankmanListType():
        return TankmanModel

    def getIsRecruitDisabled(self):
        return self._getBool(12)

    def setIsRecruitDisabled(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(MemberChangeViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addBoolProperty('hasCrew', True)
        self._addBoolProperty('hasFilters', False)
        self._addNumberProperty('roleChangeDiscountPercent', 0)
        self._addStringProperty('vehicle', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('requiredRole', '')
        self._addNumberProperty('itemsAmount', 0)
        self._addNumberProperty('itemsOffset', 0)
        self._addArrayProperty('tankmanList', Array())
        self._addBoolProperty('isRecruitDisabled', False)
        self.onResetFilters = self._addCommand('onResetFilters')
        self.onTankmanSelected = self._addCommand('onTankmanSelected')
        self.onRecruitSelected = self._addCommand('onRecruitSelected')
        self.onRecruitNewTankman = self._addCommand('onRecruitNewTankman')
        self.onTankmanRestore = self._addCommand('onTankmanRestore')
        self.onPlayRecruitVoiceover = self._addCommand('onPlayRecruitVoiceover')
        self.onLoadCards = self._addCommand('onLoadCards')
