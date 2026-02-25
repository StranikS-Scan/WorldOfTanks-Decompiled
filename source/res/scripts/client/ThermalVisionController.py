# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ThermalVisionController.py
import logging
import typing
import BigWorld
from PlayerEvents import g_playerEvents
from WeakMethod import WeakMethodProxy
from account_helpers.settings_core.settings_constants import GAME
from aih_constants import CTRL_MODE_NAME
from cache import cached_property
from gui.Scaleform.daapi.view.battle.shared.indicator_items.thermal_indicator_proxy import ThermalVisionIndicatorProxy
from gui.battle_control.avatar_getter import getInputHandler
from helpers import dependency
from constants import THERMAL_VISION_STATE, OVERTURN_WARNING_LEVEL
from helpers.thermal_vision.constants import SOUND_EVENT_ACTIVATION, SOUND_EVENT_RELOADING, SOUND_SWITCH_ACTIVATION, SOUND_EVENT_NPC_DETECTED, RELOADING_DURATION, SOUND_EVENT_ENEMY_IN_SECTOR, DISABLED_ERROR_MSG_KEY
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from items.components.shared_components import ThermalVisionParams
_logger = logging.getLogger(__name__)
_STATE_ERROR_MESSAGES = {THERMAL_VISION_STATE.ACTIVE: 'thermalVisionAlreadyActivated',
 THERMAL_VISION_STATE.RELOADING: 'thermalVisionCooldown',
 THERMAL_VISION_STATE.DISABLED: 'thermalVisionDisabled'}

class ThermalVisionController(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(ThermalVisionController, self).__init__()
        self.__indicatorProxy = ThermalVisionIndicatorProxy()
        self.__observedEntityIds = set()
        g_playerEvents.onAvatarReady += self.__onAvatarReady
        getInputHandler().onCameraChanged += self.__onCameraChanged
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__indicatorProxy.init()
        self.__initUI()

    def onDestroy(self):
        self.cleanup()

    def onLeaveWorld(self):
        self.cleanup()

    def cleanup(self):
        self.__indicatorProxy.fini()
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        getInputHandler().onCameraChanged -= self.__onCameraChanged
        self.__stopObservation()
        self.__stopAllSounds(silent=True)
        self.__hideActiveStateUI()
        self.__setSectorState(THERMAL_VISION_STATE.DISABLED)
        BigWorld.PyrometerSector.setParams(0, 0, 0)

    @property
    def params(self):
        return self.typeDescriptor.turret.thermalVision

    @property
    def state(self):
        return self.stateStatus.status

    @property
    def useCount(self):
        return self.stateStatus.useCount

    @property
    def duration(self):
        return self.stateStatus.duration

    @property
    def startTime(self):
        return self.stateStatus.startTime

    @property
    def isObserver(self):
        avatar = BigWorld.player()
        return avatar is None or avatar.playerVehicleID != self.entity.id

    @property
    def isOverturned(self):
        avatar = BigWorld.player()
        return avatar is None or avatar.vehicleOverturnLevel >= OVERTURN_WARNING_LEVEL.DANGER

    @cached_property
    def typeDescriptor(self):
        return self.entity.getDescr(None)

    @cached_property
    def stateHandlers(self):
        return {THERMAL_VISION_STATE.IDLE: WeakMethodProxy(self.__onIdleReceived),
         THERMAL_VISION_STATE.ACTIVE: WeakMethodProxy(self.__onActiveReceived),
         THERMAL_VISION_STATE.RELOADING: WeakMethodProxy(self.__onReloadingReceived),
         THERMAL_VISION_STATE.DISABLED: WeakMethodProxy(self.__onDisabledReceived)}

    def __onIdleReceived(self):
        SOUND_SWITCH_ACTIVATION.disable()
        self.__stopAllSounds()
        self.__hideActiveStateUI()

    def __onActiveReceived(self):
        self.__stopAllSounds(silent=True)
        SOUND_SWITCH_ACTIVATION.enable()
        SOUND_EVENT_ACTIVATION.play()
        self.__toggleShader(True)
        self.__toggleTerrainSector(True)

    def __onReloadingReceived(self):
        SOUND_SWITCH_ACTIVATION.disable()
        self.__stopAllSounds()
        self.__hideActiveStateUI()
        if self.useCount > 0:
            self.__enableReloading()

    def __onDisabledReceived(self):
        SOUND_SWITCH_ACTIVATION.disable()
        self.__stopAllSounds()
        self.__hideActiveStateUI()

    def __updateIndicators(self):
        self.__indicatorProxy.setState(self.stateStatus)
        self.__setSectorState(self.state)

    @noexcept
    def set_stateStatus(self, _=None):
        self.__updateState()

    def onThermalObserved(self, vehicleId):
        self.__showEntityObserveMarker(vehicleId)

    def onThermalDisappear(self, vehicleId):
        self.__hideEntityObserveMarker(vehicleId)

    def tryActivate(self):
        if self.stateStatus is None:
            return
        else:
            currentState = self.state
            if currentState != THERMAL_VISION_STATE.IDLE:
                self.__showStateErrorMessage(currentState)
                return
            if self.isOverturned:
                self.__guiSessionProvider.shared.messages.showVehicleError(DISABLED_ERROR_MSG_KEY)
                return
            self.cell.tryActivate()
            return

    def onEnemyInSector(self):
        SOUND_EVENT_ENEMY_IN_SECTOR.play()
        self.__indicatorProxy.setEntityInSector(True)

    def onSectorEmpty(self):
        SOUND_EVENT_ENEMY_IN_SECTOR.stop()
        self.__indicatorProxy.setEntityInSector(False)

    def updateUseCount(self, useCount):
        self.__indicatorProxy.setUseCount(useCount)

    def __initUI(self):
        if not self.typeDescriptor.hasThermalVision:
            _logger.error('init requested for vehicle without thermal vision config')
            return
        else:
            params = self.params
            self.__indicatorProxy.setParams(params)
            self.__indicatorProxy.setState(self.stateStatus)
            self.__stopAllSounds(silent=True)
            self.__updateSectorSettings()
            self.__setSectorState(THERMAL_VISION_STATE.IDLE)
            BigWorld.PyrometerSector.setParams(params.distance, params.hSectorAngle, params.vSectorAngle)
            if self.stateStatus is not None:
                self.__updateState()
            return

    def __updateState(self):
        state = self.state
        if state not in self.stateHandlers:
            _logger.error('Received unknown state - %s', state)
            return
        self.__updateIndicators()
        self.stateHandlers[state]()

    def __showEntityObserveMarker(self, entityId):
        self.__observedEntityIds.add(entityId)
        SOUND_EVENT_NPC_DETECTED.play()
        self.__guiSessionProvider.shared.feedback.showActiveThermalVision(entityId, False)

    def __hideEntityObserveMarker(self, entityId):
        if entityId not in self.__observedEntityIds:
            return
        self.__observedEntityIds.remove(entityId)

    def __stopObservation(self):
        for entityId in list(self.__observedEntityIds):
            self.__hideEntityObserveMarker(entityId)

    def __stopAllSounds(self, silent=False):
        SOUND_EVENT_ACTIVATION.stop(playStopSound=not silent)
        SOUND_EVENT_RELOADING.stop()
        SOUND_SWITCH_ACTIVATION.disable()
        if self.stateStatus is not None and self.state != THERMAL_VISION_STATE.ACTIVE:
            SOUND_EVENT_ENEMY_IN_SECTOR.stop()
        return

    def __hideActiveStateUI(self):
        self.__toggleShader(False)
        self.__toggleTerrainSector(False)

    def __enableReloading(self):
        reloadTime = self.duration - RELOADING_DURATION
        if reloadTime > 0:
            SOUND_EVENT_RELOADING.play(reloadTime)

    def __setSectorState(self, state):
        if self.isObserver:
            return
        if not self.__settingsCore.getSetting(GAME.SHOW_THERMAL_VISION_SECTOR_ON_MAP):
            state = THERMAL_VISION_STATE.DISABLED
        self.__guiSessionProvider.shared.feedback.updateThermalSectorState(self.entity.id, state)

    def __updateSectorSettings(self):
        if not self.isObserver:
            self.__guiSessionProvider.shared.feedback.updateThermalSectorSettings(self.entity.id, self.params)

    def __onAvatarReady(self):
        self.__updateSectorSettings()
        if self.stateStatus is not None:
            self.__updateIndicators()
        return

    def __onCameraChanged(self, *_, **__):
        if self.stateStatus is not None:
            self.__toggleTerrainSector(self.state == THERMAL_VISION_STATE.ACTIVE)
        return

    def __toggleShader(self, isVisible):
        if self.isObserver:
            self.__setIsPyrometer(False)
            return
        isVisible = isVisible and self.__settingsCore.getSetting(GAME.ENABLE_THERMAL_VISION_EFFECT)
        self.__setIsPyrometer(isVisible)

    def __setIsPyrometer(self, isVisible):
        binoculars = BigWorld.binoculars()
        if binoculars is not None:
            binoculars.setIsPyrometer(isVisible)
        return

    def __toggleTerrainSector(self, isVisible):
        isVisible = isVisible and self.__settingsCore.getSetting(GAME.ENABLE_THERMAL_VISION_SECTOR_EFFECT)
        if not isVisible or self.isObserver:
            BigWorld.PyrometerSector.detachFromCompound()
            return
        if getInputHandler().ctrlModeName == CTRL_MODE_NAME.SNIPER:
            BigWorld.PyrometerSector.detachFromCompound()
            return
        if not BigWorld.PyrometerSector.attachToCompound(self.entity.model):
            _logger.error('Failed to show sector on terrain for %s', self.entity.id)

    def __onSettingsChanged(self, diff):
        state = self.state if self.stateStatus is not None else THERMAL_VISION_STATE.IDLE
        isActive = state == THERMAL_VISION_STATE.ACTIVE
        if GAME.SHOW_THERMAL_VISION_SECTOR_ON_MAP in diff:
            self.__setSectorState(state)
        if GAME.ENABLE_THERMAL_VISION_EFFECT in diff:
            self.__setIsPyrometer(isActive and diff[GAME.ENABLE_THERMAL_VISION_EFFECT])
        if GAME.ENABLE_THERMAL_VISION_SECTOR_EFFECT in diff:
            self.__toggleTerrainSector(isActive and diff[GAME.ENABLE_THERMAL_VISION_SECTOR_EFFECT])
        return

    def __showStateErrorMessage(self, state):
        errorMessageName = _STATE_ERROR_MESSAGES[state]
        self.__guiSessionProvider.shared.messages.showVehicleError(errorMessageName)
