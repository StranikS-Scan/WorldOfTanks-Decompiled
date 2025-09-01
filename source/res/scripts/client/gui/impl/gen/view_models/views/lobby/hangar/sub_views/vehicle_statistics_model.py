# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/vehicle_statistics_model.py
from frameworks.wulf import Map, ViewModel
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_statistic_model import VehicleStatisticModel

class VehicleStatisticsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(VehicleStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getStatistics(self):
        return self._getMap(0)

    def setStatistics(self, value):
        self._setMap(0, value)

    @staticmethod
    def getStatisticsType():
        return (unicode, VehicleStatisticModel)

    def _initialize(self):
        super(VehicleStatisticsModel, self)._initialize()
        self._addMapProperty('statistics', Map(unicode, VehicleStatisticModel))
