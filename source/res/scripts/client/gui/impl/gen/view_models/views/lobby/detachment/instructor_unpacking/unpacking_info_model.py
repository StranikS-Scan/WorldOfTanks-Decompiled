# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructor_unpacking/unpacking_info_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class UnpackingInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(UnpackingInfoModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIsVoiced(self):
        return self._getBool(1)

    def setIsVoiced(self, value):
        self._setBool(1, value)

    def getDescription(self):
        return self._getResource(2)

    def setDescription(self, value):
        self._setResource(2, value)

    def getGrade(self):
        return self._getNumber(3)

    def setGrade(self, value):
        self._setNumber(3, value)

    def getBonusExperience(self):
        return self._getNumber(4)

    def setBonusExperience(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(UnpackingInfoModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addBoolProperty('isVoiced', False)
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('grade', 0)
        self._addNumberProperty('bonusExperience', 0)
