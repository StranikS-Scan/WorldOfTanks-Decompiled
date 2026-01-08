# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.rank_item_model import RankItemModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryBaseModel

class InfoViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=21, commands=1):
        super(InfoViewModel, self).__init__(properties=properties, commands=commands)

    def getValidVehicleLevels(self):
        return self._getArray(0)

    def setValidVehicleLevels(self, value):
        self._setArray(0, value)

    @staticmethod
    def getValidVehicleLevelsType():
        return int

    def getUnlockableInBattleVehicleLevel(self):
        return self._getNumber(1)

    def setUnlockableInBattleVehicleLevel(self, value):
        self._setNumber(1, value)

    def getIsBattlePassAvailable(self):
        return self._getBool(2)

    def setIsBattlePassAvailable(self, value):
        self._setBool(2, value)

    def getIsFullScreen(self):
        return self._getBool(3)

    def setIsFullScreen(self, value):
        self._setBool(3, value)

    def getStartTimestamp(self):
        return self._getNumber(4)

    def setStartTimestamp(self, value):
        self._setNumber(4, value)

    def getEndTimestamp(self):
        return self._getNumber(5)

    def setEndTimestamp(self, value):
        self._setNumber(5, value)

    def getSideDestructiblesArmor(self):
        return self._getNumber(6)

    def setSideDestructiblesArmor(self, value):
        self._setNumber(6, value)

    def getBackDestructiblesArmor(self):
        return self._getNumber(7)

    def setBackDestructiblesArmor(self, value):
        self._setNumber(7, value)

    def getDoorDestructiblesArmor(self):
        return self._getNumber(8)

    def setDoorDestructiblesArmor(self, value):
        self._setNumber(8, value)

    def getVentilationDestructiblesArmor(self):
        return self._getNumber(9)

    def setVentilationDestructiblesArmor(self, value):
        self._setNumber(9, value)

    def getMortarRespawnTime(self):
        return self._getNumber(10)

    def setMortarRespawnTime(self, value):
        self._setNumber(10, value)

    def getAirshipRespawnTime(self):
        return self._getNumber(11)

    def setAirshipRespawnTime(self, value):
        self._setNumber(11, value)

    def getPillboxRespawnTime(self):
        return self._getNumber(12)

    def setPillboxRespawnTime(self, value):
        self._setNumber(12, value)

    def getFlamerRespawnTime(self):
        return self._getNumber(13)

    def setFlamerRespawnTime(self, value):
        self._setNumber(13, value)

    def getAirshipCaptureDuration(self):
        return self._getNumber(14)

    def setAirshipCaptureDuration(self, value):
        self._setNumber(14, value)

    def getAirshipHullDamageFactor(self):
        return self._getReal(15)

    def setAirshipHullDamageFactor(self, value):
        self._setReal(15, value)

    def getAirshipTurretDamageFactor(self):
        return self._getReal(16)

    def setAirshipTurretDamageFactor(self, value):
        self._setReal(16, value)

    def getSkillsCategories(self):
        return self._getArray(17)

    def setSkillsCategories(self, value):
        self._setArray(17, value)

    @staticmethod
    def getSkillsCategoriesType():
        return SkillCategoryBaseModel

    def getRanksWithPoints(self):
        return self._getArray(18)

    def setRanksWithPoints(self, value):
        self._setArray(18, value)

    @staticmethod
    def getRanksWithPointsType():
        return RankItemModel

    def getWinTablePoints(self):
        return self._getArray(19)

    def setWinTablePoints(self, value):
        self._setArray(19, value)

    @staticmethod
    def getWinTablePointsType():
        return int

    def getLoseTablePoints(self):
        return self._getArray(20)

    def setLoseTablePoints(self, value):
        self._setArray(20, value)

    @staticmethod
    def getLoseTablePointsType():
        return int

    def _initialize(self):
        super(InfoViewModel, self)._initialize()
        self._addArrayProperty('validVehicleLevels', Array())
        self._addNumberProperty('unlockableInBattleVehicleLevel', 0)
        self._addBoolProperty('isBattlePassAvailable', False)
        self._addBoolProperty('isFullScreen', False)
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addNumberProperty('sideDestructiblesArmor', 0)
        self._addNumberProperty('backDestructiblesArmor', 0)
        self._addNumberProperty('doorDestructiblesArmor', 0)
        self._addNumberProperty('ventilationDestructiblesArmor', 0)
        self._addNumberProperty('mortarRespawnTime', 0)
        self._addNumberProperty('airshipRespawnTime', 0)
        self._addNumberProperty('pillboxRespawnTime', 0)
        self._addNumberProperty('flamerRespawnTime', 0)
        self._addNumberProperty('airshipCaptureDuration', 0)
        self._addRealProperty('airshipHullDamageFactor', 0.0)
        self._addRealProperty('airshipTurretDamageFactor', 0.0)
        self._addArrayProperty('skillsCategories', Array())
        self._addArrayProperty('ranksWithPoints', Array())
        self._addArrayProperty('winTablePoints', Array())
        self._addArrayProperty('loseTablePoints', Array())
        self.onClose = self._addCommand('onClose')
