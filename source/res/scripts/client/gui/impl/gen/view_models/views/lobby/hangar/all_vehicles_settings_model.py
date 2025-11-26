# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/all_vehicles_settings_model.py
from frameworks.wulf import ViewModel

class AllVehiclesSettingsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(AllVehiclesSettingsModel, self).__init__(properties=properties, commands=commands)

    def getCrewEnabled(self):
        return self._getBool(0)

    def setCrewEnabled(self, value):
        self._setBool(0, value)

    def getTtcEnabled(self):
        return self._getBool(1)

    def setTtcEnabled(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(AllVehiclesSettingsModel, self)._initialize()
        self._addBoolProperty('crewEnabled', False)
        self._addBoolProperty('ttcEnabled', False)
