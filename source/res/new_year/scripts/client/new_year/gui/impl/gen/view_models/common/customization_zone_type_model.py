# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/common/customization_zone_type_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CustomizationZone(Enum):
    FIR = 'Fir'
    LIGHTS = 'Lights'
    INSTALLATIONS = 'Installations'
    FAIR = 'Fair'
    SKATING = 'Skating'
    ATTRACTIONS = 'Attractions'


class CustomizationZoneTypeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(CustomizationZoneTypeModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return CustomizationZone(self._getString(0))

    def setValue(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(CustomizationZoneTypeModel, self)._initialize()
        self._addStringProperty('value', CustomizationZone.FIR.value)
