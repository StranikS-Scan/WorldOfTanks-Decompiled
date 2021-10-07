# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_header_tooltip_view_model.py
from frameworks.wulf import ViewModel

class CrewHeaderTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CrewHeaderTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsActive(self):
        return self._getBool(0)

    def setIsActive(self, value):
        self._setBool(0, value)

    def getWarning(self):
        return self._getString(1)

    def setWarning(self, value):
        self._setString(1, value)

    def getBonusXpPerHour(self):
        return self._getNumber(2)

    def setBonusXpPerHour(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(CrewHeaderTooltipViewModel, self)._initialize()
        self._addBoolProperty('isActive', False)
        self._addStringProperty('warning', '')
        self._addNumberProperty('bonusXpPerHour', 50)
