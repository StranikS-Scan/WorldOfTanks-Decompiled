# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/halloween_gui_constants.py
from constants_utils import ConstInjector
from gui.prb_control import settings

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    HALLOWEEN_BATTLE = 'halloween'
    HALLOWEEN_BATTLE_SQUAD = 'halloweenSquad'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    HALLOWEEN_BATTLE = 4294967296L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    HALLOWEEN_BATTLE = 'HalloweenBattle'


class HW_EQUIPMENT(object):
    FIRE_ARROW = 'hwVehicleFireArrow'
    CURSE_ARROW = 'hwVehicleCurseArrow'
    FROZEN_ARROW = 'hwVehicleFrozenArrow'
    HEALING_ARROW = 'hwVehicleHealingArrow'
    LAUGH_ARROW = 'hwVehicleLaughArrow'
