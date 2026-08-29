# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/fall_tanks_gui_constants.py
from __future__ import absolute_import
from constants_utils import ConstInjector
from gui.battle_control import battle_constants
from gui.impl.gen import R
from gui.Scaleform.daapi.settings import views
from shared_utils import CONST_CONTAINER
FALL_TANKS_EQUIPMENTS = ('fall_tanks_ability_dash', 'fall_tanks_ability_shield')
FALL_TANKS_SUB_MODE_IMAGES_PATH = R.images.fun_random.gui.maps.icons.feature.asset_packs.sub_modes.fall_tanks
FALL_TANKS_GUI_PROPS_NAME = 'teamFallTanks'

class BATTLE_CTRL_ID(battle_constants.BATTLE_CTRL_ID, ConstInjector):
    FALL_TANKS_BATTLE_CTRL = 201


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    FALL_TANKS_BATTLE_PAGE = 'fallTanksBattlePage'


class FallTanksTooltipConstants(CONST_CONTAINER):
    FALL_TANKS_CUSTOM_SHELLS = 'fallTanksCustomShells'
    FALL_TANKS_CUSTOM_ABILITIES = 'fallTanksCustomAbilities'
    LOBBY_TOOLTIPS_SET = (FALL_TANKS_CUSTOM_SHELLS, FALL_TANKS_CUSTOM_ABILITIES)
