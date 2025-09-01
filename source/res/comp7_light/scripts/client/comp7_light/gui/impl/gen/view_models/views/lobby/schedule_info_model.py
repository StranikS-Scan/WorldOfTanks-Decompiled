# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/schedule_info_model.py
from frameworks.wulf import ViewModel
from comp7_light.gui.impl.gen.view_models.views.lobby.season_model import SeasonModel
from comp7_light.gui.impl.gen.view_models.views.lobby.year_model import YearModel

class ScheduleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ScheduleInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def year(self):
        return self._getViewModel(0)

    @staticmethod
    def getYearType():
        return YearModel

    @property
    def season(self):
        return self._getViewModel(1)

    @staticmethod
    def getSeasonType():
        return SeasonModel

    def getTooltipId(self):
        return self._getString(2)

    def setTooltipId(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ScheduleInfoModel, self)._initialize()
        self._addViewModelProperty('year', YearModel())
        self._addViewModelProperty('season', SeasonModel())
        self._addStringProperty('tooltipId', '')
