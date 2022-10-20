# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/event_banner_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.phase_tooltip_item_model import PhaseTooltipItemModel

class PerformanceRiskEnum(Enum):
    LOWRISK = 'lowRisk'
    MEDIUMRISK = 'mediumRisk'
    HIGHRISK = 'highRisk'


class EventBannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(EventBannerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getIsPost(self):
        return self._getBool(2)

    def setIsPost(self, value):
        self._setBool(2, value)

    def getPerformanceRisk(self):
        return PerformanceRiskEnum(self._getString(3))

    def setPerformanceRisk(self, value):
        self._setString(3, value.value)

    def getPhases(self):
        return self._getArray(4)

    def setPhases(self, value):
        self._setArray(4, value)

    @staticmethod
    def getPhasesType():
        return PhaseTooltipItemModel

    def _initialize(self):
        super(EventBannerTooltipModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('isPost', False)
        self._addStringProperty('performanceRisk')
        self._addArrayProperty('phases', Array())
