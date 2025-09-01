# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSVehicleDissolveComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from vehicle_systems.tankStructure import VehiclePartsTuple, TankPartNames
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
_DISSOLVE_TIME_TICK = 0.05
_DISSOLVE_FACTOR_STEP = 0.015
_DISSOLVE_FULL_FACTOR = 1.0
_DISSOLVE_INSTANT_FACTOR = 0.95
_INSTANT_DISSOLVE_TIME_PASSED = 2.0

class LSVehicleDissolveComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LSVehicleDissolveComponent, self).__init__()
        self.__callbackDelayer = CallbackDelayer()
        self.__dissolveHandler = None
        return

    def onDestroy(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        if self.entity.appearance:
            self.entity.appearance.onModelChanged -= self.__onModelChanged
        self.__callbackDelayer.destroy()
        super(LSVehicleDissolveComponent, self).onDestroy()

    def _onAvatarReady(self):
        appearance = self.entity.appearance
        self.entity.onAppearanceReady += self.__onAppearanceReady
        if appearance is not None:
            if appearance.isAlive:
                self.__onAppearanceReady()
            else:
                self.__onModelChanged()
        super(LSVehicleDissolveComponent, self)._onAvatarReady()
        return

    @property
    def lsBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def __onAppearanceReady(self):
        self.lsBattleGuiCtrl.setVehicleHidden(self.entity.id, False)
        self.__dissolveHandler = None
        self.__callbackDelayer.clearCallbacks()
        appearance = self.entity.appearance
        if appearance.isAlive:
            appearance.onModelChanged += self.__onModelChanged
        else:
            self.__onModelChanged()
        return

    def __onModelChanged(self):
        vehicle = self.entity
        if vehicle.isDestroyed or vehicle.health > 0:
            return
        appearance = vehicle.appearance
        if not appearance.damageState.isCurrentModelDamaged:
            return
        fashions = VehiclePartsTuple(BigWorld.WGVehicleFashion(), BigWorld.WGVehicleFashion(), BigWorld.WGVehicleFashion(), BigWorld.WGVehicleFashion())
        appearance._setFashions(fashions, appearance.isTurretDetached)
        self.__dissolveHandler = BigWorld.PyDissolveHandler()
        for fashionIdx, _ in enumerate(TankPartNames.ALL):
            fashion = appearance.fashions[fashionIdx]
            fashion.addMaterialHandler(self.__dissolveHandler)
            fashion.addTrackMaterialHandler(self.__dissolveHandler)

        self.__dissolveHandler.setEnabled(True)
        effectDuration = BigWorld.serverTime() - self.deathTime if self.deathTime > 0.0 else 0.0
        initialFactor = 0.0 if effectDuration < _INSTANT_DISSOLVE_TIME_PASSED else _DISSOLVE_INSTANT_FACTOR
        self.__dissolve(initialFactor)

    def __dissolve(self, factor):
        factor += _DISSOLVE_FACTOR_STEP
        self.__dissolveHandler.setDissolveFactor(factor)
        if factor < _DISSOLVE_FULL_FACTOR:
            self.__callbackDelayer.delayCallback(_DISSOLVE_TIME_TICK, self.__dissolve, factor)
        else:
            self.__hideModel()
            for fashionIdx, _ in enumerate(TankPartNames.ALL):
                self.entity.appearance.fashions[fashionIdx].removeMaterialHandler(self.__dissolveHandler)

            self.__dissolveHandler = None
        return

    def __hideModel(self):
        self.entity.show(False)
        self.entity.appearance.boundEffects.stop()
        self.lsBattleGuiCtrl.setVehicleHidden(self.entity.id, True)
