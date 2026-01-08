# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/meta_view/pages/progression_model.py
from enum import IntEnum
from comp7.gui.impl.gen.view_models.views.lobby.enums import StatisticsMode
from frameworks.wulf import Array
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.customization_tasks_model import CustomizationTasksModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.day_statistics_model import DayStatisticsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.season_statistics_model import SeasonStatisticsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.top_vehicle_statistics_model import TopVehicleStatisticsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_base_model import ProgressionBaseModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.progression_qualification_model import ProgressionQualificationModel
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_model import ProgressionItemModel

class PageState(IntEnum):
    INITIAL = 0
    SUCCESS = 1
    ERROR = 2


class ProgressionModel(ProgressionBaseModel):
    __slots__ = ('onSelectDay', 'onOpenCustomization', 'onCustomizationProgressShown', 'onOpenVehicleStats', 'onRefresh')
    DEFAULT_SELECTED_DAY = -1

    def __init__(self, properties=19, commands=5):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    @property
    def qualificationModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getQualificationModelType():
        return ProgressionQualificationModel

    @property
    def seasonStatisticsModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getSeasonStatisticsModelType():
        return SeasonStatisticsModel

    def getCurrentScore(self):
        return self._getNumber(4)

    def setCurrentScore(self, value):
        self._setNumber(4, value)

    def getLastBestUserPointsValue(self):
        return self._getNumber(5)

    def setLastBestUserPointsValue(self, value):
        self._setNumber(5, value)

    def getIsLastBestUserPointsValueLoading(self):
        return self._getBool(6)

    def setIsLastBestUserPointsValueLoading(self, value):
        self._setBool(6, value)

    def getLeaderboardUpdateTimestamp(self):
        return self._getNumber(7)

    def setLeaderboardUpdateTimestamp(self, value):
        self._setNumber(7, value)

    def getRankInactivityCount(self):
        return self._getNumber(8)

    def setRankInactivityCount(self, value):
        self._setNumber(8, value)

    def getItems(self):
        return self._getArray(9)

    def setItems(self, value):
        self._setArray(9, value)

    @staticmethod
    def getItemsType():
        return ProgressionItemModel

    def getPageState(self):
        return PageState(self._getNumber(10))

    def setPageState(self, value):
        self._setNumber(10, value.value)

    def getStatisticsMode(self):
        return StatisticsMode(self._getNumber(11))

    def setStatisticsMode(self, value):
        self._setNumber(11, value.value)

    def getIsStatisticsLoading(self):
        return self._getBool(12)

    def setIsStatisticsLoading(self, value):
        self._setBool(12, value)

    def getStatisticsUpdateTimestamp(self):
        return self._getNumber(13)

    def setStatisticsUpdateTimestamp(self, value):
        self._setNumber(13, value)

    def getCurrentDayIndex(self):
        return self._getNumber(14)

    def setCurrentDayIndex(self, value):
        self._setNumber(14, value)

    def getSelectedDayIndex(self):
        return self._getNumber(15)

    def setSelectedDayIndex(self, value):
        self._setNumber(15, value)

    def getStatisticsByDay(self):
        return self._getArray(16)

    def setStatisticsByDay(self, value):
        self._setArray(16, value)

    @staticmethod
    def getStatisticsByDayType():
        return DayStatisticsModel

    def getTopVehiclesStatistics(self):
        return self._getArray(17)

    def setTopVehiclesStatistics(self, value):
        self._setArray(17, value)

    @staticmethod
    def getTopVehiclesStatisticsType():
        return TopVehicleStatisticsModel

    def getCustomizationTasks(self):
        return self._getArray(18)

    def setCustomizationTasks(self, value):
        self._setArray(18, value)

    @staticmethod
    def getCustomizationTasksType():
        return CustomizationTasksModel

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addViewModelProperty('qualificationModel', ProgressionQualificationModel())
        self._addViewModelProperty('seasonStatisticsModel', SeasonStatisticsModel())
        self._addNumberProperty('currentScore', 0)
        self._addNumberProperty('lastBestUserPointsValue', 0)
        self._addBoolProperty('isLastBestUserPointsValueLoading', False)
        self._addNumberProperty('leaderboardUpdateTimestamp', 0)
        self._addNumberProperty('rankInactivityCount', -1)
        self._addArrayProperty('items', Array())
        self._addNumberProperty('pageState')
        self._addNumberProperty('statisticsMode')
        self._addBoolProperty('isStatisticsLoading', False)
        self._addNumberProperty('statisticsUpdateTimestamp', 0)
        self._addNumberProperty('currentDayIndex', 0)
        self._addNumberProperty('selectedDayIndex', -1)
        self._addArrayProperty('statisticsByDay', Array())
        self._addArrayProperty('topVehiclesStatistics', Array())
        self._addArrayProperty('customizationTasks', Array())
        self.onSelectDay = self._addCommand('onSelectDay')
        self.onOpenCustomization = self._addCommand('onOpenCustomization')
        self.onCustomizationProgressShown = self._addCommand('onCustomizationProgressShown')
        self.onOpenVehicleStats = self._addCommand('onOpenVehicleStats')
        self.onRefresh = self._addCommand('onRefresh')
