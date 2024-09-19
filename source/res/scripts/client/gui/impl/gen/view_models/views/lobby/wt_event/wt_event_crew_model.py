# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_crew_model.py
from frameworks.wulf import ViewModel

class WtEventCrewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WtEventCrewModel, self).__init__(properties=properties, commands=commands)

    def getTankmanID(self):
        return self._getString(0)

    def setTankmanID(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(WtEventCrewModel, self)._initialize()
        self._addStringProperty('tankmanID', '')
        self._addStringProperty('name', '')
