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
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(event.getArgument('roleSkill'), event.getArgument('roleName')))
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
        roleSkill, roleName = self.__getCurrentVehicleRoleInfo()
        with self.viewModel.transaction() as model:
            model.roleSkillSlot.setRoleSkill(roleSkill.name if roleSkill is not None else '')
            model.roleSkillSlot.setRoleName(roleName if roleName is not None else '')
        return

    def __getCurrentVehicleRoleInfo(self):
        if not g_currentVehicle.isPresent():
            return (None, None)
        else:
            vehicle = g_currentVehicle.item
            restriction = self.__comp7Controller.isSuitableVehicle(vehicle)
            if restriction is not None:
                return (None, None)
            roleName = ROLE_TYPE_TO_LABEL.get(vehicle.descriptor.role)
            roleSkill = self.__comp7Controller.getRoleEquipment(roleName)
            return (roleSkill, roleName)
