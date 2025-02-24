# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/parameters_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from cosmic_event.gui.impl.gen.view_models.views.lobby.tooltips.specification_tooltip_model import SpecificationTooltipModel

class ParameterEnum(Enum):
    STABILITY = 'stability'
    ACCELERATION = 'acceleration'
    MAX_SPEED = 'maxSpeed'
    FIRE_RATE = 'fireRate'
    SHOT_POWER = 'shotPower'


class ParametersModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ParametersModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(0)

    def setValue(self, value):
        self._setNumber(0, value)

    def getParameterName(self):
        return ParameterEnum(self._getString(1))

    def setParameterName(self, value):
        self._setString(1, value.value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getParameterDesc(self):
        return self._getString(3)

    def setParameterDesc(self, value):
        self._setString(3, value)

    def getTooltipArgs(self):
        return self._getArray(4)

    def setTooltipArgs(self, value):
        self._setArray(4, value)

    @staticmethod
    def getTooltipArgsType():
        return SpecificationTooltipModel

    def _initialize(self):
        super(ParametersModel, self)._initialize()
        self._addNumberProperty('value', 0)
        self._addStringProperty('parameterName')
        self._addStringProperty('icon', '')
        self._addStringProperty('parameterDesc', '')
        self._addArrayProperty('tooltipArgs', Array())
