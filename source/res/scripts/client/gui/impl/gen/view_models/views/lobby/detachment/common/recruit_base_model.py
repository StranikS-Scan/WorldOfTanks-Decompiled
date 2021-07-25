# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/recruit_base_model.py
from frameworks.wulf import ViewModel

class RecruitBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(RecruitBaseModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getSpecialization(self):
        return self._getString(4)

    def setSpecialization(self, value):
        self._setString(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getHasCrewSkin(self):
        return self._getBool(6)

    def setHasCrewSkin(self, value):
        self._setBool(6, value)

    def getEndRestoreTime(self):
        return self._getNumber(7)

    def setEndRestoreTime(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(RecruitBaseModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('specialization', '')
        self._addStringProperty('nation', '')
        self._addBoolProperty('hasCrewSkin', False)
        self._addNumberProperty('endRestoreTime', 0)
