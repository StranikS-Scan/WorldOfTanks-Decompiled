# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/comp7/ammunition_panel.py
from CurrentVehicle import g_currentVehicle
from constants import ROLE_TYPE_TO_LABEL
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7AmmunitionPanelView(HangarAmmunitionPanelView):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == TOOLTIPS_CONSTANTS.COMP7_ROLE_SKILL_LOBBY_TOOLTIP:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(event.getArgument('roleSkill'), self.__getCurrentVehicleRoleSkillLevel()))
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(Comp7AmmunitionPanelView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(Comp7AmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.viewModel.roleSkillSlot.setTooltipId(TOOLTIPS_CONSTANTS.COMP7_ROLE_SKILL_LOBBY_TOOLTIP)

    def _updateViewModel(self):
        super(Comp7AmmunitionPanelView, self)._updateViewModel()
        self.__updateRoleSkillSlot()

    def __updateRoleSkillSlot(self):
        roleSkill = self.__getCurrentVehicleRoleSkill()
        self.viewModel.roleSkillSlot.setRoleSkill(roleSkill.name if roleSkill is not None else '')
        return

    def __getCurrentVehicleRoleSkill(self):
        roleName = self.__getCurrentVehicleRole()
        return None if roleName is None else self.__comp7Controller.getRoleEquipment(roleName)

    def __getCurrentVehicleRole(self):
        if not g_currentVehicle.isPresent():
            return None
        else:
            vehicle = g_currentVehicle.item
            restriction = self.__comp7Controller.isSuitableVehicle(vehicle)
            return None if restriction is not None else ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role)

    def __getCurrentVehicleRoleSkillLevel(self):
        roleName = self.__getCurrentVehicleRole()
        return None if roleName is None else self.__comp7Controller.getEquipmentStartLevel(roleName)
