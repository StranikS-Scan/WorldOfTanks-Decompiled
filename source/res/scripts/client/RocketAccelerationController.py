# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/RocketAccelerationController.py
import logging
import BigWorld
import CGF
from Event import Event
from constants import ROCKET_ACCELERATION_STATE
from wotdecorators import noexcept
from vehicle_systems.model_assembler import loadAppearancePrefab
_logger = logging.getLogger(__name__)

class RocketAccelerationController(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(RocketAccelerationController, self).__init__()
        self.__readyCallback = None
        self.__prefabRoot = None
        self.__onStateChanged = Event()
        self.__onTryActivate = Event()
        self.__effectsPrefab = ''
        self.__duration = 0
        self.__reloadTime = 0.0
        self.__deployTme = 0.0
        self.__inited = False
        self.init()
        return

    @noexcept
    def init(self):
        if self.__inited or not self.entity or not self.entity.typeDescriptor:
            return
        self.__duration = self.entity.typeDescriptor.type.rocketAccelerationParams.duration
        self.__reloadTime = self.entity.typeDescriptor.type.rocketAccelerationParams.reloadTime
        self.__deployTme = self.entity.typeDescriptor.type.rocketAccelerationParams.deployTime
        appearance = self.entity.appearance
        modelsSet = appearance.outfit.modelsSet
        outfit = 'default' if not modelsSet else modelsSet
        self.__effectsPrefab = self.entity.typeDescriptor.type.rocketAccelerationParams.effectsPrefab[outfit]
        loadAppearancePrefab(self.__effectsPrefab, appearance, self.__onLoaded)
        self.__inited = True

    @property
    def prefabPath(self):
        return self.__effectsPrefab

    @property
    def reloadTime(self):
        return self.__reloadTime

    @property
    def deployTime(self):
        return self.__deployTme

    def tryActivate(self):
        if self.stateStatus.status == ROCKET_ACCELERATION_STATE.READY:
            self.cell.tryActivate()
        self.__onTryActivate()

    @noexcept
    def set_stateStatus(self, _=None):
        self.__onStateChanged(self.stateStatus)

    def onDestroy(self):
        self.cleanup()

    def onLeaveWorld(self):
        self.cleanup()

    def subscribe(self, callback=None, tryActivateCallback=None):
        try:
            if callback is not None:
                self.__onStateChanged += callback
            if tryActivateCallback is not None:
                self.__onTryActivate += tryActivateCallback
            if callback is not None and self.stateStatus is not None:
                callback(self.stateStatus)
        except Exception as ex:
            _logger.exception(ex)
            self.cleanup()

        return

    def unsubscribe(self, callback=None, tryActivateCallback=None):
        if callback is not None:
            self.__onStateChanged -= callback
        if tryActivateCallback is not None:
            self.__onTryActivate -= tryActivateCallback
        return

    def sendStateToAllSubscribers(self):
        self.__onStateChanged(self.stateStatus)

    def cleanup(self):
        self.__onStateChanged.clear()
        self.__onTryActivate.clear()
        if self.__prefabRoot is not None:
            CGF.removeGameObject(self.__prefabRoot)
        return

    def __onLoaded(self, root):
        if not root.isValid:
            _logger.error('Failed to load prefab: %s', self.__effectsPrefab)
            return
        self.__prefabRoot = root
