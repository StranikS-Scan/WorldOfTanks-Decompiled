# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/vehicle_appearance/systems.py
from __future__ import absolute_import
import logging
import typing
import BigWorld
import CGF
import Vehicular
from CustomEffectManager import CustomEffectManager
from vehicle_appearance.common_tank_appearance import ActivateContext, DeactivateContext, UpdateContext, DestroyContext
from vehicle_appearance import constants as appearance_constants
from vehicle_systems.CompoundAppearance import UpdateDirtContext
from vehicle_systems.components.CrashedTracks import CrashedTracksController
from vehicle_systems.components.highlighter import Highlighter
from vehicle_systems.components.hull_aiming_controller import HullAimingController
from vehicle_systems.components.vehicle_shadow_manager import VehicleShadowManager
from vehicle_systems.components.siegeEffectsController import SiegeEffectsController
from vehicle_appearance.component import VehicleAppearanceComponent
if typing.TYPE_CHECKING:
    from vehicle_appearance.common_tank_appearance import CommonTankAppearance
_logger = logging.getLogger(__name__)

class CommonTankAppearanceActivateSystem(CGF.System):
    Create = CGF.CreateReaction(CGF.ReactRo(VehicleAppearanceComponent))
    Activate = CGF.ActivateReaction(CGF.ReactRo(VehicleAppearanceComponent), CGF.Rw(BigWorld.CollisionComponent), CGF.Rw(Vehicular.LodCalculator), CGF.OptRw(Vehicular.GeneralWheelsAnimator), CGF.OptRw(Vehicular.TankWheelsAnimator), CGF.OptRw(Vehicular.FlyingInfoProvider), CGF.OptRo(Vehicular.VehicleAudition), CGF.OptRo(HullAimingController), CGF.OptRw(Vehicular.DetailedEngineState), CGF.OptRo(Vehicular.DirtComponent), CGF.OptRw(Vehicular.GearBox), CGF.OptRw(Vehicular.Suspension), CGF.OptRw(Vehicular.LeveredSuspension), CGF.OptRw(Vehicular.CollisionObstaclesCollector), CGF.OptRw(Vehicular.TessellationCollisionSensor), CGF.OptRw(Vehicular.SuspensionSound), CGF.OptRw(Vehicular.WaterSensor), CGF.OptRw(Vehicular.VehicleTracks), CGF.OptRw(Vehicular.VehicleTraces), CGF.OptRw(Vehicular.TrackNodesAnimator), CGF.OptRw(CustomEffectManager), CGF.OptRw(Vehicular.TerrainMatKindSensor), CGF.OptRw(Vehicular.FrictionAudition), CGF.OptRw(CrashedTracksController), CGF.OptRw(Highlighter))
    Deactivate = CGF.DeactivateReaction(CGF.ReactRo(VehicleAppearanceComponent), CGF.Ro(BigWorld.CollisionComponent), CGF.Rw(VehicleShadowManager), CGF.OptRw(Vehicular.FlyingInfoProvider))
    Remove = CGF.RemoveReaction(CGF.ReactRo(VehicleAppearanceComponent), CGF.OptRw(Vehicular.VehicleTracks))
    Reactions = CGF.Reactions(Create, Activate, Deactivate, Remove)

    def update(self):
        for reactions in self.reaction(self.Deactivate):
            self.__deactivateAppearance(reactions)

        for reactions in self.reaction(self.Remove):
            self.__destroyAppearance(reactions)

        for appearanceCmp in self.reaction(self.Create):
            appearanceCmp.appearance.onComponentsCreate()

        for reactions in self.reaction(self.Activate):
            self.__activateAppearance(reactions)

    def __deactivateAppearance(self, reactions):
        appearance = reactions[0].appearance
        appearance.onDeactivate(DeactivateContext(*reactions))

    def __destroyAppearance(self, reactions):
        appearance = reactions[0].appearance
        appearance.onDestroy(DestroyContext(*reactions))

    def __activateAppearance(self, reactions):
        appearance = reactions[0].appearance
        appearance.onActivate(ActivateContext(self.clock.gameTime, *reactions))


class CommonTankAppearanceUpdateSystem(CGF.System):
    UpdateIterate = CGF.PeriodicIterateReaction(int(appearance_constants.PERIODIC_UPDATE_TIME * 1000), 4, CGF.ActiveOnly, CGF.Ro(VehicleAppearanceComponent), CGF.Ro(Vehicular.LodCalculator), CGF.Ro(BigWorld.CollisionComponent), CGF.OptRo(Vehicular.WaterSensor), CGF.OptRo(Vehicular.GeneralWheelsAnimator), CGF.OptRo(Vehicular.TankWheelsAnimator), CGF.OptRw(CustomEffectManager), CGF.OptRo(Vehicular.DetailedEngineState), CGF.OptRw(Vehicular.VehicleTraces), CGF.OptRo(Vehicular.TerrainMatKindSensor), CGF.OptRw(SiegeEffectsController))
    Reactions = CGF.Reactions(UpdateIterate)

    def update(self):
        for reactions in self.reaction(self.UpdateIterate):
            appearance = reactions[0].appearance
            appearance.update(UpdateContext(*reactions))


class CompoundAppearanceDirtUpdateSystem(CGF.System):
    UpdateIterate = CGF.PeriodicIterateReaction(int(appearance_constants.DIRT_UPDATE_MIN_TIME * 1000), 12, CGF.ActiveOnly, CGF.Ro(VehicleAppearanceComponent), CGF.Ro(Vehicular.LodCalculator), CGF.OptRo(Vehicular.DirtComponent), CGF.OptRo(Vehicular.WaterSensor))
    Reactions = CGF.Reactions(UpdateIterate)

    def update(self):
        for reactions in self.reaction(self.UpdateIterate):
            appearance = reactions[0].appearance
            appearance.updateDirt(UpdateDirtContext(self.clock.gameTime, *reactions))
