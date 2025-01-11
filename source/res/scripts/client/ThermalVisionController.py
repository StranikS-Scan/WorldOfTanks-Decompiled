# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ThermalVisionController.py
import logging
import typing
import BigWorld
from PlayerEvents import g_playerEvents
from WeakMethod import WeakMethodProxy
from cache import cached_property
from gui.Scaleform.daapi.view.battle.shared.indicator_items.thermal_indicator_proxy import ThermalVisionIndicatorProxy
from helpers import dependency
from constants import THERMAL_VISION_STATE
from helpers.thermal_vision.constants import SOUND_EVENT_ACTIVATION, SOUND_EVENT_RELOADING, SOUND_SWITCH_ACTIVATION, SOUND_EVENT_NPC_DETECTED, RELOADING_DURATION
from skeletons.gui.battle_session import IBattleSessionProvider
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from items.components.shared_components import ThermalVisionParams
_logger = logging.getLogger(__name__)

class ThermalVisionController(BigWorld.DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(ThermalVisionController, self).__init__()
        self.__indicatorProxy = ThermalVisionIndicatorProxy()
        self.__observedEntityIds = set()
        g_playerEvents.onAvatarReady += self.__onAvatarReady
        if self.stateStatus is None:
            self.__indicatorProxy.setBeforeBattleState(self.params)
        else:
            self.__onObserverVehicleChanged()
        return

    def onDestroy(self):
        self.cleanup()

    def onLeaveWorld(self):
        self.cleanup()

    def cleanup(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__stopObservation()
        self.__stopAllSounds()
        self.__toggleShader(False)

    @property
    def params(self):
        return self.entity.typeDescriptor.turret.thermalVision

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
    def reloadTime(self):
        return self.stateStatus.reloadTime

    @property
    def startTime(self):
        return self.stateStatus.startTime

    @property
    def attachedVehId(self):
        avatar = BigWorld.player()
        return avatar.vehicle.id if avatar and avatar.vehicle else None

    @property
    def playerVehId(self):
        avatar = BigWorld.player()
        return avatar.playerVehicleID if avatar and avatar.playerVehicleID else None

    @cached_property
    def stateHandlers(self):
        return {THERMAL_VISION_STATE.IDLE: WeakMethodProxy(self.__onIdleReceived),
         THERMAL_VISION_STATE.ACTIVE: WeakMethodProxy(self.__onActiveReceived),
         THERMAL_VISION_STATE.RELOADING: WeakMethodProxy(self.__onReloadingReceived),
         THERMAL_VISION_STATE.DISABLED: WeakMethodProxy(self.__onDisabledReceived)}

    def setIndicator(self, indicator):
        self.__indicatorProxy.setIndicator(indicator)
        if self.stateStatus is None:
            self.__indicatorProxy.setBeforeBattleState(self.params)
        else:
            self.__indicatorProxy.setState(self.stateStatus)
        return

    def __onIdleReceived(self):
        self.__stopPyrometerSound()
        self.__toggleShader(False)

    def __onActiveReceived(self):
        self.__playPyrometerSound()
        self.__toggleShader(True)

    def __onReloadingReceived(self):
        self.__stopPyrometerSound()
        self.__toggleShader(False)
        if self.useCount > 0:
            self.__enableReloading()

    def __onDisabledReceived(self):
        self.__stopPyrometerSound()
        self.__toggleShader(False)

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
        if self.state == THERMAL_VISION_STATE.IDLE:
            self.cell.tryActivate()

    def __updateState(self):
        if self.playerVehId != self.entity.id:
            return
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

    def __stopAllSounds(self):
        SOUND_EVENT_ACTIVATION.stop()
        SOUND_EVENT_RELOADING.stop()
        SOUND_SWITCH_ACTIVATION.disable()

    def __playPyrometerSound(self):
        SOUND_SWITCH_ACTIVATION.enable()
        SOUND_EVENT_ACTIVATION.play()

    def __stopPyrometerSound(self):
        SOUND_SWITCH_ACTIVATION.disable()
        SOUND_EVENT_ACTIVATION.stop()

    def __enableReloading(self):
        reloadTime = self.reloadTime - RELOADING_DURATION
        if reloadTime > 0:
            SOUND_EVENT_RELOADING.play(reloadTime)

    def __setSectorState(self, state):
        self.__guiSessionProvider.shared.feedback.updateThermalSectorState(self.playerVehId, state)

    def __updateSectorSettings(self):
        self.__guiSessionProvider.shared.feedback.updateThermalSectorSettings(self.playerVehId, self.params)

    def __onObserverVehicleChanged(self):
        self.__stopAllSounds()
        self.__setSectorState(THERMAL_VISION_STATE.DISABLED)
        self.__indicatorProxy.hide()

    def __onAvatarReady(self):
        if self.playerVehId != self.attachedVehId:
            return
        else:
            self.__updateSectorSettings()
            if self.stateStatus is not None:
                self.__updateState()
            return

    def __toggleShader(self, isVisible):
        binoculars = BigWorld.wg_binoculars()
        if binoculars is not None:
            binoculars.setIsPyrometer(isVisible)
        return
