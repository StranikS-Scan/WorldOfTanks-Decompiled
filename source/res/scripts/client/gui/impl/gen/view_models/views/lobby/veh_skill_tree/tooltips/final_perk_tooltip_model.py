# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/tooltips/final_perk_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.base_perk_tooltip_model import BasePerkTooltipModel

class FinalPerkTooltipModel(BasePerkTooltipModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FinalPerkTooltipModel, self).__init__(properties=properties, commands=commands)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(FinalPerkTooltipModel, self)._initialize()
        self._addStringProperty('vehicleType', '')
