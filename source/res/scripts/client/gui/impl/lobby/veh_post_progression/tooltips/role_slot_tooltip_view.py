# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/tooltips/role_slot_tooltip_view.py
import typing
from gui.Scaleform.daapi.view.lobby.veh_post_progression.veh_post_progression_vehicle import g_postProgressionVehicle
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.role_model import RoleModel
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.role_slot_tooltip_view_model import RoleSlotTooltipViewModel
from gui.impl.lobby.veh_post_progression.tooltips.base_feature_tooltip_view import BaseFeatureTooltipView
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from helpers import dependency
from shared_utils import first
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from items.components.supply_slots_components import SupplySlot

class RoleSlotTooltipView(BaseFeatureTooltipView):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(RoleSlotTooltipView, self).__init__(R.views.lobby.veh_post_progression.tooltip.RoleSlotTooltipView(), RoleSlotTooltipViewModel(), *args, **kwargs)

    @property
    def viewModel(self):
        return super(RoleSlotTooltipView, self).getViewModel()

    def _onLoading(self, step, *args, **kwargs):
        super(RoleSlotTooltipView, self)._onLoading(step, *args, **kwargs)
        if not g_postProgressionVehicle.isPresent():
            return
        moneyShortage = self._itemsCache.items.stats.money.getShortage(step.action.getPrice())
        with self.viewModel.transaction() as model:
            self.__fillRolesData(model)
            PriceModelBuilder.fillPriceModel(model.price, step.action.getPrice())
            PriceModelBuilder.fillPriceModel(model.moneyShortage, moneyShortage)

    def __fillRolesData(self, model):
        optionalDevices = g_postProgressionVehicle.defaultItem.optDevices
        slots = model.getSlots()
        slots.clear()
        for slotIdx in range(len(optionalDevices.slots)):
            slot = optionalDevices.getSlot(slotIdx)
            slotModel = RoleModel()
            self.__fillRole(slotModel, slot.item)
            slots.addViewModel(slotModel)
            if optionalDevices.isSlotHasDynamicSpecialization(slotIdx) and slot.isDynamic:
                self.__fillRole(model.chosenRole, slot.item)

        slots.invalidate()
        roles = model.getAvailableRoles()
        roles.clear()
        for slot in optionalDevices.dynSlotTypeOptions:
            roleModel = RoleModel()
            self.__fillRole(roleModel, slot)
            roles.addViewModel(roleModel)

        roles.invalidate()

    def __fillRole(self, roleModel, slot):
        roleModel.setId(slot.slotID)
        if slot.categories:
            roleModel.setRole(first(slot.categories))
