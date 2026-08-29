# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/helpers/PrefabHelper.py
import logging
import CGF
from vehicle_systems.model_assembler import loadAppearancePrefab
_logger = logging.getLogger(__name__)

class AppearancePrefabHandler(object):

    def __init__(self, funcIsPrefabActive):
        super(AppearancePrefabHandler, self).__init__()
        self.__funcIsPrefabActive = funcIsPrefabActive
        self.__callbackOnLoad = lambda : None
        self.__prefabGO = None
        self.__constructed = True
        self.__isBeingLoaded = None
        return

    def destroy(self):
        self.unload()
        self.__isBeingLoaded = None
        self.__constructed = None
        self.__prefabGO = None
        self.__callbackOnLoad = None
        self.__funcIsPrefabActive = None
        return

    def load(self, appearance, prefabPath, callback):
        if not self.__constructed:
            _logger.warning('the object has been destroyed already')
            return
        if self.__prefabGO:
            _logger.error('self.__prefabGO is already initialised, probable multiple calls')
            return
        if not appearance:
            _logger.error('appearance is invalid')
            return
        if not appearance.isConstructed:
            _logger.error('appearance is not constructed')
            return
        if not prefabPath:
            _logger.error('prefabPath is not valid')
            return
        self.__callbackOnLoad = callback
        self.__isBeingLoaded = True
        loadAppearancePrefab(prefabPath, appearance, self._onAppearancePrefabLoaded)

    def unload(self):
        if self.__prefabGO:
            AppearancePrefabHandler.__removeGameObject(self.__prefabGO)
        self.__prefabGO = None
        self.__isBeingLoaded = None
        return

    def _onAppearancePrefabLoaded(self, gameObject):
        removeGo = False
        if not self.__constructed:
            _logger.error('the object has been destroyed already')
            removeGo = True
        else:
            if not self.__isBeingLoaded:
                _logger.warning('no effect is being loaded')
                removeGo = True
            if not self.__funcIsPrefabActive():
                _logger.warning('Not active')
                removeGo = True
            self.__isBeingLoaded = None
        if removeGo:
            _logger.warning('Removing game object')
            AppearancePrefabHandler.__removeGameObject(gameObject)
            self.__prefabGO = None
            return
        else:
            self.__prefabGO = gameObject
            self.__callbackOnLoad()
            return

    @staticmethod
    def __removeGameObject(gameObject):
        if gameObject is None:
            _logger.warning('no gameObject')
            return
        elif not gameObject.isValid():
            _logger.warning('existing gameObject is invalid')
            return
        else:
            CGF.removeGameObject(gameObject)
            return
