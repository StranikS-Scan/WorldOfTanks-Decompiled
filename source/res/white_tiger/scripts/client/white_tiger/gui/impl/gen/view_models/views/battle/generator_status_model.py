# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/battle/generator_status_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class GeneratorStatusEnum(Enum):
    ACTIVE = 'active'
    LOCKED = 'locked'
    DESTROYED = 'destroyed'


class GeneratorStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(GeneratorStatusModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getProgress(self):
        return self._getNumber(1)

    def setProgress(self, value):
        self._setNumber(1, value)

    def getGeneratorStatus(self):
        return GeneratorStatusEnum(self._getString(2))

    def setGeneratorStatus(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(GeneratorStatusModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('progress', 0)
        self._addStringProperty('generatorStatus', GeneratorStatusEnum.ACTIVE.value)
