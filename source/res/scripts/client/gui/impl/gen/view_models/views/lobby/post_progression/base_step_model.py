# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/base_step_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.post_progression.restrictions_model import RestrictionsModel

class ActionType(Enum):
    MODIFICATION = 'modification'
    PAIRMODIFICATION = 'pairModification'
    MODIFICATIONWITHFEATURE = 'modificationWithFeature'


class ActionState(Enum):
    PERSISTENT = 'persistent'
    SELECTABLE = 'selectable'
    CHANGEABLE = 'changeable'


class StepState(Enum):
    RESTRICTED = 'restricted'
    UNAVAILABLELOCKED = 'unavailableLocked'
    AVAILABLEPURCHASE = 'availablePurchase'
    RECEIVED = 'received'


class BaseStepModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BaseStepModel, self).__init__(properties=properties, commands=commands)

    @property
    def restrictions(self):
        return self._getViewModel(0)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getActionType(self):
        return ActionType(self._getString(3))

    def setActionType(self, value):
        self._setString(3, value.value)

    def getActionState(self):
        return ActionState(self._getString(4))

    def setActionState(self, value):
        self._setString(4, value.value)

    def getStepState(self):
        return StepState(self._getString(5))

    def setStepState(self, value):
        self._setString(5, value.value)

    def _initialize(self):
        super(BaseStepModel, self)._initialize()
        self._addViewModelProperty('restrictions', RestrictionsModel())
        self._addNumberProperty('id', 0)
        self._addBoolProperty('isDisabled', False)
        self._addStringProperty('actionType')
        self._addStringProperty('actionState')
        self._addStringProperty('stepState')
