# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_2.py
from bootcamp.scenery.AbstractMission import AbstractMission
import MusicControllerWWISE as MC
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP

class MarkerStruct(object):
    MARKER = 0
    NEED_TO_SHOW = 1
    VEHICLES = 2


class Mission2(AbstractMission):

    def __init__(self, assistant):
        super(Mission2, self).__init__(assistant)
        self._marker0Data = {'trigger': 'MoveHere0_trigger',
         'marker': self.createMarker('MoveHere0'),
         'killVehicleToEnable': [self.createVehicle('Aleksandr Antonuk')],
         'killVehicleToDisable': [self.createVehicle('Petr Sergeev')],
         'isEnable': False,
         'isInZone': False}
        self._markers1Data = {'MoveHere1_trigger': [self.createMarker('MoveHere1'), True, [self.createVehicle('Petr Sergeev')]],
         'MoveHere2_trigger': [self.createMarker('MoveHere2'), True, [self.createVehicle('Aleksey Egorov')]]}

    def start(self):
        super(Mission2, self).start()
        for data in self._markers1Data.itervalues():
            data[MarkerStruct.MARKER].hide(True)

        self.playSound2D('vo_bc_destroy_all_enemies')
        self.playSound2D('bc_main_tips_task_start')

    def destroy(self):
        self._marker0Data.clear()
        self._markers1Data.clear()
        super(Mission2, self).destroy()

    def update(self):
        super(Mission2, self).update()
        for data in self._markers1Data.itervalues():
            if data[MarkerStruct.NEED_TO_SHOW] and self._isVehiclesKilled(data[MarkerStruct.VEHICLES]):
                data[MarkerStruct.MARKER].show()
                data[MarkerStruct.NEED_TO_SHOW] = False

        if not self._marker0Data['isEnable'] and self._isVehiclesKilled(self._marker0Data['killVehicleToEnable']):
            if not self._isVehiclesKilled(self._marker0Data['killVehicleToDisable']):
                self._marker0Data['isEnable'] = True
                if not MC.g_musicController.isPlaying(MC.MUSIC_EVENT_COMBAT):
                    MC.g_musicController.muteMusic(False)
            if self._marker0Data['isEnable'] and self._isVehiclesKilled(self._marker0Data['killVehicleToDisable']):
                self._marker0Data['isEnable'] = False
            if self._marker0Data['isEnable'] and not self._marker0Data['isInZone']:
                self._marker0Data['marker'].isVisible or self._marker0Data['marker'].show()
        elif self._marker0Data['marker'].isVisible:
            self._marker0Data['marker'].hide()

    def onZoneTriggerActivated(self, name):
        if name in self._markers1Data:
            markerData = self._markers1Data[name]
            markerData[MarkerStruct.NEED_TO_SHOW] = False
            markerData[MarkerStruct.MARKER].hide()
        if name == self._marker0Data['trigger']:
            self._marker0Data['isInZone'] = True

    def onZoneTriggerDeactivated(self, name):
        markerData = self._markers1Data.get(name, None)
        if markerData and not self._isVehiclesKilled(markerData[MarkerStruct.VEHICLES]):
            markerData[MarkerStruct.NEED_TO_SHOW] = True
        if name == self._marker0Data['trigger']:
            self._marker0Data['isInZone'] = False
        return

    @staticmethod
    def _isVehiclesKilled(vehicles):
        return all((not vehicle.isAlive for vehicle in vehicles if vehicle))
