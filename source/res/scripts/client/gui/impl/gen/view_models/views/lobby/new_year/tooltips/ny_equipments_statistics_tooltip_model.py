# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_equipments_statistics_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_equipment_statistics_model import NyEquipmentStatisticsModel

class NyEquipmentsStatisticsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyEquipmentsStatisticsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEquipments(self):
        return self._getArray(0)

    def setEquipments(self, value):
        self._setArray(0, value)

    @staticmethod
    def getEquipmentsType():
        return NyEquipmentStatisticsModel

    def _initialize(self):
        super(NyEquipmentsStatisticsTooltipModel, self)._initialize()
        self._addArrayProperty('equipments', Array())
