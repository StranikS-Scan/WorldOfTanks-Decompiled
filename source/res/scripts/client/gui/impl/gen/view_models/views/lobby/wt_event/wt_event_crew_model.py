# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_crew_model.py
from frameworks.wulf import ViewModel

class WtEventCrewModel(ViewModel):
    __slots__ = ('onEscKeyDown',)
    SKILL_TOOLTIP = 'crewPerkGf'

    def __init__(self, properties=4, commands=1):
        super(WtEventCrewModel, self).__init__(properties=properties, commands=commands)

    def getTankmanID(self):
        return self._getString(0)

    def setTankmanID(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getInvID(self):
        return self._getNumber(2)

    def setInvID(self, value):
        self._setNumber(2, value)

    def getHasSixthSense(self):
        return self._getBool(3)

    def setHasSixthSense(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WtEventCrewModel, self)._initialize()
        self._addStringProperty('tankmanID', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('invID', 0)
        self._addBoolProperty('hasSixthSense', False)
        self.onEscKeyDown = self._addCommand('onEscKeyDown')
