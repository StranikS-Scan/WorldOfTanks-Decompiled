# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/tooltips/base_perk_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.kpi_model import KpiModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.node_model import NodeModel

class BasePerkTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BasePerkTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def node(self):
        return self._getViewModel(0)

    @staticmethod
    def getNodeType():
        return NodeModel

    def getKpis(self):
        return self._getArray(1)

    def setKpis(self, value):
        self._setArray(1, value)

    @staticmethod
    def getKpisType():
        return KpiModel

    def _initialize(self):
        super(BasePerkTooltipModel, self)._initialize()
        self._addViewModelProperty('node', NodeModel())
        self._addArrayProperty('kpis', Array())
