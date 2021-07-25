# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/instructor_info_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.instructor_base_model import InstructorBaseModel

class InstructorInfoModel(InstructorBaseModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(InstructorInfoModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(4)

    def setName(self, value):
        self._setString(4, value)

    def getIsVoiced(self):
        return self._getBool(5)

    def setIsVoiced(self, value):
        self._setBool(5, value)

    def getTrait(self):
        return self._getResource(6)

    def setTrait(self, value):
        self._setResource(6, value)

    def getNation(self):
        return self._getString(7)

    def setNation(self, value):
        self._setString(7, value)

    def getGender(self):
        return self._getString(8)

    def setGender(self, value):
        self._setString(8, value)

    def getBonusExperience(self):
        return self._getNumber(9)

    def setBonusExperience(self, value):
        self._setNumber(9, value)

    def getLocation(self):
        return self._getString(10)

    def setLocation(self, value):
        self._setString(10, value)

    def getIsUnique(self):
        return self._getBool(11)

    def setIsUnique(self, value):
        self._setBool(11, value)

    def getState(self):
        return self._getString(12)

    def setState(self, value):
        self._setString(12, value)

    def getRemoveTime(self):
        return self._getNumber(13)

    def setRemoveTime(self, value):
        self._setNumber(13, value)

    def _initialize(self):
        super(InstructorInfoModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addBoolProperty('isVoiced', False)
        self._addResourceProperty('trait', R.invalid())
        self._addStringProperty('nation', '')
        self._addStringProperty('gender', '')
        self._addNumberProperty('bonusExperience', 0)
        self._addStringProperty('location', '')
        self._addBoolProperty('isUnique', False)
        self._addStringProperty('state', '')
        self._addNumberProperty('removeTime', 0)
