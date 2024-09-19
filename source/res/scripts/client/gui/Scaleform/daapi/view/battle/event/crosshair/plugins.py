# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/crosshair/plugins.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import CrosshairPlugin
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.wt_event.wt_event_helpers import isBoss
from constants import EQUIPMENT_STAGES
from gui.impl import backport
from gui.impl.gen import R

def createPlugins():
    resultPlugins = {'plasmaBuffPlugin': PlasmaBuffPlugin,
     'specialShotPlugin': SpecialShotPlugin}
    return resultPlugins


class PlasmaBuffPlugin(CrosshairPlugin):

    def __init__(self, parentObj):
        super(PlasmaBuffPlugin, self).__init__(parentObj)
        self.__plasmaBonusValue = 0
        self.__plasmaBonusMultiplier = 0
        self.__plasmaBonusMultiplierText = {}
        self.__currentViewID = 0
        self.__isWt = False

    def start(self):
        super(PlasmaBuffPlugin, self).start()
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo()
        self.__isWt = isBoss(vInfo.vehicleType.tags)
        if self.__isWt:
            return
        else:
            self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBonusValue, False, 0)
            crosshairCtrl = self.sessionProvider.shared.crosshair
            if crosshairCtrl is not None:
                crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            vehicleStateCtrl = self.sessionProvider.shared.vehicleState
            if vehicleStateCtrl is not None:
                vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
            self.__updatePlasmaCount(vInfo)
            return

    def stop(self):
        super(PlasmaBuffPlugin, self).stop()
        if self.__isWt:
            return
        else:
            ctrl = self.sessionProvider.shared.crosshair
            if ctrl is not None:
                ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            vehicleStateCtrl = self.sessionProvider.shared.vehicleState
            if vehicleStateCtrl is not None:
                vehicleStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
            return

    def __onCrosshairViewChanged(self, viewID):
        self.__currentViewID = viewID
        self._parentObj.setViewID(self.__currentViewID)
        self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBonusValue, False, self.__plasmaBonusMultiplierText)

    def __onSettingsChanged(self, diff):
        self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBonusValue, False, self.__plasmaBonusMultiplierText)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.PLASMA:
            vInfo = self.sessionProvider.getArenaDP().getVehicleInfo()
            self.__updatePlasmaCount(vInfo, value)

    def __updatePlasmaCount(self, vInfo, value=None):
        plasmaBonusVal = 0
        plasmaMultiplierVal = 0
        if value:
            plasmaBonusVal = value[0]
            plasmaMultiplierVal = self.__calculateMultiplierPercent(value[1])
        else:
            vehicleID = vInfo.vehicleID
            arenaInfo = BigWorld.player().arena.arenaInfo
            plasmaBonus = arenaInfo.dynamicComponents.get('plasmaBonusLevel') if arenaInfo else None
            if plasmaBonus:
                plasmaBonusVal = plasmaBonus.getPlasmaBonusForVehicle(vehicleID)
                plasmaMultiplierVal = plasmaBonus.getPlasmaBonusMultiplier(plasmaBonusVal)
        self.__plasmaBonusValue = plasmaBonusVal
        self.__plasmaBonusMultiplier = plasmaMultiplierVal
        self.__plasmaBonusMultiplier = int(self.__plasmaBonusMultiplier)
        self.__plasmaBonusMultiplierText = backport.text(R.strings.event.reticle.dmg(), num=self.__plasmaBonusMultiplier)
        self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBonusValue, True, self.__plasmaBonusMultiplierText)
        return

    def __calculateMultiplierPercent(self, multiplierDecimal):
        return (multiplierDecimal - 1) * 100


class SpecialShotPlugin(CrosshairPlugin):

    def __init__(self, parentObj):
        super(SpecialShotPlugin, self).__init__(parentObj)
        self.__isExplosiveShotActive = False

    def start(self):
        super(SpecialShotPlugin, self).start()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def stop(self):
        super(SpecialShotPlugin, self).stop()
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __onCrosshairViewChanged(self, viewID):
        self.__currentViewID = viewID
        self._parentObj.as_showExplosiveShotIndicatorS(self.__isExplosiveShotActive)

    def __onEquipmentUpdated(self, intCD, item):
        if item.getDescriptor().name in ('builtinExplosiveShot_wt', 'builtinChargedShot_wt'):
            self.__isExplosiveShotActive = item.getStage() == EQUIPMENT_STAGES.ACTIVE
            self._parentObj.as_showExplosiveShotIndicatorS(self.__isExplosiveShotActive)
