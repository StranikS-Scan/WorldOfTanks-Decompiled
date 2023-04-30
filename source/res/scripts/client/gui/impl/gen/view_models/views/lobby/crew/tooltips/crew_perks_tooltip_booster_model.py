# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/crew_perks_tooltip_booster_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PerkImpactType(Enum):
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'


class CrewPerksTooltipBoosterModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CrewPerksTooltipBoosterModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getText(self):
        return self._getString(1)

    def setText(self, value):
        self._setString(1, value)

    def getImpact(self):
        return self._getString(2)

    def setImpact(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(CrewPerksTooltipBoosterModel, self)._initialize()
        self._addStringProperty('value', '')
        self._addStringProperty('text', '')
        self._addStringProperty('impact', '')
