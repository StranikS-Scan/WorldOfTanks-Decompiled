# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleDamageShield.py
import BigWorld
import CGF
from Math import Vector3

class WTVehicleDamageShield(BigWorld.DynamicScriptComponent):
    _PREFAB_SRC = 'content/WtPrefabs/abilities/Shield.prefab'
    _SOUND_ON = 'ev_white_tiger_gameplay_b25t_shield_on'
    _SOUND_OFF = 'ev_white_tiger_gameplay_b25t_shield_off'

    def __init__(self):
        super(WTVehicleDamageShield, self).__init__()
        self.__go = None
        return

    def set_isActive(self, prev):
        if self.isActive == prev:
            return
        if self.isActive:
            self.__activate()
        else:
            self.__deactivate()

    def __activate(self):

        def postloadSetup(go):
            self.__go = go

        if self.__go is None:
            CGF.loadGameObjectIntoHierarchy(self._PREFAB_SRC, self.entity.entityGameObject, Vector3(0, 0, 0), postloadSetup)
        else:
            self.__go.activate()
        return

    def __deactivate(self):
        if self.__go is not None:
            if self.__go.isValid():
                self.__go.deactivate()
        return

    def onDestroy(self):
        if self.__go is not None:
            if self.__go.isValid():
                CGF.removeGameObject(self.__go)
            self.__go = None
        return
