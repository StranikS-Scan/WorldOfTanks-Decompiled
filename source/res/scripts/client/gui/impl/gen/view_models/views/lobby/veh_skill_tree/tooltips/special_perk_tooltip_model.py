# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/veh_skill_tree/tooltips/special_perk_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.base_perk_tooltip_model import BasePerkTooltipModel

class SpecialPerkTooltipModel(BasePerkTooltipModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SpecialPerkTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLockedVehicle(self):
        return self._getBool(2)

    def setLockedVehicle(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(SpecialPerkTooltipModel, self)._initialize()
        self._addBoolProperty('lockedVehicle', False)
