# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/sub_views/stepper_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class StepperSize(Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'


class StepperViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(StepperViewModel, self).__init__(properties=properties, commands=commands)

    def getMinValue(self):
        return self._getNumber(0)

    def setMinValue(self, value):
        self._setNumber(0, value)

    def getMaxValue(self):
        return self._getNumber(1)

    def setMaxValue(self, value):
        self._setNumber(1, value)

    def getStep(self):
        return self._getNumber(2)

    def setStep(self, value):
        self._setNumber(2, value)

    def getValue(self):
        return self._getNumber(3)

    def setValue(self, value):
        self._setNumber(3, value)

    def getSize(self):
        return StepperSize(self._getString(4))

    def setSize(self, value):
        self._setString(4, value.value)

    def getWidth(self):
        return self._getNumber(5)

    def setWidth(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(StepperViewModel, self)._initialize()
        self._addNumberProperty('minValue', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('step', 1)
        self._addNumberProperty('value', 1)
        self._addStringProperty('size')
        self._addNumberProperty('width', 0)
