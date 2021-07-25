# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/constants.py
import typing
from enum import Enum
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_columns import ModeSelectorColumns
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
DEFAULT_COLUMN = ModeSelectorColumns.COLUMN_2
DEFAULT_PRIORITY = -1

class CustomModeName(object):
    BOOTCAMP = 'bootcamp'
    DEFAULT = 'default'


COLUMN_SETTINGS = {PREBATTLE_ACTION_NAME.RANDOM: (ModeSelectorColumns.COLUMN_0, -1),
 PREBATTLE_ACTION_NAME.MAPBOX: (ModeSelectorColumns.COLUMN_1, 10),
 PREBATTLE_ACTION_NAME.RANKED: (ModeSelectorColumns.COLUMN_2, 10),
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE: (ModeSelectorColumns.COLUMN_2, 20),
 PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST: (ModeSelectorColumns.COLUMN_3, 10),
 PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST: (ModeSelectorColumns.COLUMN_3, 20),
 PREBATTLE_ACTION_NAME.TRAININGS_LIST: (ModeSelectorColumns.COLUMN_3, 30),
 PREBATTLE_ACTION_NAME.MAPS_TRAINING: (ModeSelectorColumns.COLUMN_3, 40),
 CustomModeName.BOOTCAMP: (ModeSelectorColumns.COLUMN_3, 50),
 CustomModeName.DEFAULT: (ModeSelectorColumns.COLUMN_2, 50)}

class ModeSelectorRewardID(Enum):
    BONES = 'bones'
    BOUNTY_EQUIPMENT = 'bountyEquipment'
    CREDITS = 'credits'
    CREW = 'crew'
    EXPERIENCE = 'experience'
    IMPROVED_EQUIPMENT = 'improvedEquipment'
    OTHER = 'other'
    STYLE = 'style'
    VEHICLE = 'vehicle'
