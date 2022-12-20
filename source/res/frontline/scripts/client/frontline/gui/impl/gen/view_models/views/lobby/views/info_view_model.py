# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.rank_item_model import RankItemModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryBaseModel

class InfoViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=7, commands=1):
        super(InfoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsNinthLevelEnabled(self):
        return self._getBool(0)

    def setIsNinthLevelEnabled(self, value):
        self._setBool(0, value)

    def getIsBattlePassAvailable(self):
        return self._getBool(1)

    def setIsBattlePassAvailable(self, value):
        self._setBool(1, value)

    def getIsFullScreen(self):
        return self._getBool(2)

    def setIsFullScreen(self, value):
        self._setBool(2, value)

    def getStartTimestamp(self):
        return self._getNumber(3)

    def setStartTimestamp(self, value):
        self._setNumber(3, value)

    def getEndTimestamp(self):
        return self._getNumber(4)

    def setEndTimestamp(self, value):
        self._setNumber(4, value)

    def getSkillsCategories(self):
        return self._getArray(5)

    def setSkillsCategories(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSkillsCategoriesType():
        return SkillCategoryBaseModel

    def getRanksWithPoints(self):
        return self._getArray(6)

    def setRanksWithPoints(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRanksWithPointsType():
        return RankItemModel

    def _initialize(self):
        super(InfoViewModel, self)._initialize()
        self._addBoolProperty('isNinthLevelEnabled', False)
        self._addBoolProperty('isBattlePassAvailable', False)
        self._addBoolProperty('isFullScreen', False)
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addArrayProperty('skillsCategories', Array())
        self._addArrayProperty('ranksWithPoints', Array())
        self.onClose = self._addCommand('onClose')
