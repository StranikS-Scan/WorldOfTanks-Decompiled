# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/progression_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.progression_item_model import ProgressionItemModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_base_model import ProgressionBaseModel
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.progression_qualification_model import ProgressionQualificationModel

class ProgressionModel(ProgressionBaseModel):
    __slots__ = ('onLeaderboardLinkClick',)

    def __init__(self, properties=9, commands=1):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    @property
    def qualificationModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getQualificationModelType():
        return ProgressionQualificationModel

    def getCurrentScore(self):
        return self._getNumber(2)

    def setCurrentScore(self, value):
        self._setNumber(2, value)

    def getLastBestUserPointsValue(self):
        return self._getNumber(3)

    def setLastBestUserPointsValue(self, value):
        self._setNumber(3, value)

    def getLeaderboardUpdateTimestamp(self):
        return self._getNumber(4)

    def setLeaderboardUpdateTimestamp(self, value):
        self._setNumber(4, value)

    def getIsLastBestUserPointsValueLoading(self):
        return self._getBool(5)

    def setIsLastBestUserPointsValueLoading(self, value):
        self._setBool(5, value)

    def getRankInactivityCount(self):
        return self._getNumber(6)

    def setRankInactivityCount(self, value):
        self._setNumber(6, value)

    def getMyPosition(self):
        return self._getNumber(7)

    def setMyPosition(self, value):
        self._setNumber(7, value)

    def getItems(self):
        return self._getArray(8)

    def setItems(self, value):
        self._setArray(8, value)

    @staticmethod
    def getItemsType():
        return ProgressionItemModel

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addViewModelProperty('qualificationModel', ProgressionQualificationModel())
        self._addNumberProperty('currentScore', 0)
        self._addNumberProperty('lastBestUserPointsValue', 0)
        self._addNumberProperty('leaderboardUpdateTimestamp', 0)
        self._addBoolProperty('isLastBestUserPointsValueLoading', False)
        self._addNumberProperty('rankInactivityCount', -1)
        self._addNumberProperty('myPosition', -1)
        self._addArrayProperty('items', Array())
        self.onLeaderboardLinkClick = self._addCommand('onLeaderboardLinkClick')
