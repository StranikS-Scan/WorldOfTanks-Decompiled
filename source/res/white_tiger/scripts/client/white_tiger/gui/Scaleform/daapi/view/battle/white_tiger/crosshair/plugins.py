# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/crosshair/plugins.py
import typing
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import CrosshairPlugin
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID
from constants import EQUIPMENT_STAGES
from functools import partial
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers.CallbackDelayer import CallbackDelayer
from items import vehicles
from white_tiger.gui.shared.events import DynamicFactorsEvent, WTCrosshairVisibilityEvents
from wt_settings import g_wt_config
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.consumables.equipment_ctrl import _EquipmentItem

def createPlugins():
    resultPlugins = {'crosshairVisibilityPlugin': CrosshairVisibilityPlugin,
     'plasmaBuffPlugin': PlasmaBuffPlugin,
     'specialShotPlugin': SpecialShotPlugin,
     'barrierPlugin': BarrierPlugin,
     'decreaseReloadTimePlugin': DecreaseReloadTimePlugin,
     'IncreaseDamagePlugin': IncreaseDamagePlugin}
    return resultPlugins


class CrosshairVisibilityPlugin(CrosshairPlugin):

    def start(self):
        super(CrosshairVisibilityPlugin, self).start()
        g_eventBus.addListener(WTCrosshairVisibilityEvents.SHOW_CROSSHAIR, self.__handleCrosshairVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        g_eventBus.removeListener(WTCrosshairVisibilityEvents.SHOW_CROSSHAIR, self.__handleCrosshairVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        super(CrosshairVisibilityPlugin, self).stop()

    def __handleCrosshairVisibility(self, event):
        self._parentObj.setVisible(event.ctx['visible'])


class PlasmaBuffPlugin(CrosshairPlugin):

    def __init__(self, parentObj):
        super(PlasmaBuffPlugin, self).__init__(parentObj)
        self.__plasmaBuffValue = 0
        self.__plasmaBuffMultiplicator = 0
        self.__plasmaBuffMultiplicatorText = {}
        self.__plasmaSavedValue = 0
        self.__currentViewID = 0
        self.__isWt = False
        self.__isPlasmaExtractor = False

    def start(self):
        super(PlasmaBuffPlugin, self).start()
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo()
        vehCD = vInfo.vehicleType.compactDescr
        self.__isWt = g_wt_config.isAnyTypeBoss(vehCD)
        self.__isPlasmaExtractor = self.__isBossWithPlasma(vInfo)
        if self.__isWt and not self.__isPlasmaExtractor:
            return
        else:
            LOG_DEBUG_DEV('PlasmaBuffPlugin applied for vehilce ID={id}, CD={cd}'.format(id=vInfo.vehicleID, cd=vInfo.vehicleType.compactDescr))
            self.__plasmaBuffMultiplicatorText = 0
            self.__showPlasmaToUI(self.__plasmaBuffValue)
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
        self.__showPlasmaToUI(self.__plasmaBuffValue)

    def __onSettingsChanged(self, diff):
        self.__showPlasmaToUI(self.__plasmaBuffValue)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__plasmaBuffValue = 0
        if state == VEHICLE_VIEW_STATE.PLASMA:
            oldPlasmaBuffValue = self.__plasmaBuffValue
            self.__plasmaBuffValue = value[0]
            self.__plasmaBuffMultiplicator = (value[1] - 1) * 100
            self.__plasmaBuffMultiplicator = int(self.__plasmaBuffMultiplicator)
            self.__plasmaBuffMultiplicatorText = backport.text(R.strings.event.reticle.dmg(), num=self.__plasmaBuffMultiplicator)
            self.__plasmaSavedValue = value[2]
            self.__showPlasmaToUI(oldPlasmaBuffValue)

    def __showPlasmaToUI(self, oldPlasmaBuffValue):
        self._parentObj.as_setPlasmaSavedS(self.__plasmaSavedValue)
        self._parentObj.as_showPlasmaIndicatorS(self.__plasmaBuffValue, oldPlasmaBuffValue, self.__plasmaBuffMultiplicatorText)

    def __isBossWithPlasma(self, vInfo):
        vehicle = BigWorld.entities.get(vInfo.vehicleID)
        return False if not vehicle else 'wtExtractorShot' in vehicle.dynamicComponents


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
        if item.getDescriptor().name in ('wt_explosive_shot', 'wt_charged_shot'):
            self.__isExplosiveShotActive = item.getStage() == EQUIPMENT_STAGES.ACTIVE
            self._parentObj.as_showExplosiveShotIndicatorS(self.__isExplosiveShotActive)


class BarrierPlugin(CrosshairPlugin):

    def __init__(self, parentObj):
        super(BarrierPlugin, self).__init__(parentObj)
        self._currentViewID = CROSSHAIR_VIEW_ID.ARCADE
        self._barrierIsActive = False
        self._equipmentIndex = ''

    def start(self):
        super(BarrierPlugin, self).start()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        return

    def stop(self):
        super(BarrierPlugin, self).stop()
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        return

    def __onCrosshairViewChanged(self, viewID):
        self._currentViewID = viewID
        if viewID == CROSSHAIR_VIEW_ID.ARCADE and self._barrierIsActive:
            self._parentObj.as_showBarrierS(True, self._equipmentIndex)

    def __onEquipmentUpdated(self, intCD, item):
        equipmentCtrl = self.sessionProvider.shared.equipments
        if item.getDescriptor().name == 'wt_barrier':
            self._barrierIsActive = item.getStage() == EQUIPMENT_STAGES.ACTIVE
            if self._currentViewID == CROSSHAIR_VIEW_ID.ARCADE:
                self._equipmentIndex = str(equipmentCtrl.getItemIDx(intCD))
                self._parentObj.as_showBarrierS(self._barrierIsActive, self._equipmentIndex)


class _DynamicFactorsLevelsPlugin(CrosshairPlugin):
    _FAIL_DELAY = 0.6
    _COMPONENT_NAME = 'WTVehicleAbilityLevelManager'
    _KEY_NAME = ''

    def __init__(self, parentObj):
        super(_DynamicFactorsLevelsPlugin, self).__init__(parentObj)
        self._callbackDelayer = CallbackDelayer()

    def start(self):
        super(_DynamicFactorsLevelsPlugin, self).start()
        self._onStartUpdate()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        g_eventBus.addListener(DynamicFactorsEvent.UPDATE_LEVEL, self._onUpdateLevel, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def stop(self):
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        g_eventBus.removeListener(DynamicFactorsEvent.UPDATE_LEVEL, self._onUpdateLevel, scope=EVENT_BUS_SCOPE.BATTLE)
        self._callbackDelayer.destroy()
        self._hidePlugin()
        super(_DynamicFactorsLevelsPlugin, self).stop()
        return

    def _showPlugin(self, useAnim=False):
        pass

    def _hidePlugin(self, useAnim=False):
        pass

    def _updatePlugin(self, level, isFail, useAnim=False):
        pass

    def _onStartUpdate(self):
        component = self.__getComponent()
        if component is None or not component.isComponentActive:
            return
        else:
            currentLevel = component.currentAbilityLevel
            self._showPlugin()
            if currentLevel > 0:
                self._updatePlugin(component.currentAbilityLevel, False)
            return

    def _onUpdateLevel(self, event):
        if event.ctx['keyName'] != self._KEY_NAME:
            return
        level = event.ctx['level']
        isFail = event.ctx['isFail']
        isActive = event.ctx['isActive']
        if not isActive:
            self._callbackDelayer.delayCallback(self._FAIL_DELAY, partial(self._hidePlugin, True))
            return
        self._showPlugin(True)
        self._updatePlugin(level, isFail, True)
        if isFail:
            self._callbackDelayer.delayCallback(self._FAIL_DELAY, self._onFail)

    def _onFail(self):
        self._hidePlugin(True)

    def __onCrosshairViewChanged(self, viewID):
        component = self.__getComponent()
        if not component or not component.isComponentActive:
            self._hidePlugin()
            return
        currentLevel = component.currentAbilityLevel
        isFail = component.isFail
        if viewID in (CROSSHAIR_VIEW_ID.ARCADE, CROSSHAIR_VIEW_ID.SNIPER) and not isFail:
            self._showPlugin()
            self._updatePlugin(currentLevel, False)
        else:
            self._onFail()

    def __getComponent(self):
        vehicle = avatar_getter.getPlayerVehicle()
        if vehicle is None:
            return
        else:
            componentName = '{}_{}'.format(self._COMPONENT_NAME, self._KEY_NAME)
            return vehicle.dynamicComponents.get(componentName)


class DecreaseReloadTimePlugin(_DynamicFactorsLevelsPlugin):
    _FAIL_DELAY = 2.0
    _KEY_NAME = 'wt_decrease_reload_time'

    def _showPlugin(self, useAnim=False):
        self._parentObj.as_showReloadBoostS(useAnim)

    def _hidePlugin(self, useAnim=False):
        self._parentObj.as_hideReloadBoostS(useAnim)

    def _updatePlugin(self, level, isFail, useAnim=False):
        self._parentObj.as_updateReloadBoostS(level, isFail, useAnim)

    def _onFail(self):
        self._updatePlugin(0, False, True)


class IncreaseDamagePlugin(_DynamicFactorsLevelsPlugin):
    _FAIL_DELAY = 0.6
    _KEY_NAME = 'wt_increase_damage'

    def __init__(self, parentObj):
        super(IncreaseDamagePlugin, self).__init__(parentObj)
        self.__maxLevel = 0
        self.__isMaxLevelReached = False

    def _onStartUpdate(self):
        super(IncreaseDamagePlugin, self)._onStartUpdate()
        self.__maxLevel = self.__getMaxLevel()

    def _showPlugin(self, useAnim=False):
        self._parentObj.as_showIncreaseDamageS(useAnim)

    def _hidePlugin(self, useAnim=False):
        self._parentObj.as_hideIncreaseDamageS(useAnim)
        self.__isMaxLevelReached = False

    def _updatePlugin(self, level, isFail, useAnim=False):
        currentLevel = level
        if self.__isMaxLevelReached and not isFail:
            currentLevel = self.__maxLevel
        self._parentObj.as_updateIncreaseDamageS(currentLevel, isFail, useAnim)
        self.__isMaxLevelReached = level == self.__maxLevel

    def _onFail(self):
        pass

    def __getMaxLevel(self):
        eqId = vehicles.g_cache.equipmentIDs()[self._KEY_NAME]
        equipment = vehicles.g_cache.equipments()[eqId]
        return len(equipment.components[('WTVehicleDynamicFactors', 'wtDynamicFactors')]['factors'])
