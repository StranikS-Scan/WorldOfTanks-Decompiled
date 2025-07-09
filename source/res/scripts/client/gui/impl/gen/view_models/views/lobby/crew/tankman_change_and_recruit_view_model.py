# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tankman_change_and_recruit_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.vehicle_item_view_model import VehicleItemViewModel
from gui.impl.gen.view_models.views.lobby.crew.drop_down_item_view_model import DropDownItemViewModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_change_model import TankmanChangeModel

class TankmanChangeAndRecruitViewModel(ViewModel):
    __slots__ = ('onNameChange', 'onSurnameChange', 'onNationChange', 'onVehChange', 'onVehTypeChange', 'onRetrainingChange', 'onSpecialtyChange', 'onViewClose', 'onTankmanPhotoChange', 'onTankmanUpdate', 'onSetInVehChange', 'onRecruit')

    def __init__(self, properties=21, commands=12):
        super(TankmanChangeAndRecruitViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentTankman(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentTankmanType():
        return TankmanChangeModel

    @property
    def futureTankman(self):
        return self._getViewModel(1)

    @staticmethod
    def getFutureTankmanType():
        return TankmanChangeModel

    def getIsRecruit(self):
        return self._getBool(2)

    def setIsRecruit(self, value):
        self._setBool(2, value)

    def getIsNameCanBeChanged(self):
        return self._getBool(3)

    def setIsNameCanBeChanged(self, value):
        self._setBool(3, value)

    def getIsPhotoLocked(self):
        return self._getBool(4)

    def setIsPhotoLocked(self, value):
        self._setBool(4, value)

    def getInitialIcon(self):
        return self._getResource(5)

    def setInitialIcon(self, value):
        self._setResource(5, value)

    def getRetraining(self):
        return self._getString(6)

    def setRetraining(self, value):
        self._setString(6, value)

    def getCredits(self):
        return self._getNumber(7)

    def setCredits(self, value):
        self._setNumber(7, value)

    def getSpecialtyGold(self):
        return self._getNumber(8)

    def setSpecialtyGold(self, value):
        self._setNumber(8, value)

    def getRetrainingGold(self):
        return self._getNumber(9)

    def setRetrainingGold(self, value):
        self._setNumber(9, value)

    def getIsEnoughCredits(self):
        return self._getBool(10)

    def setIsEnoughCredits(self, value):
        self._setBool(10, value)

    def getIsEnoughGold(self):
        return self._getBool(11)

    def setIsEnoughGold(self, value):
        self._setBool(11, value)

    def getIsShowCheckBox(self):
        return self._getBool(12)

    def setIsShowCheckBox(self, value):
        self._setBool(12, value)

    def getIsCheckBoxSelected(self):
        return self._getBool(13)

    def setIsCheckBoxSelected(self, value):
        self._setBool(13, value)

    def getNations(self):
        return self._getArray(14)

    def setNations(self, value):
        self._setArray(14, value)

    @staticmethod
    def getNationsType():
        return DropDownItemViewModel

    def getVehTypes(self):
        return self._getArray(15)

    def setVehTypes(self, value):
        self._setArray(15, value)

    @staticmethod
    def getVehTypesType():
        return DropDownItemViewModel

    def getNames(self):
        return self._getArray(16)

    def setNames(self, value):
        self._setArray(16, value)

    @staticmethod
    def getNamesType():
        return DropDownItemViewModel

    def getSurnames(self):
        return self._getArray(17)

    def setSurnames(self, value):
        self._setArray(17, value)

    @staticmethod
    def getSurnamesType():
        return DropDownItemViewModel

    def getVehicles(self):
        return self._getArray(18)

    def setVehicles(self, value):
        self._setArray(18, value)

    @staticmethod
    def getVehiclesType():
        return VehicleItemViewModel

    def getRetrainings(self):
        return self._getArray(19)

    def setRetrainings(self, value):
        self._setArray(19, value)

    @staticmethod
    def getRetrainingsType():
        return DropDownItemViewModel

    def getSpecialties(self):
        return self._getArray(20)

    def setSpecialties(self, value):
        self._setArray(20, value)

    @staticmethod
    def getSpecialtiesType():
        return DropDownItemViewModel

    def _initialize(self):
        super(TankmanChangeAndRecruitViewModel, self)._initialize()
        self._addViewModelProperty('currentTankman', TankmanChangeModel())
        self._addViewModelProperty('futureTankman', TankmanChangeModel())
        self._addBoolProperty('isRecruit', False)
        self._addBoolProperty('isNameCanBeChanged', True)
        self._addBoolProperty('isPhotoLocked', False)
        self._addResourceProperty('initialIcon', R.invalid())
        self._addStringProperty('retraining', '')
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('specialtyGold', 0)
        self._addNumberProperty('retrainingGold', 0)
        self._addBoolProperty('isEnoughCredits', False)
        self._addBoolProperty('isEnoughGold', False)
        self._addBoolProperty('isShowCheckBox', False)
        self._addBoolProperty('isCheckBoxSelected', False)
        self._addArrayProperty('nations', Array())
        self._addArrayProperty('vehTypes', Array())
        self._addArrayProperty('names', Array())
        self._addArrayProperty('surnames', Array())
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('retrainings', Array())
        self._addArrayProperty('specialties', Array())
        self.onNameChange = self._addCommand('onNameChange')
        self.onSurnameChange = self._addCommand('onSurnameChange')
        self.onNationChange = self._addCommand('onNationChange')
        self.onVehChange = self._addCommand('onVehChange')
        self.onVehTypeChange = self._addCommand('onVehTypeChange')
        self.onRetrainingChange = self._addCommand('onRetrainingChange')
        self.onSpecialtyChange = self._addCommand('onSpecialtyChange')
        self.onViewClose = self._addCommand('onViewClose')
        self.onTankmanPhotoChange = self._addCommand('onTankmanPhotoChange')
        self.onTankmanUpdate = self._addCommand('onTankmanUpdate')
        self.onSetInVehChange = self._addCommand('onSetInVehChange')
        self.onRecruit = self._addCommand('onRecruit')
