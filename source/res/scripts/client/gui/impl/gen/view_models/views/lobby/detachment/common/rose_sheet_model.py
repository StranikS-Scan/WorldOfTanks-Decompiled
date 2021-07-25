# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/rose_sheet_model.py
from frameworks.wulf import ViewModel

class RoseSheetModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(RoseSheetModel, self).__init__(properties=properties, commands=commands)

    def getCourse(self):
        return self._getNumber(0)

    def setCourse(self, value):
        self._setNumber(0, value)

    def getProgress(self):
        return self._getNumber(1)

    def setProgress(self, value):
        self._setNumber(1, value)

    def getPlus(self):
        return self._getNumber(2)

    def setPlus(self, value):
        self._setNumber(2, value)

    def getInstructorPoints(self):
        return self._getNumber(3)

    def setInstructorPoints(self, value):
        self._setNumber(3, value)

    def getBoosterPoints(self):
        return self._getNumber(4)

    def setBoosterPoints(self, value):
        self._setNumber(4, value)

    def getIsUltimate(self):
        return self._getBool(5)

    def setIsUltimate(self, value):
        self._setBool(5, value)

    def getIconName(self):
        return self._getString(6)

    def setIconName(self, value):
        self._setString(6, value)

    def getIsHighlighted(self):
        return self._getBool(7)

    def setIsHighlighted(self, value):
        self._setBool(7, value)

    def getHasOvercappedPerk(self):
        return self._getBool(8)

    def setHasOvercappedPerk(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(RoseSheetModel, self)._initialize()
        self._addNumberProperty('course', 0)
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('plus', 0)
        self._addNumberProperty('instructorPoints', 0)
        self._addNumberProperty('boosterPoints', 0)
        self._addBoolProperty('isUltimate', False)
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isHighlighted', False)
        self._addBoolProperty('hasOvercappedPerk', False)
