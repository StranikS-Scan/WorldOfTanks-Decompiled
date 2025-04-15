# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/__init__.py
from gui.shared.system_factory import registerIngameHelpPagesFilters, registerPostmortemInfoView
from fall_tanks_constants import ARENA_GUI_TYPE
from fall_tanks.gui.battle_control.fall_tanks_battle_constants import injectConsts
from fall_tanks.gui.impl.battle.battle_page.fall_tanks_postmortem_info_view import FallTanksPostmortemInfoView
from fall_tanks.gui.ingame_help.fall_tanks_pages import FallTanksHelpPagesFilter

def registerFallTanksBattle(personality):
    injectConsts(personality)
    registerIngameHelpPagesFilters(ARENA_GUI_TYPE.FALL_TANKS, FallTanksHelpPagesFilter)
    registerPostmortemInfoView(ARENA_GUI_TYPE.FALL_TANKS, FallTanksPostmortemInfoView)
