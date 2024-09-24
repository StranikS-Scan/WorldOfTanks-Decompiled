# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PersonalDeathZone.py
import Math
import BigWorld
from AreaOfEffect import AreaOfEffect
import TriggersManager
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
TRIGGER_NAME_PREFIX = 'personal_deathzone'

class PersonalDeathZone(AreaOfEffect, TriggersManager.ITriggerListener):
    _TRIGGER_NAME_TEMPLATE = TRIGGER_NAME_PREFIX + '_{}'
    _TRIGGER_TYPE = TriggersManager.TRIGGER_TYPE.CURRENT_VEHICLE_AREA
    _TRIGGER_EXIT_INTERVAL = 1.0
    _TRIGGER_SCALE = (1, 1, 1)
    _TRIGGER_DIRECTION_AXIS = 1
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PersonalDeathZone, self).__init__()
        self._triggerName = self._TRIGGER_NAME_TEMPLATE.format(self.id)
        self._triggerId = None
        self._markerItem = None
        return

    def onEnterWorld(self, prereqs):
        super(PersonalDeathZone, self).onEnterWorld(prereqs)
        BigWorld.player().arena.onVehicleKilled += self._onVehicleKilled
        TriggersManager.g_manager.addListener(self)
        self._triggerId = TriggersManager.g_manager.addTrigger(self._TRIGGER_TYPE, name=self._triggerName, position=self.position, radius=self._equipment.areaRadius, scale=self._TRIGGER_SCALE, exitInterval=self._TRIGGER_EXIT_INTERVAL, direction=Math.Matrix(self.matrix).applyToAxis(self._TRIGGER_DIRECTION_AXIS))

    def onLeaveWorld(self):
        BigWorld.player().arena.onVehicleKilled -= self._onVehicleKilled
        if self._guiController:
            self._guiController.onPlayerLeft(self)
        TriggersManager.g_manager.delListener(self)
        if self._triggerId is not None:
            TriggersManager.g_manager.delTrigger(self._triggerId)
            self._triggerId = None
        self._hideMarker()
        self._markerItem = None
        super(PersonalDeathZone, self).onLeaveWorld()
        return

    def onTriggerActivated(self, args):
        vehicle = BigWorld.player().vehicle
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            if self.__isOwnTrigger(args) and self._guiController:
                self._guiController.onPlayerEntered(self)
            return

    def onTriggerDeactivated(self, args):
        if self.__isOwnTrigger(args) and self._guiController:
            self._guiController.onPlayerLeft(self)

    @property
    def adjustedDelay(self):
        return round(self._adjustedDelay)

    @property
    def delay(self):
        return self._equipment.delay

    @property
    def _guiController(self):
        return self._guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.PERSONAL_DEATH_ZONES_GUI_CTRL)

    def _showMarker(self):
        if not self._equipment.areaVisibleToEnemies and self._isAttackerEnemy():
            return
        equipmentsCtrl = self.sessionProvider.shared.equipments
        if equipmentsCtrl and self.delay > 0:
            self._markerItem = equipmentsCtrl.showMarker(self._equipment, self.position, self._direction, self.delay)

    def _hideMarker(self):
        equipmentsCtrl = self.sessionProvider.shared.equipments
        if equipmentsCtrl:
            equipmentsCtrl.hideMarker(self._markerItem)

    def _onVehicleKilled(self, victimID, *_):
        if self._guiController and BigWorld.player().vehicle and BigWorld.player().vehicle.id == victimID:
            self._guiController.onPlayerLeft(self)

    def __isOwnTrigger(self, args):
        return args['type'] == self._TRIGGER_TYPE and args['name'] == self._triggerName
