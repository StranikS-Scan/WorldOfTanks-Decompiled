# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/customization_zone/customization_zone_panel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.customization_zone.customization_zone_model import CustomizationZoneModel

class CustomizationZonePanelModel(ViewModel):
    __slots__ = ('onClick', 'onNextLevel')

    def __init__(self, properties=1, commands=2):
        super(CustomizationZonePanelModel, self).__init__(properties=properties, commands=commands)

    def getCustomizationZones(self):
        return self._getArray(0)

    def setCustomizationZones(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCustomizationZonesType():
        return CustomizationZoneModel

    def _initialize(self):
        super(CustomizationZonePanelModel, self)._initialize()
        self._addArrayProperty('customizationZones', Array())
        self.onClick = self._addCommand('onClick')
        self.onNextLevel = self._addCommand('onNextLevel')
