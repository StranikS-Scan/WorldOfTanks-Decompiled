# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/event_tanks_highlight_controller.py
import BigWorld
from HalloweenHangarTank import HalloweenHangarTank
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from account_helpers.settings_core.settings_constants import GRAPHICS
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency

class _DefferedHighlightStrategy(object):
    __IDLE_TRIGGER_NAME = 'toIdle'
    __HANGAR_VEHICLE_TRIGGER_NAME = 'trigger_buy'

    def start(self, highlightHangarVehicle):
        if highlightHangarVehicle:
            BigWorld.wg_setTrigger(self.__HANGAR_VEHICLE_TRIGGER_NAME)

    def stop(self, highlightHangarVehicle):
        if highlightHangarVehicle:
            BigWorld.wg_setTrigger(self.__IDLE_TRIGGER_NAME)

    def handleSelectedEntityUpdated(self, state, entity):
        if state != CameraMovementStates.MOVING_TO_OBJECT:
            return
        if isinstance(entity, HalloweenHangarTank):
            BigWorld.wg_setTrigger(entity.highlightTriggerName)
        else:
            BigWorld.wg_setTrigger(self.__IDLE_TRIGGER_NAME)


class _ForwardHighlightStrategy(object):
    __ISLAND_ENV_NAME = 'Env_Forward_Light'

    def __init__(self):
        super(_ForwardHighlightStrategy, self).__init__()
        self.__renderEnv = BigWorld.CustomizationEnvironment()

    def start(self, highlightHangarVehicle):
        if highlightHangarVehicle:
            self.__renderEnv.enable(True, self.__ISLAND_ENV_NAME)

    def stop(self, highlightHangarVehicle):
        if highlightHangarVehicle:
            self.__renderEnv.enable(False)

    def handleSelectedEntityUpdated(self, state, entity):
        if state != CameraMovementStates.MOVING_TO_OBJECT:
            return
        if isinstance(entity, HalloweenHangarTank):
            self.__renderEnv.enable(True, self.__ISLAND_ENV_NAME)
        else:
            self.__renderEnv.enable(False)


class EventTanksHighlightController(EventSystemEntity):
    __HIGHLIGHT_STRATEGIES = (_DefferedHighlightStrategy, _ForwardHighlightStrategy)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __highlightStrategy = None

    def __init__(self):
        super(EventTanksHighlightController, self).__init__()
        pipelineType = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        highlightStrategyClass = self.__HIGHLIGHT_STRATEGIES[pipelineType]
        self.__highlightStrategy = highlightStrategyClass()

    def start(self, highlightHangarVehicle=False):
        self.__highlightStrategy.start(highlightHangarVehicle)
        if not highlightHangarVehicle:
            self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)

    def stop(self, highlightHangarVehicle=False):
        self.__highlightStrategy.stop(highlightHangarVehicle)
        if not highlightHangarVehicle:
            self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)

    def __handleSelectedEntityUpdated(self, event):
        state = event.ctx['state']
        entity = BigWorld.entities.get(event.ctx['entityId'], None)
        self.__highlightStrategy.handleSelectedEntityUpdated(state, entity)
        return
