# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/tooltips/progression_table_tooltip_model.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from frameworks.wulf import Array
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_base_model import ProgressionBaseModel
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_model import ProgressionItemModel

class ProgressionTableTooltipModel(ProgressionBaseModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(ProgressionTableTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSeasonName(self):
        return SeasonName(self._getString(2))

    def setSeasonName(self, value):
        self._setString(2, value.value)

    def getCurrentScore(self):
        return self._getNumber(3)

    def setCurrentScore(self, value):
        self._setNumber(3, value)

    def getRankInactivityCount(self):
        return self._getNumber(4)

    def setRankInactivityCount(self, value):
        self._setNumber(4, value)

    def getRankInactivityPointsCount(self):
        return self._getNumber(5)

    def setRankInactivityPointsCount(self, value):
        self._setNumber(5, value)

    def getEarnedRankInactivityPerBattle(self):
        return self._getNumber(6)

    def setEarnedRankInactivityPerBattle(self, value):
        self._setNumber(6, value)

    def getItems(self):
        return self._getArray(7)

    def setItems(self, value):
        self._setArray(7, value)

    @staticmethod
    def getItemsType():
        return ProgressionItemModel

    def _initialize(self):
        super(ProgressionTableTooltipModel, self)._initialize()
        self._addStringProperty('seasonName')
        self._addNumberProperty('currentScore', 0)
        self._addNumberProperty('rankInactivityCount', -1)
        self._addNumberProperty('rankInactivityPointsCount', 0)
        self._addNumberProperty('earnedRankInactivityPerBattle', 0)
        self._addArrayProperty('items', Array())
