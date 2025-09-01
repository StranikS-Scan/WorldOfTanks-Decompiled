# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/role_skill_slot_presenter.py
from __future__ import absolute_import
from comp7_light.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_LIGHT_TOOLTIPS
from comp7_core.gui.impl.lobby.role_skill_slot_presenter import RoleSkillSlotPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightRoleSkillSlotPresenter(RoleSkillSlotPresenter):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController

    @property
    def _roleSkillTooltipId(self):
        return COMP7_LIGHT_TOOLTIPS.COMP7_LIGHT_ROLE_SKILL_LOBBY_TOOLTIP
