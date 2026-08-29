# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_core/scripts/client/comp7_core/gui/impl/lobby/role_skill_slot_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.pub.view_component import ViewComponent
from gui.impl.gen.view_models.views.lobby.tank_setup.common.role_skill_slot_model import RoleSkillSlotModel

class RoleSkillSlotPresenter(ViewComponent[RoleSkillSlotModel]):

    def __init__(self):
        super(RoleSkillSlotPresenter, self).__init__(model=RoleSkillSlotModel)

    @property
    def _modeController(self):
        raise NotImplementedError

    @property
    def _roleSkillTooltipId(self):
        raise NotImplementedError

    def _onLoading(self, *args, **kwargs):
        super(RoleSkillSlotPresenter, self)._onLoading(*args, **kwargs)
        self.viewModel.setTooltipId(self._roleSkillTooltipId)
        self.__updateRoleSkillSlot()

    @property
    def viewModel(self):
        return super(RoleSkillSlotPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == self._roleSkillTooltipId:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(event.getArgument('roleSkill'), self.__getCurrentVehicleRoleEquipmentKey(), self.__getCurrentVehicleRoleSkillLevel()))
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(RoleSkillSlotPresenter, self).createToolTip(event)

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__updateRoleSkillSlot),)

    def __updateRoleSkillSlot(self):
        roleSkill = self.__getCurrentVehicleRoleSkill()
        self.viewModel.setRoleSkill(roleSkill.name if roleSkill is not None else '')
        return

    def __getCurrentVehicleRoleSkill(self):
        vehicle = self._getVehicle()
        if vehicle is None:
            return
        else:
            roleEquipmentKey = self.__getCurrentVehicleRoleEquipmentKey()
            return self._modeController.getRoleEquipment(roleEquipmentKey)

    def __getCurrentVehicleRoleSkillLevel(self):
        vehicle = self._getVehicle()
        if vehicle is None:
            return
        else:
            roleEquipmentKey = self.__getCurrentVehicleRoleEquipmentKey()
            return self._modeController.getEquipmentStartLevel(roleEquipmentKey)

    def __getCurrentVehicleRoleEquipmentKey(self):
        vehicle = self._getVehicle()
        return None if vehicle is None else self._modeController.getRoleEquipmentKey(vehicle.descriptor.type)

    def _getVehicle(self):
        if not g_currentVehicle.isPresent():
            return None
        else:
            vehicle = g_currentVehicle.item
            restriction = self._modeController.isSuitableVehicle(vehicle)
            return None if restriction is not None else vehicle
