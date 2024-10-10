# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_crew_model.py
from frameworks.wulf import ViewModel

class WtCrewModel(ViewModel):
    __slots__ = ('onAboutClicked',)
    SKILL_TOOLTIP = 'crewPerkGf'

    def __init__(self, properties=4, commands=1):
        super(WtCrewModel, self).__init__(properties=properties, commands=commands)

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
        super(WtCrewModel, self)._initialize()
        self._addStringProperty('tankmanID', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('invID', 0)
        self._addBoolProperty('hasSixthSense', False)
        self.onAboutClicked = self._addCommand('onAboutClicked')
