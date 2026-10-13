# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/shared/hw_indicators.py
from __future__ import absolute_import, division
import BigWorld
import weakref
import CommandMapping
from gui.impl.gen import R
from constants import EQUIPMENT_STAGES
from gui.impl import backport
from gui.Scaleform.daapi.view.common.keybord_helpers import getHotKeyList
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from halloween.gui.scaleform.daapi.view.meta.NitroIndicatorMeta import NitroIndicatorMeta
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID
from skeletons.gui.impl import IGuiLoader

class HWRocketAcceleratorIndicator(NitroIndicatorMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    NITRO_EQUIPMENT_NAME = 'nitroRamDamage'
    STAGE_TO_INDICATOR_STATE = {EQUIPMENT_STAGES.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     EQUIPMENT_STAGES.READY: MECHANICS_WIDGET_CONST.READY,
     EQUIPMENT_STAGES.UNAVAILABLE: MECHANICS_WIDGET_CONST.DISABLE,
     EQUIPMENT_STAGES.COOLDOWN: MECHANICS_WIDGET_CONST.PREPARING}
    TIMER_UPDATE_INTERVAL = 0.1

    def __init__(self):
        super(HWRocketAcceleratorIndicator, self).__init__()
        self.__isEnabled = True
        self.__item = None
        self.__intCD = None
        self.__activeEndTime = 0
        self._callbackDelayer = CallbackDelayer()
        return

    def _populate(self):
        super(HWRocketAcceleratorIndicator, self)._populate()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairPositionChanged += self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
            crosshairCtrl.onCrosshairScaleChanged += self.__onCrosshairPositionChanged
            self.__onCrosshairPositionChanged(*crosshairCtrl.getPosition())
            self.__onCrosshairViewChanged(crosshairCtrl.getViewID())
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
            equipmentCtrl.onEquipmentsCleared += self.__onEquipmentsCleared
        hwNitroCtrl = getattr(BigWorld.player(), 'hwNitroAccelerationControl', None)
        if hwNitroCtrl is not None:
            hwNitroCtrl.onActivate += self.__handleNitroPressed
        self.as_setKeyS(getHotKeyList(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION))
        self.as_setStateS(MECHANICS_WIDGET_CONST.READY)
        self.as_setTooltipS(makeTooltip(backport.text(R.strings.artefacts.nitroRamDamage.name()), backport.text(R.strings.artefacts.nitroRamDamage.descr())))
        if self.__item is not None and self.__item() is not None:
            self.__startTimerUpdate()
        return

    def _dispose(self):
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            crosshairCtrl.onCrosshairPositionChanged -= self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairScaleChanged -= self.__onCrosshairPositionChanged
            crosshairCtrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        equipmentCtrl = self.sessionProvider.shared.equipments
        if equipmentCtrl is not None:
            equipmentCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
            equipmentCtrl.onEquipmentsCleared -= self.__onEquipmentsCleared
        hwNitroCtrl = getattr(BigWorld.player(), 'hwNitroAccelerationControl', None)
        if hwNitroCtrl is not None:
            hwNitroCtrl.onActivate -= self.__handleNitroPressed
        self._callbackDelayer.destroy()
        self.__item = None
        super(HWRocketAcceleratorIndicator, self)._dispose()
        return

    @property
    def _hasTabScreen(self):
        guiLoader = dependency.instance(IGuiLoader)
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.halloween.mono.battle.tab_screen())
        return view is not None and not view.getParentWindow().isHidden()

    def _updateTimer(self):
        item = self.__item() if self.__item else None
        if item is None:
            return
        else:
            restartTimer = self._updateProgress(item)
            return self.TIMER_UPDATE_INTERVAL if restartTimer else -1

    def _updateProgress(self, item):
        stage = item.getStage()
        inCriticalCondition, _ = item.inCriticalCondition()
        if inCriticalCondition:
            self.as_setStateS(MECHANICS_WIDGET_CONST.DISABLE)
            return True
        if stage in self.STAGE_TO_INDICATOR_STATE:
            self.as_setStateS(self.STAGE_TO_INDICATOR_STATE[stage])
        self.as_setKeyS(getHotKeyList(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION))
        if stage not in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN):
            return True
        leftTime = max(0, self.__activeEndTime - BigWorld.serverTime())
        progress = leftTime / item.getTotalTime()
        if progress <= 0 and item.getQuantity() == 0:
            self.as_setStateS(MECHANICS_WIDGET_CONST.DISABLE)
            return False
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            progress = 1 - progress
        self.as_setProgressS(progress)
        self.as_setTimeS(leftTime)
        return True

    def __onVehicleControlling(self, vehicle):
        self.__isEnabled = False
        if vehicle.isAlive() and vehicle.isPlayerVehicle:
            self.__isEnabled = True
        self.__onCrosshairPositionChanged()
        self.__updateVisibility()

    def __onVehicleStateUpdated(self, state, value):
        if state in (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.__isEnabled = False
            self.__updateVisibility()

    def __onCrosshairPositionChanged(self, *args):
        self.as_updateLayoutS(*self.sessionProvider.shared.crosshair.getScaledPosition())

    def __onCrosshairViewChanged(self, viewID):
        if viewID == CROSSHAIR_VIEW_ID.UNDEFINED:
            self.as_setVisibleS(False)
        else:
            self.__updateVisibility()

    def __updateVisibility(self):
        self.as_setVisibleS(self.__isEnabled and not self._hasTabScreen)

    def __onEquipmentUpdated(self, intCD, item):
        desc = item.getDescriptor()
        if desc.name != self.NITRO_EQUIPMENT_NAME:
            return
        stage = item.getStage()
        if stage in self.STAGE_TO_INDICATOR_STATE and not BigWorld.player().fireInVehicle:
            self.as_setStateS(self.STAGE_TO_INDICATOR_STATE[stage])
        if stage in (EQUIPMENT_STAGES.ACTIVE, EQUIPMENT_STAGES.COOLDOWN):
            self.__activeEndTime = BigWorld.serverTime() + item.getTimeRemaining()
        self.__intCD = intCD
        self.__item = weakref.ref(item)
        self.__startTimerUpdate()

    def __onEquipmentsCleared(self):
        self.__stopTimerUpdate()
        self.__item = None
        return

    def __setState(self, state):
        self.__curState = state
        self.as_setStateS(state)

    def __handleNitroPressed(self):
        intCD = self.__intCD
        if intCD is None:
            return
        else:
            ctrl = self.sessionProvider.shared.equipments
            if ctrl is None:
                return
            result, error = ctrl.changeSetting(intCD)
            if not result and error:
                ctrl = self.sessionProvider.shared.messages
                if ctrl is not None:
                    ctrl.showVehicleError(error.key, error.ctx)
            return

    def __startTimerUpdate(self):
        if not self._callbackDelayer.hasDelayedCallback(self._updateTimer):
            self._callbackDelayer.delayCallback(self.TIMER_UPDATE_INTERVAL, self._updateTimer)

    def __stopTimerUpdate(self):
        self._callbackDelayer.clearCallbacks()
