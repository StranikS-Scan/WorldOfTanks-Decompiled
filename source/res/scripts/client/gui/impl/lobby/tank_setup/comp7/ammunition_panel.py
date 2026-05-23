# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/comp7/ammunition_panel.py
from CurrentVehicle import g_currentVehicle
from constants import ROLE_TYPE_TO_LABEL
from gui.impl.gen import R
from gui.impl.lobby.comp7.tooltips.comp7_skill_tooltip import Comp7SkillTooltip
from gui.impl.lobby.tank_setup.ammunition_panel.hangar_view import HangarAmmunitionPanelView
from gui.shared.event_dispatcher import showComp7SkillSelectWindow
from gui.shared.gui_items.processors.plugins import VehicleValidator
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7AmmunitionPanelView(HangarAmmunitionPanelView):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.comp7.tooltips.Comp7SkillTooltip():
            intCD = event.getArgument('intCD')
            return Comp7SkillTooltip(intCD)
        return super(Comp7AmmunitionPanelView, self).createToolTipContent(event=event, contentID=contentID)

    def _addListeners(self):
        super(Comp7AmmunitionPanelView, self)._addListeners()
        self.viewModel.roleSkillSlot.onClick += self.__onSkillClick

    def _removeListeners(self):
        super(Comp7AmmunitionPanelView, self)._removeListeners()
        self.viewModel.roleSkillSlot.onClick -= self.__onSkillClick

    def _updateViewModel(self):
        super(Comp7AmmunitionPanelView, self)._updateViewModel()
        self.__updateRoleSkillSlot()

    def __updateRoleSkillSlot(self):
        roleSkill, roleName = self.__getCurrentVehicleRoleInfo()
        with self.viewModel.transaction() as model:
            model.roleSkillSlot.setRoleSkill(roleSkill.name if roleSkill is not None else '')
            model.roleSkillSlot.setRoleName(roleName if roleName is not None else '')
            model.roleSkillSlot.setIntCD(roleSkill.id.itemID if roleSkill is not None else 0)
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
            roleSkill = self.__comp7Controller.getVehicleSkillEquipment(vehicle)
            return (roleSkill, roleName)

    def __onSkillClick(self, *_):
        if not g_currentVehicle.isPresent():
            return
        else:
            vehicle = g_currentVehicle.item
            restriction = self.__comp7Controller.isSuitableVehicle(vehicle)
            if restriction is not None:
                return
            validator = VehicleValidator(vehicle)
            if validator.validate().success:
                showComp7SkillSelectWindow()
            return
