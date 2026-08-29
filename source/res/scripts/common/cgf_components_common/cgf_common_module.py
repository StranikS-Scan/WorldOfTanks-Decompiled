# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/cgf_common_module.py
from __future__ import absolute_import
import CGF
from cgf_components_common.managers.state_managers import StateSwitcherSystem
from cgf_components_common.vehicle_components import VehicleDestroyingComponent, VehicleDamageLoggerComponent, VehicleSequenceParamsAttachedComponent
from cgf_components_common.material_component import MaterialComponent
from cgf_components_common.state_components import RemoveOnDeathComponent, SpawnOnDeathComponent, VehicleHealthObserverComponent
from cgf_components_common.vehicle_mechanics import StationaryReloadSequenceParamsComponent, CrestMovingSequenceParamsComponent
from cgf_script.registration import registerModule

@registerModule
class CommonScriptsModule(object):
    name = 'Common Module'
    desc = 'Client Server Common Components'
    group = 'Common'
    systems = [CGF.RegisterSystem(StateSwitcherSystem, domain=CGF.Domain.ClientServer)]
    components = [VehicleDestroyingComponent,
     VehicleDamageLoggerComponent,
     RemoveOnDeathComponent,
     SpawnOnDeathComponent,
     VehicleHealthObserverComponent,
     MaterialComponent,
     StationaryReloadSequenceParamsComponent,
     CrestMovingSequenceParamsComponent,
     VehicleSequenceParamsAttachedComponent]
