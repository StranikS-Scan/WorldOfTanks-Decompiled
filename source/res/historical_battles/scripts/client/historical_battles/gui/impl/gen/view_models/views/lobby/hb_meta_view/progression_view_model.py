# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/progression_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_quests_model import BattleQuestsModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.mark_detail_model import MarkDetailModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.progress_level_model import ProgressLevelModel

class ProgressionState(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'


class ProgressionViewModel(ViewModel):
    __slots__ = ('onPreviewClicked', 'onVehicleBuyClicked', 'onShowVideoClicked')

    def __init__(self, properties=10, commands=3):
        super(ProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def battleQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getBattleQuestsType():
        return BattleQuestsModel

    def getFrontName(self):
        return self._getString(1)

    def setFrontName(self, value):
        self._setString(1, value)

    def getState(self):
        return ProgressionState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getCurProgressPoints(self):
        return self._getNumber(3)

    def setCurProgressPoints(self, value):
        self._setNumber(3, value)

    def getPrevProgressPoints(self):
        return self._getNumber(4)

    def setPrevProgressPoints(self, value):
        self._setNumber(4, value)

    def getVehicleDiscount(self):
        return self._getNumber(5)

    def setVehicleDiscount(self, value):
        self._setNumber(5, value)

    def getHasVehicle(self):
        return self._getBool(6)

    def setHasVehicle(self, value):
        self._setBool(6, value)

    def getPointsForLevel(self):
        return self._getArray(7)

    def setPointsForLevel(self, value):
        self._setArray(7, value)

    @staticmethod
    def getPointsForLevelType():
        return int

    def getProgressLevels(self):
        return self._getArray(8)

    def setProgressLevels(self, value):
        self._setArray(8, value)

    @staticmethod
    def getProgressLevelsType():
        return ProgressLevelModel

    def getMarksDetails(self):
        return self._getArray(9)

    def setMarksDetails(self, value):
        self._setArray(9, value)

    @staticmethod
    def getMarksDetailsType():
        return MarkDetailModel

    def _initialize(self):
        super(ProgressionViewModel, self)._initialize()
        self._addViewModelProperty('battleQuests', BattleQuestsModel())
        self._addStringProperty('frontName', '')
        self._addStringProperty('state')
        self._addNumberProperty('curProgressPoints', 0)
        self._addNumberProperty('prevProgressPoints', 0)
        self._addNumberProperty('vehicleDiscount', 0)
        self._addBoolProperty('hasVehicle', False)
        self._addArrayProperty('pointsForLevel', Array())
        self._addArrayProperty('progressLevels', Array())
        self._addArrayProperty('marksDetails', Array())
        self.onPreviewClicked = self._addCommand('onPreviewClicked')
        self.onVehicleBuyClicked = self._addCommand('onVehicleBuyClicked')
        self.onShowVideoClicked = self._addCommand('onShowVideoClicked')
