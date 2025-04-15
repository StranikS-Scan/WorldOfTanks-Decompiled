# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/fall_tanks_gui_constants.py
from constants_utils import ConstInjector
from gui.battle_control import battle_constants
from gui.impl.gen import R
from gui.Scaleform.daapi.settings import views
FALL_TANKS_EQUIPMENTS = ('fall_tanks_ability_dash', 'fall_tanks_ability_shield')
FALL_TANKS_IMAGES_PATH = R.images.fall_tanks.gui.maps.icons.feature
FALL_TANKS_GUI_PROPS_NAME = 'teamFallTanks'

class FallTanksTankSetupConstants(object):
    FALL_TANK_SHELLS = 'fallTanksShells'
    FALL_TANK_CONSUMABLES = 'fallTanksConsumables'
    FALL_TANK_INFINITE_SHELL_OVERLAY = 'fallTankInfiniteShell'


FALL_TANKS_TOOLTIPS_SET = (FallTanksTankSetupConstants.FALL_TANK_SHELLS, FallTanksTankSetupConstants.FALL_TANK_CONSUMABLES)

class BATTLE_CTRL_ID(battle_constants.BATTLE_CTRL_ID, ConstInjector):
    FALL_TANKS_BATTLE_CTRL = 201


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    FALL_TANKS_BATTLE_PAGE = 'fallTanksBattlePage'
