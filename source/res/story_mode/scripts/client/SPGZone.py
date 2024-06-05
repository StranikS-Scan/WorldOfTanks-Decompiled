# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SPGZone.py
import math
import BigWorld
import Math
import TriggersManager
from AreaOfEffect import AreaOfEffect

class SPGZone(AreaOfEffect, TriggersManager.ITriggerListener):
    _TRIGGER_NAME_TEMPLATE = 'spg_zone_{}'
    _TRIGGER_EXIT_INTERVAL = 1.0
    _TRIGGER_SCALE = (1, 1, 1)
    _TRIGGER_DIRECTION_AXIS = 1

    def __init__(self):
        super(SPGZone, self).__init__()
        self._triggerName = self._TRIGGER_NAME_TEMPLATE.format(self.id)
        self._triggerId = None
        self._hpCallbackId = None
        self.__yawHitPrediction = math.radians(self._equipment.yawHitPrediction)
        self.__hitPredictionDuration = self._equipment.hitPredictionDuration
        return

    def onEnterWorld(self, prereqs):
        super(SPGZone, self).onEnterWorld(prereqs)
        TriggersManager.g_manager.addListener(self)
        self._triggerId = TriggersManager.g_manager.addTrigger(TriggersManager.TRIGGER_TYPE.AREA, name=self._triggerName, position=self.position, radius=self._equipment.areaRadius, scale=self._TRIGGER_SCALE, exitInterval=self._TRIGGER_EXIT_INTERVAL, direction=Math.Matrix(self.matrix).applyToAxis(self._TRIGGER_DIRECTION_AXIS))

    def onLeaveWorld(self):
        if self._hpCallbackId:
            BigWorld.cancelCallback(self._hpCallbackId)
            self._removeHitPrediction()
        TriggersManager.g_manager.delListener(self)
        if self._triggerId is not None:
            TriggersManager.g_manager.delTrigger(self._triggerId)
            self._triggerId = None
        super(SPGZone, self).onLeaveWorld()
        return

    def onTriggerActivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AREA and args['name'] == self._triggerName and self.__hitPredictionDuration > 0:
            self.sessionProvider.shared.hitDirection.addArtyHitPrediction(self.__yawHitPrediction)
            self._hpCallbackId = BigWorld.callback(self.__hitPredictionDuration, self._removeHitPrediction)

    def onTriggerDeactivated(self, args):
        if args['type'] == TriggersManager.TRIGGER_TYPE.AREA and args['name'] == self._triggerName and self._hpCallbackId:
            BigWorld.cancelCallback(self._hpCallbackId)
            self._removeHitPrediction()

    def _removeHitPrediction(self):
        self.sessionProvider.shared.hitDirection.removeArtyHitPrediction(self.__yawHitPrediction)
        self._hpCallbackId = None
        return

    def _showMarker(self):
        pass
