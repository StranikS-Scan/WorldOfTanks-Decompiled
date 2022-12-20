# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/dt_component.py
from frameworks.wulf import ViewModel

class DtComponent(ViewModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(DtComponent, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getIsLocked(self):
        return self._getBool(2)

    def setIsLocked(self, value):
        self._setBool(2, value)

    def getPurpose(self):
        return self._getString(3)

    def setPurpose(self, value):
        self._setString(3, value)

    def getCurrentGradeValue(self):
        return self._getReal(4)

    def setCurrentGradeValue(self, value):
        self._setReal(4, value)

    def getNextGradeValue(self):
        return self._getReal(5)

    def setNextGradeValue(self, value):
        self._setReal(5, value)

    def getCurrentGrade(self):
        return self._getNumber(6)

    def setCurrentGrade(self, value):
        self._setNumber(6, value)

    def getCurrentProgress(self):
        return self._getReal(7)

    def setCurrentProgress(self, value):
        self._setReal(7, value)

    def getProgressNumberType(self):
        return self._getString(8)

    def setProgressNumberType(self, value):
        self._setString(8, value)

    def getIsNew(self):
        return self._getBool(9)

    def setIsNew(self, value):
        self._setBool(9, value)

    def getDisplayableProgress(self):
        return self._getString(10)

    def setDisplayableProgress(self, value):
        self._setString(10, value)

    def getIsDeprecated(self):
        return self._getBool(11)

    def setIsDeprecated(self, value):
        self._setBool(11, value)

    def getIsExternalUnlockOnly(self):
        return self._getBool(12)

    def setIsExternalUnlockOnly(self, value):
        self._setBool(12, value)

    def getIsDemoted(self):
        return self._getBool(13)

    def setIsDemoted(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(DtComponent, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('type', '')
        self._addBoolProperty('isLocked', False)
        self._addStringProperty('purpose', '')
        self._addRealProperty('currentGradeValue', 0.0)
        self._addRealProperty('nextGradeValue', 0.0)
        self._addNumberProperty('currentGrade', 0)
        self._addRealProperty('currentProgress', 0.0)
        self._addStringProperty('progressNumberType', '')
        self._addBoolProperty('isNew', False)
        self._addStringProperty('displayableProgress', '')
        self._addBoolProperty('isDeprecated', False)
        self._addBoolProperty('isExternalUnlockOnly', False)
        self._addBoolProperty('isDemoted', False)
