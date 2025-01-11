# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/grinch_damage_indicator_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class DamageIndicatorTypeEnum(Enum):
    NONE = 'none'
    PENETRATION = 'penetration'
    RICOCHET = 'ricochet'


class GrinchDamageIndicatorModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(GrinchDamageIndicatorModel, self).__init__(properties=properties, commands=commands)

    def getAngle(self):
        return self._getReal(0)

    def setAngle(self, value):
        self._setReal(0, value)

    def getType(self):
        return DamageIndicatorTypeEnum(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(GrinchDamageIndicatorModel, self)._initialize()
        self._addRealProperty('angle', 0.0)
        self._addStringProperty('type', DamageIndicatorTypeEnum.NONE.value)
