# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/arena_components/comp7_equipment_component.py
from comp7_core.arena_components.comp7_core_equipment_component import Comp7CoreEquipmentComponent, _AoeHealEffect
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class _Comp7AoeHealEffect(_AoeHealEffect):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller


class Comp7EquipmentComponent(Comp7CoreEquipmentComponent):
    _AOE_HEAL_EFFECT = _Comp7AoeHealEffect
