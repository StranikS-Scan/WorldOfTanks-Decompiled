# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/death_cam/death_cam_ui_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ImpactMode(Enum):
    PENETRATION = 'penetration'
    NONPENETRATIONDAMAGE = 'nonPenetrationDamage'
    LEGACYHE = 'legacyHE'
    MODERNHE = 'modernHE'


class DeathCamUiViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DeathCamUiViewModel, self).__init__(properties=properties, commands=commands)

    def getBarsVisible(self):
        return self._getBool(0)

    def setBarsVisible(self, value):
        self._setBool(0, value)

    def getIsFinalPhase(self):
        return self._getBool(1)

    def setIsFinalPhase(self, value):
        self._setBool(1, value)

    def getRemainingTime(self):
        return self._getReal(2)

    def setRemainingTime(self, value):
        self._setReal(2, value)

    def getImpactMode(self):
        return ImpactMode(self._getString(3))

    def setImpactMode(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(DeathCamUiViewModel, self)._initialize()
        self._addBoolProperty('barsVisible', False)
        self._addBoolProperty('isFinalPhase', False)
        self._addRealProperty('remainingTime', 0.0)
        self._addStringProperty('impactMode')
