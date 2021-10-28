# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PersonalDeathZone.py
import BigWorld
import Math
from AreaOfEffect import AreaOfEffect
import TriggersManager

class PersonalDeathZone(AreaOfEffect, TriggersManager.ITriggerListener):
    _TRIGGER_NAME_TEMPLATE = 'personal_deathzone_{}'
    _TRIGGER_EXIT_INTERVAL = 1.0
    _TRIGGER_SCALE = (1, 1, 1)
    _TRIGGER_DIRECTION_AXIS = 1
    MAX_LAG = 2.0

    def __init__(self):
        super(PersonalDeathZone, self).__init__()
        self._triggerName = self._TRIGGER_NAME_TEMPLATE.format(self.id)
        self._triggerId = None
        self._triggered = False
        self.callbackId = None
        self.__arenaComponent = None
        return

    def onEnterWorld(self, prereqs):
        super(PersonalDeathZone, self).onEnterWorld(prereqs)
        TriggersManager.g_manager.addListener(self)
        self._triggerId = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.AREA, name=self._triggerName, position=self.position, radius=self._equipment.areaRadius, scale=self._TRIGGER_SCALE, exitInterval=self._TRIGGER_EXIT_INTERVAL, direction=Math.Matrix(self.matrix).applyToAxis(self._TRIGGER_DIRECTION_AXIS))

    def onLeaveWorld(self):
        self.__getArenaComponent().removeZone(self)
        TriggersManager.g_manager.delListener(self)
        if self._triggerId is not None:
            TriggersManager.g_manager.delTrigger(self._triggerId)
            self._triggerId = None
        super(PersonalDeathZone, self).onLeaveWorld()
        return

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AREA and args['name'] == self._triggerName:
            self.__getArenaComponent().addZone(self)

    def onTriggerDeactivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AREA and args['name'] == self._triggerName:
            self.__getArenaComponent().removeZone(self)

    def __getArenaComponent(self):
        if not self.__arenaComponent:
            componentSystem = BigWorld.player().arena.componentSystem
            self.__arenaComponent = getattr(componentSystem, 'personalDeathZones')
        return self.__arenaComponent
