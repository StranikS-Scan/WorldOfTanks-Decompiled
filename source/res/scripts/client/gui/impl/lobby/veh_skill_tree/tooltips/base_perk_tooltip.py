# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/tooltips/base_perk_tooltip.py
from frameworks.wulf import Array
from gui.veh_post_progression.models.modifications import SimpleModItem
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.base_perk_tooltip_model import BasePerkTooltipModel
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.kpi_model import KpiModel
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.tooltips.kpi_value_model import KpiValueModel
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.utils import fillNodeModel
from gui.impl.pub import ViewImpl
from gui.shared.gui_items import Vehicle
from skeletons.gui.shared import IItemsCache

class BasePerkTooltipView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    @property
    def viewModel(self):
        raise NotImplementedError

    def _onLoading(self, vehCD, step, stepStatus, *args, **kwargs):
        super(BasePerkTooltipView, self)._onLoading(*args, **kwargs)
        vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        with self.getViewModel().transaction() as vm:
            fillNodeModel(vm.node, step, stepStatus, vehicle)
            self.__fillModifiers(vehicle, vm.getKpis(), step.action)

    @staticmethod
    def __fillModifiers(vehicle, modifiers, modification):
        modifiers.clear()
        for kpi in modification.getKpi(vehicle):
            value = KpiValueModel()
            value.setValue(kpi.value)
            value.setValueKey(kpi.name)
            value.setValueType(kpi.type)
            bonusModel = KpiModel()
            bonusModel.setKpiName(kpi.name)
            bonusModel.getKpiValues().addViewModel(value)
            modifiers.addViewModel(bonusModel)

        modifiers.invalidate()
