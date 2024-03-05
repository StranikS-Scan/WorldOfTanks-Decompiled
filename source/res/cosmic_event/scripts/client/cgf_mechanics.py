# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cgf_mechanics.py
import CGF
import GenericComponents
import Math
from typing import TYPE_CHECKING
import Vehicle
from cgf_components.gun_shot_effect_component import GunShotEffectComponent
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery, autoregister
from constants import IS_CLIENT
from cgf_script.component_meta_class import registerComponent
if IS_CLIENT:
    from helpers import dependency
    from skeletons.gui.battle_session import IBattleSessionProvider
elif TYPE_CHECKING:
    from typing import Optional
    from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController
    from gui.battle_control.controllers.consumables.ammo_ctrl import ReloadingTimeState

@registerComponent
class MyUserGunShotEffectComponent(object):
    domain = CGF.DomainOption.DomainClient


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class CosmicArenaVehicleManager(CGF.ComponentManager):
    _ENEMIES_BASIC_RGB = (0.1, 0.5, 1)

    @onAddedQuery(GenericComponents.DynamicModelComponent, GunShotEffectComponent, CGF.GameObject)
    def onGunShotEffectAdded(self, dynModel, gunShotCmp, go):
        vehicle = self._getVehicle(go)
        from gui.battle_control import avatar_getter
        if vehicle.id == avatar_getter.getPlayerVehicleID():
            go.createComponent(MyUserGunShotEffectComponent)
        else:
            r, g, b = self._ENEMIES_BASIC_RGB
            dynModel.setMaterialParameterVector4(gunShotCmp.materialParam, Math.Vector4(r, g, b, 1))

    def _getVehicle(self, gameObject):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        rootGameObject = hierarchy.getTopMostParent(gameObject)
        goSyncComponent = rootGameObject.findComponentByType(GenericComponents.EntityGOSync)
        return goSyncComponent.entity


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class CosmicEffectComponentManager(CGF.ComponentManager):
    _PERCENT_0 = 0.0
    _PERCENT_100 = 1.0
    _BASIC_RGB = (1, 0.1, 0)
    _RGB = _BASIC_RGB
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CosmicEffectComponentManager, self).__init__()
        self.setBasicVehicleGunGlow()

    @onProcessQuery(GenericComponents.DynamicModelComponent, GunShotEffectComponent, MyUserGunShotEffectComponent, tickGroup='PostHierarchy', period=0.2)
    def onProcess(self, model, gunShotCmp, _):
        r, g, b = self._RGB
        model.setMaterialParameterVector4(gunShotCmp.materialParam, Math.Vector4(r, g, b, self._getGunReloadAnimPercent(gunShotCmp)))

    def _getGunReloadAnimPercent(self, gunShotCmp):
        try:
            ammo = self.sessionProvider.shared.ammo
        except (AttributeError, TypeError):
            return self._PERCENT_0

        reloadState = ammo.getGunReloadingState()
        if reloadState.isReloadingFinished():
            return self._PERCENT_100
        timePassed = reloadState.getTimePassed()
        totalReloadingTime = reloadState.getBaseValue()
        if timePassed <= totalReloadingTime:
            startValue = gunShotCmp.startValue
            val = timePassed / totalReloadingTime * (gunShotCmp.endValue - startValue) + startValue
            return val
        return self._PERCENT_0

    @classmethod
    def setBasicVehicleGunGlow(cls):
        cls._RGB = cls._BASIC_RGB

    @classmethod
    def setAdvancedVehicleGunGlow(cls, glowColor):
        cls._RGB = glowColor
