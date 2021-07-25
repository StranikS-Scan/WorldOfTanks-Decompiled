# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/post_progression_base_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel
from gui.impl.gen.view_models.views.lobby.post_progression.post_progression_grid_model import PostProgressionGridModel

class ProgressionAvailability(Enum):
    AVAILABLE = 'available'
    UNAVAILABLEELITE = 'unavailableElite'
    UNAVAILABLEPURCHASE = 'unavailablePurchase'
    UNAVAILABLERENT = 'unavailableRent'
    UNAVAILABLERENTOVER = 'unavailableRentOver'
    UNAVAILABLEBATTLE = 'unavailableBattle'
    UNAVAILABLEFORMATION = 'unavailableFormation'
    UNAVAILABLEBREAKER = 'unavailableBreaker'
    UNAVAILABLEBROKEN = 'unavailableBroken'


class ProgressionState(Enum):
    INITIAL = 'initial'
    TRANSITIONAL = 'transitional'
    FINAL = 'final'


class PostProgressionBaseViewModel(ViewModel):
    __slots__ = ('onViewRendered',)

    def __init__(self, properties=5, commands=1):
        super(PostProgressionBaseViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def grid(self):
        return self._getViewModel(0)

    @property
    def persistentBonuses(self):
        return self._getViewModel(1)

    def getProgressionAvailability(self):
        return ProgressionAvailability(self._getString(2))

    def setProgressionAvailability(self, value):
        self._setString(2, value.value)

    def getProgressionState(self):
        return ProgressionState(self._getString(3))

    def setProgressionState(self, value):
        self._setString(3, value.value)

    def getVehicleRole(self):
        return self._getString(4)

    def setVehicleRole(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(PostProgressionBaseViewModel, self)._initialize()
        self._addViewModelProperty('grid', PostProgressionGridModel())
        self._addViewModelProperty('persistentBonuses', BonusesModel())
        self._addStringProperty('progressionAvailability')
        self._addStringProperty('progressionState')
        self._addStringProperty('vehicleRole', '')
        self.onViewRendered = self._addCommand('onViewRendered')
