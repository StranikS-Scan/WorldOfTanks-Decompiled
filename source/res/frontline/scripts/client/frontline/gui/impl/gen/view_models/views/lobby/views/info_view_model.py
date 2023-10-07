# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.rank_item_model import RankItemModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryBaseModel

class InfoViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=12, commands=1):
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

    def getSkillsCategories(self):
        return self._getArray(10)

    def setSkillsCategories(self, value):
        self._setArray(10, value)

    @staticmethod
    def getSkillsCategoriesType():
        return SkillCategoryBaseModel

    def getRanksWithPoints(self):
        return self._getArray(11)

    def setRanksWithPoints(self, value):
        self._setArray(11, value)

    @staticmethod
    def getRanksWithPointsType():
        return RankItemModel

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
        self._addArrayProperty('skillsCategories', Array())
        self._addArrayProperty('ranksWithPoints', Array())
        self.onClose = self._addCommand('onClose')
