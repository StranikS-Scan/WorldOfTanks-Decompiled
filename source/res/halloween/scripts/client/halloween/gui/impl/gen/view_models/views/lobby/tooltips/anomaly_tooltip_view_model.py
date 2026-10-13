# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/anomaly_tooltip_view_model.py
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.common.anomaly_model import AnomalyModel

class AnomalyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AnomalyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def anomaly(self):
        return self._getViewModel(0)

    @staticmethod
    def getAnomalyType():
        return AnomalyModel

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getSpecialInfo(self):
        return self._getString(2)

    def setSpecialInfo(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(AnomalyTooltipViewModel, self)._initialize()
        self._addViewModelProperty('anomaly', AnomalyModel())
        self._addStringProperty('description', '')
        self._addStringProperty('specialInfo', '')
