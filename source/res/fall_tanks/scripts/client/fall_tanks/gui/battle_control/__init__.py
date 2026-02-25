# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/__init__.py
from __future__ import absolute_import
from gui.shared.system_factory import registerPostmortemInfoView
from fall_tanks_constants import ARENA_GUI_TYPE
from fall_tanks.gui.battle_control.fall_tanks_battle_constants import injectConsts
from fall_tanks.gui.impl.battle.battle_page.fall_tanks_postmortem_info_view import FallTanksPostmortemInfoView

def registerFallTanksBattle(personality):
    injectConsts(personality)
    registerPostmortemInfoView(ARENA_GUI_TYPE.FALL_TANKS, FallTanksPostmortemInfoView)
