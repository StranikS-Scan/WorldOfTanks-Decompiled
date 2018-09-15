# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_2.py
from bootcamp.scenery.AbstractMission import AbstractMission

class Mission2(AbstractMission):

    def __init__(self, assistant):
        super(Mission2, self).__init__(assistant)
        self._marker0Data = {'trigger': 'MoveHere0_trigger',
         'marker': self.createMarker('MoveHere0'),
         'killVehicleToEnable': [self.createVehicle('Aleksandr Antonuk')],
         'killVehicleToDisable': [self.createVehicle('Petr Sergeev')],
         'isEnable': False,
         'isInZone': False}
        self._marker1Data = {'trigger': 'MoveHere1_trigger',
         'marker': self.createMarker('MoveHere1'),
         'needToShow': True,
         'vehicles': [self.createVehicle('Petr Sergeev')]}
        self._marker2Data = {'trigger': 'MoveHere2_trigger',
         'marker': self.createMarker('MoveHere2'),
         'needToShow': True,
         'vehicles': [self.createVehicle('Aleksey Egorov'), self.createVehicle('Petr Sergeev'), self.createVehicle('Pascal Raymond')]}

    def start(self):
        super(Mission2, self).start()
        self._marker0Data['marker'].hide()
        self._marker1Data['marker'].hide()
        self._marker2Data['marker'].hide()
        self.playSound2D('vo_bc_destroy_all_enemies')
        self.playSound2D('bc_main_tips_task_start')

    def destroy(self):
        self._marker0Data.clear()
        self._marker1Data.clear()
        self._marker2Data.clear()
        super(Mission2, self).destroy()

    def update(self):
        super(Mission2, self).update()
        data1 = self._marker1Data
        if data1['needToShow'] and self._isVehiclesKilled(data1['vehicles']):
            data1['marker'].show()
            data1['needToShow'] = False
        data2 = self._marker2Data
        if data2['needToShow'] and self._isVehiclesKilled(data2['vehicles']):
            data2['marker'].show()
            data2['needToShow'] = False
            data1['needToShow'] = False
            if data1['marker'].isVisible:
                data1['marker'].hide()
        data0 = self._marker0Data
        if not data0['isEnable'] and self._isVehiclesKilled(data0['killVehicleToEnable']) and not self._isVehiclesKilled(data0['killVehicleToDisable']):
            data0['isEnable'] = True
            self._playCombatMusic()
        if data0['isEnable'] and self._isVehiclesKilled(data0['killVehicleToDisable']):
            data0['isEnable'] = False
        if data0['isEnable'] and not data0['isInZone']:
            if not data0['marker'].isVisible:
                data0['marker'].show()
        elif data0['marker'].isVisible:
            data0['marker'].hide()

    def onZoneTriggerActivated(self, name):
        data0 = self._marker0Data
        data1 = self._marker1Data
        data2 = self._marker2Data
        if name == data1['trigger']:
            data1['needToShow'] = False
            data1['marker'].hide()
        if name == data2['trigger']:
            data2['needToShow'] = False
            data2['marker'].hide()
        if name == data0['trigger']:
            data0['isInZone'] = True

    def onZoneTriggerDeactivated(self, name):
        data1 = self._marker1Data
        if data1 and not self._isVehiclesKilled(data1['vehicles']):
            data1['needToShow'] = True
        data2 = self._marker2Data
        if data2 and not self._isVehiclesKilled(data2['vehicles']):
            data2['needToShow'] = True
        data0 = self._marker0Data
        if name == data0['trigger']:
            data0['isInZone'] = False

    @staticmethod
    def _isVehiclesKilled(vehicles):
        return all((not vehicle.isAlive for vehicle in vehicles if vehicle))
