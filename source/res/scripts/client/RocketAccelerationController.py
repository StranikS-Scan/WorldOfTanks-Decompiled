# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/RocketAccelerationController.py
import logging
from functools import partial
import BigWorld
import CGF
from Event import Event
from constants import ROCKET_ACCELERATION_STATE
from wotdecorators import noexcept
from vehicle_systems.model_assembler import loadAppearancePrefab
_logger = logging.getLogger(__name__)
_DEFAULT_OUTFIT = 'default'

class RocketAccelerationController(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(RocketAccelerationController, self).__init__()
        self.__prefabGameObject = None
        self.__onStateChanged = Event()
        self.__onTryActivate = Event()
        self.__initAppearance()
        return

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
        if self.entity.isDestroyed or not self.entity.inWorld:
            return
        else:
            if callback is not None:
                self.__onStateChanged -= callback
            if tryActivateCallback is not None:
                self.__onTryActivate -= tryActivateCallback
            return

    def sendStateToAllSubscribers(self):
        self.__onStateChanged(self.stateStatus)

    def cleanup(self):
        if self.entity.isDestroyed or not self.entity.inWorld:
            return
        else:
            self.__onStateChanged.clear()
            self.__onTryActivate.clear()
            self.entity.onAppearanceReady -= self.__tryUpdatePrefab
            if self.__prefabGameObject is not None:
                CGF.removeGameObject(self.__prefabGameObject)
                self.__prefabGameObject = None
            return

    def __initAppearance(self):
        if not self.__tryUpdatePrefab():
            self.entity.onAppearanceReady += self.__tryUpdatePrefab

    def __onLoaded(self, path, root):
        if not root.isValid:
            _logger.error('Failed to load prefab: %s', path)
            return
        self.__prefabGameObject = root

    def __tryUpdatePrefab(self):
        if self.__prefabGameObject is not None:
            return False
        else:
            typeDescriptor = self.entity.typeDescriptor
            if typeDescriptor is None:
                return False
            appearance = self.entity.appearance
            if appearance is None or not appearance.isConstructed or appearance.isDestroyed:
                return False
            modelsSet = appearance.outfit.modelsSet
            outfit = _DEFAULT_OUTFIT if not modelsSet else modelsSet
            prefabPath = typeDescriptor.type.rocketAccelerationParams.effectsPrefab[outfit]
            loadAppearancePrefab(prefabPath, appearance, partial(self.__onLoaded, prefabPath))
            return True
