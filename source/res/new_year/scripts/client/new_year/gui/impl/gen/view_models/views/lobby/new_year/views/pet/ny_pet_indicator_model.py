# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet/ny_pet_indicator_model.py
from frameworks.wulf import Array
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_indicator_type import NyIndicatorType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_item_leaderboard_point import NyPetItemLeaderboardPoint

class NyPetIndicatorModel(NyIndicatorType):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(NyPetIndicatorModel, self).__init__(properties=properties, commands=commands)

    def getMaxPoint(self):
        return self._getNumber(1)

    def setMaxPoint(self, value):
        self._setNumber(1, value)

    def getCurPoint(self):
        return self._getNumber(2)

    def setCurPoint(self, value):
        self._setNumber(2, value)

    def getPotentialCurPoint(self):
        return self._getNumber(3)

    def setPotentialCurPoint(self, value):
        self._setNumber(3, value)

    def getScaleLevels(self):
        return self._getArray(4)

    def setScaleLevels(self, value):
        self._setArray(4, value)

    @staticmethod
    def getScaleLevelsType():
        return int

    def getItemCount(self):
        return self._getNumber(5)

    def setItemCount(self, value):
        self._setNumber(5, value)

    def getItemScalePoint(self):
        return self._getNumber(6)

    def setItemScalePoint(self, value):
        self._setNumber(6, value)

    def getItemLeaderboardPoint(self):
        return self._getArray(7)

    def setItemLeaderboardPoint(self, value):
        self._setArray(7, value)

    @staticmethod
    def getItemLeaderboardPointType():
        return NyPetItemLeaderboardPoint

    def getScaleDowngradeTime(self):
        return self._getReal(8)

    def setScaleDowngradeTime(self, value):
        self._setReal(8, value)

    def getScaleEmptyTime(self):
        return self._getReal(9)

    def setScaleEmptyTime(self, value):
        self._setReal(9, value)

    def getIsLocked(self):
        return self._getBool(10)

    def setIsLocked(self, value):
        self._setBool(10, value)

    def getLettersToUnlock(self):
        return self._getNumber(11)

    def setLettersToUnlock(self, value):
        self._setNumber(11, value)

    def getIsLoading(self):
        return self._getBool(12)

    def setIsLoading(self, value):
        self._setBool(12, value)

    def getBonus(self):
        return self._getNumber(13)

    def setBonus(self, value):
        self._setNumber(13, value)

    def getWasOverflowed(self):
        return self._getBool(14)

    def setWasOverflowed(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(NyPetIndicatorModel, self)._initialize()
        self._addNumberProperty('maxPoint', 0)
        self._addNumberProperty('curPoint', 0)
        self._addNumberProperty('potentialCurPoint', 0)
        self._addArrayProperty('scaleLevels', Array())
        self._addNumberProperty('itemCount', 0)
        self._addNumberProperty('itemScalePoint', 0)
        self._addArrayProperty('itemLeaderboardPoint', Array())
        self._addRealProperty('scaleDowngradeTime', 0.0)
        self._addRealProperty('scaleEmptyTime', 0.0)
        self._addBoolProperty('isLocked', False)
        self._addNumberProperty('lettersToUnlock', 0)
        self._addBoolProperty('isLoading', False)
        self._addNumberProperty('bonus', 0)
        self._addBoolProperty('wasOverflowed', False)
