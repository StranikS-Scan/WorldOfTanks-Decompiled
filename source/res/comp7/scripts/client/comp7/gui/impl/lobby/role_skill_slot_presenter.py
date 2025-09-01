# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/role_skill_slot_presenter.py
from __future__ import absolute_import
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7_core.gui.impl.lobby.role_skill_slot_presenter import RoleSkillSlotPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7RoleSkillSlotPresenter(RoleSkillSlotPresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller

    @property
    def _roleSkillTooltipId(self):
        return COMP7_TOOLTIPS.COMP7_ROLE_SKILL_LOBBY_TOOLTIP
