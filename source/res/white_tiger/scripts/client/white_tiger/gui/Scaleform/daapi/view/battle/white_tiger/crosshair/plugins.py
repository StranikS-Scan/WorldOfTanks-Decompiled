# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/crosshair/plugins.py
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import CrosshairPlugin
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.wt_event.wt_event_helpers import getBossType
from constants import EQUIPMENT_STAGES
from gui.impl import backport
from gui.impl.gen import R
from debug_utils import LOG_DEBUG_DEV

def createPlugins():
    resultPlugins = {'plasmaBuffPlugin': PlasmaBuffPlugin,
     'specialShotPlugin': SpecialShotPlugin}
    return resultPlugins


class PlasmaBuffPlugin(CrosshairPlugin):

    def __init__(self, parentObj):
        super(PlasmaBuffPlugin, self).__init__(parentObj)
        self.__plasmaBuffValue = 0
        self.__plasmaBuffMultiplicator = 0
        self.__plasmaBuffMultiplicatorText = {}
        self.__currentViewID = 0
        self.__isWt = False
        self.__isPlasmaExtractor = False

    def start(self):
        super(PlasmaBuffPlugin, self).start()
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo()
        self.__isWt = getBossType(vInfo.vehicleType.tags) is not None
        self.__isPlasmaExtractor = 'builtinPlasmaExtractor_wt_user' in vInfo.vehicleType.tags
        if self.__isWt and not self.__isPlasmaExtractor:
            return
        else:
            LOG_DEBUG_DEV('PlasmaBuffPlugin applied for vehilce ID={id}, CD={cd}'.format(id=vInfo.vehicleID, cd=vInfo.vehicleType.compactDescr))
            self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBuffValue, self.__plasmaBuffValue, 0)
            crosshairCtrl = self.sessionProvider.shared.crosshair
            if crosshairCtrl is not None:
                crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            vehicleStateCtrl = self.sessionProvider.shared.vehicleState
            if vehicleStateCtrl is not None:
                vehicleStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            self.settingsCore.onSettingsChanged += self.__onSettingsChanged
            return

    def stop(self):
        super(PlasmaBuffPlugin, self).stop()
        if self.__isWt and not self.__isPlasmaExtractor:
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
        self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBuffValue, self.__plasmaBuffValue, self.__plasmaBuffMultiplicatorText)

    def __onSettingsChanged(self, diff):
        self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBuffValue, self.__plasmaBuffValue, self.__plasmaBuffMultiplicatorText)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__plasmaBuffValue = 0
        if state == VEHICLE_VIEW_STATE.PLASMA:
            oldPlasmaBuffValue = self.__plasmaBuffValue
            self.__plasmaBuffValue = value[0]
            self.__plasmaBuffMultiplicator = (value[1] - 1) * 100
            self.__plasmaBuffMultiplicator = int(self.__plasmaBuffMultiplicator)
            self.__plasmaBuffMultiplicatorText = backport.text(R.strings.event.reticle.dmg(), num=self.__plasmaBuffMultiplicator)
            self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBuffValue, oldPlasmaBuffValue, self.__plasmaBuffMultiplicatorText)


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
