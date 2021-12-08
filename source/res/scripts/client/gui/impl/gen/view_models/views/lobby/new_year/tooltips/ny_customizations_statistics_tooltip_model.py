# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_customizations_statistics_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_loot_box_statistics_customization_model import NyLootBoxStatisticsCustomizationModel

class NyCustomizationsStatisticsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyCustomizationsStatisticsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCustomizations(self):
        return self._getArray(0)

    def setCustomizations(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(NyCustomizationsStatisticsTooltipModel, self)._initialize()
        self._addArrayProperty('customizations', Array())
