# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_configurator_progression_inject.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.lobby.vehicle_compare.modifications_panel import CompareModificationsPanelView
from gui.impl.lobby.vehicle_compare.upgrades_panel import CompareUpgradesPanelView

class VehicleCompareConfiguratorProgressionInject(InjectComponentAdaptor):

    def update(self):
        self.getInjectView().update()

    def _makeInjectView(self):
        vehicle = cmp_helpers.getCmpConfiguratorMainView().getCurrentVehicleItem()
        return CompareUpgradesPanelView() if vehicle.getItem().postProgression.isVehSkillTree() else CompareModificationsPanelView()
