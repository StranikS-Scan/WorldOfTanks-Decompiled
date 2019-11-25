# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_header_reserve_model.py
from frameworks.wulf import ViewModel

class PremDashboardHeaderReserveModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PremDashboardHeaderReserveModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getProgress(self):
        return self._getNumber(1)

    def setProgress(self, value):
        self._setNumber(1, value)

    def getTimeleft(self):
        return self._getNumber(2)

    def setTimeleft(self, value):
        self._setNumber(2, value)

    def getIconId(self):
        return self._getString(3)

    def setIconId(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(PremDashboardHeaderReserveModel, self)._initialize()
        self._addNumberProperty('id', -1)
        self._addNumberProperty('progress', -1)
        self._addNumberProperty('timeleft', -1)
        self._addStringProperty('iconId', '')
