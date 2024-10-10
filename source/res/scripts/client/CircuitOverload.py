# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CircuitOverload.py
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency
import CGF
import Math
from script_component.DynamicScriptComponent import DynamicScriptComponent

class CircuitOverload(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CircuitOverload, self).__init__()
        self.__prefab = None
        return

    def set_circuitOverloadInfo(self, _=None):
        circuitOverloadInfo = self.circuitOverloadInfo
        if circuitOverloadInfo is None:
            return
        else:
            vehicle = self.entity
            CGF.loadGameObjectIntoHierarchy(circuitOverloadInfo['prefabPath'], vehicle.entityGameObject, Math.Vector3(0, 0, 0), self.__onGameObjectLoaded)
            return

    def __onGameObjectLoaded(self, prefab):
        self.__prefab = prefab

    def onDestroy(self):
        if self.__prefab is not None:
            CGF.removeGameObject(self.__prefab)
        self.__prefab = None
        super(CircuitOverload, self).onDestroy()
        return
