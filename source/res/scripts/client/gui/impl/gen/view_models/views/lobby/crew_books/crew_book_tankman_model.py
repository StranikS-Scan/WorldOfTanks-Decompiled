# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_book_tankman_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class CrewBookTankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(CrewBookTankmanModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankmanSkillList(self):
        return self._getViewModel(0)

    def getIdx(self):
        return self._getNumber(1)

    def setIdx(self, value):
        self._setNumber(1, value)

    def getRoleIcon(self):
        return self._getResource(2)

    def setRoleIcon(self, value):
        self._setResource(2, value)

    def getTankmanIcon(self):
        return self._getResource(3)

    def setTankmanIcon(self, value):
        self._setResource(3, value)

    def getIsLowRoleLevel(self):
        return self._getBool(4)

    def setIsLowRoleLevel(self, value):
        self._setBool(4, value)

    def getIsWrongVehicle(self):
        return self._getBool(5)

    def setIsWrongVehicle(self, value):
        self._setBool(5, value)

    def getIsLearnDisable(self):
        return self._getBool(6)

    def setIsLearnDisable(self, value):
        self._setBool(6, value)

    def getIsEmpty(self):
        return self._getBool(7)

    def setIsEmpty(self, value):
        self._setBool(7, value)

    def getIsClickEnable(self):
        return self._getBool(8)

    def setIsClickEnable(self, value):
        self._setBool(8, value)

    def getIsTankamanSelected(self):
        return self._getBool(9)

    def setIsTankamanSelected(self, value):
        self._setBool(9, value)

    def getIsArrowAnimPlay(self):
        return self._getBool(10)

    def setIsArrowAnimPlay(self, value):
        self._setBool(10, value)

    def getIsSkillsEmpty(self):
        return self._getBool(11)

    def setIsSkillsEmpty(self, value):
        self._setBool(11, value)

    def getTankmanGainExp(self):
        return self._getString(12)

    def setTankmanGainExp(self, value):
        self._setString(12, value)

    def getRoleLevel(self):
        return self._getString(13)

    def setRoleLevel(self, value):
        self._setString(13, value)

    def getNativeVehicle(self):
        return self._getString(14)

    def setNativeVehicle(self, value):
        self._setString(14, value)

    def getInvID(self):
        return self._getNumber(15)

    def setInvID(self, value):
        self._setNumber(15, value)

    def getIsTooltipEnable(self):
        return self._getBool(16)

    def setIsTooltipEnable(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(CrewBookTankmanModel, self)._initialize()
        self._addViewModelProperty('tankmanSkillList', ListModel())
        self._addNumberProperty('idx', 0)
        self._addResourceProperty('roleIcon', R.invalid())
        self._addResourceProperty('tankmanIcon', R.invalid())
        self._addBoolProperty('isLowRoleLevel', False)
        self._addBoolProperty('isWrongVehicle', False)
        self._addBoolProperty('isLearnDisable', False)
        self._addBoolProperty('isEmpty', False)
        self._addBoolProperty('isClickEnable', False)
        self._addBoolProperty('isTankamanSelected', False)
        self._addBoolProperty('isArrowAnimPlay', False)
        self._addBoolProperty('isSkillsEmpty', False)
        self._addStringProperty('tankmanGainExp', '')
        self._addStringProperty('roleLevel', '')
        self._addStringProperty('nativeVehicle', '')
        self._addNumberProperty('invID', 0)
        self._addBoolProperty('isTooltipEnable', True)
