# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/shared/tooltips/comp7_light_tooltips.py
from comp7_core.gui.shared.tooltips.comp7_core_tooltips import RoleSkillLobbyTooltipData, RoleSkillBattleTooltipData
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightRoleSkillLobbyTooltipData(RoleSkillLobbyTooltipData):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController


class Comp7LightRoleSkillBattleTooltipData(RoleSkillBattleTooltipData):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController
