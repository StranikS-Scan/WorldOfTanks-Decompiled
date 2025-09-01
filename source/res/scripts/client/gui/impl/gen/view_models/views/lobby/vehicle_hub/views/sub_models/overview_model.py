# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/overview_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.vehicle_mechanic_model import VehicleMechanicModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.slot_model import SlotModel

class BenefitsEnum(Enum):
    EXPERIENCE = 'experience'
    CREDITS = 'credits'
    CREWS_TRAIN = 'crewsTrain'
    REPAIR_KIT = 'repairKit'
    BONDS = 'bonds'


class OverviewModel(ViewModel):
    __slots__ = ('onWatchMechanicsVideo',)

    def __init__(self, properties=5, commands=1):
        super(OverviewModel, self).__init__(properties=properties, commands=commands)

    def getMechanics(self):
        return self._getArray(0)

    def setMechanics(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMechanicsType():
        return VehicleMechanicModel

    def getHistoricalReference(self):
        return self._getString(1)

    def setHistoricalReference(self, value):
        self._setString(1, value)

    def getCustomDescription(self):
        return self._getString(2)

    def setCustomDescription(self, value):
        self._setString(2, value)

    def getCrew(self):
        return self._getArray(3)

    def setCrew(self, value):
        self._setArray(3, value)

    @staticmethod
    def getCrewType():
        return SlotModel

    def getBenefits(self):
        return self._getArray(4)

    def setBenefits(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBenefitsType():
        return BenefitsEnum

    def _initialize(self):
        super(OverviewModel, self)._initialize()
        self._addArrayProperty('mechanics', Array())
        self._addStringProperty('historicalReference', '')
        self._addStringProperty('customDescription', '')
        self._addArrayProperty('crew', Array())
        self._addArrayProperty('benefits', Array())
        self.onWatchMechanicsVideo = self._addCommand('onWatchMechanicsVideo')
