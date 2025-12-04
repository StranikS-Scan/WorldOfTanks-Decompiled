# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/customization_zone/customization_level_up_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.customization_zone.customization_zone_model import CustomizationZoneModel

class CustomizationLevelUpModel(CustomizationZoneModel):
    __slots__ = ('onLevelUp', 'onClose')

    def __init__(self, properties=11, commands=2):
        super(CustomizationLevelUpModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CustomizationLevelUpModel, self)._initialize()
        self.onLevelUp = self._addCommand('onLevelUp')
        self.onClose = self._addCommand('onClose')
