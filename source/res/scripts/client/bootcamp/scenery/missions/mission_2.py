# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/missions/mission_2.py
import BigWorld
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
        self._marker3Data = {'triggerOn': 'MoveHere3_trigger',
         'triggerOff': 'MoveHere4_trigger',
         'delay': 30.0,
         'checkTime': None,
         'marker': self.createMarker('MoveHere3'),
         'needToShow': True,
         'vehiclesDead': [self.createVehicle('Aleksey Egorov'), self.createVehicle('Petr Sergeev'), self.createVehicle('Pascal Raymond')],
         'vehiclesAlive': [self.createVehicle('John King')],
         'vehiclesAliveAllies': [self.createVehicle('Valeriy Gayduchenko'), self.createVehicle('Samuel Bronn'), self.createVehicle('Gerhard Braun')],
         'voiceover': 'vo_bc_get_around_enemy'}
        self._detectedEnemiesList = set()
        return

    def start(self):
        super(Mission2, self).start()
        self._marker0Data['marker'].hide()
        self._marker1Data['marker'].hide()
        self._marker2Data['marker'].hide()
        self._marker3Data['marker'].hide()
        self.playSound2D('vo_bc_destroy_all_enemies')
        self.playSound2D('bc_main_tips_task_start')

    def destroy(self):
        self._marker0Data.clear()
        self._marker1Data.clear()
        self._marker2Data.clear()
        self._marker3Data.clear()
        super(Mission2, self).destroy()

    def update(self):
        super(Mission2, self).update()
        data1 = self._marker1Data
        if data1['needToShow'] and self._isAllVehiclesKilled(data1['vehicles']):
            data1['marker'].show()
            data1['needToShow'] = False
        data2 = self._marker2Data
        if data2['needToShow'] and self._isAllVehiclesKilled(data2['vehicles']):
            data2['marker'].show()
            data2['needToShow'] = False
            data1['needToShow'] = False
            if data1['marker'].isVisible:
                data1['marker'].hide()
        data3 = self._marker3Data
        if data3['needToShow'] and self._isAllVehiclesKilled(data3['vehiclesDead']) and not self._isAllVehiclesKilled(data3['vehiclesAlive']) and not self._isAllVehiclesKilled(data3['vehiclesAliveAllies']) and self._isAnyFromVehiclesDetected(data3['vehiclesAlive']):
            if data3['checkTime'] is None:
                data3['checkTime'] = BigWorld.serverTime() + data3['delay']
            elif BigWorld.serverTime() > data3['checkTime']:
                if not data3['marker'].isVisible:
                    data3['marker'].show()
                    self.playSound2D(data3['voiceover'])
            if data1['marker'].isVisible:
                data1['marker'].hide()
            if data2['marker'].isVisible:
                data2['marker'].hide()
        elif not data3['needToShow'] or self._isAllVehiclesKilled(data3['vehiclesAlive']) or self._isAllVehiclesKilled(data3['vehiclesAliveAllies']):
            if data3['marker'].isVisible:
                data3['marker'].hide()
        data0 = self._marker0Data
        if not data0['isEnable'] and self._isAllVehiclesKilled(data0['killVehicleToEnable']) and not self._isAllVehiclesKilled(data0['killVehicleToDisable']):
            data0['isEnable'] = True
            self._playCombatMusic()
        if data0['isEnable'] and self._isAllVehiclesKilled(data0['killVehicleToDisable']):
            data0['isEnable'] = False
        if data0['isEnable'] and not data0['isInZone']:
            if not data0['marker'].isVisible:
                data0['marker'].show()
        elif data0['marker'].isVisible:
            data0['marker'].hide()
        return

    def onZoneTriggerActivated(self, name):
        data0 = self._marker0Data
        data1 = self._marker1Data
        data2 = self._marker2Data
        data3 = self._marker3Data
        if name == data1['trigger']:
            data1['needToShow'] = False
            data1['marker'].hide()
        if name == data2['trigger']:
            data2['needToShow'] = False
            data2['marker'].hide()
        if name == data0['trigger']:
            data0['isInZone'] = True
        if name == data3['triggerOff']:
            data3['needToShow'] = False

    def onZoneTriggerDeactivated(self, name):
        data1 = self._marker1Data
        if data1 and not self._isAllVehiclesKilled(data1['vehicles']):
            data1['needToShow'] = True
        data2 = self._marker2Data
        if data2 and not self._isAllVehiclesKilled(data2['vehicles']):
            data2['needToShow'] = True
        data0 = self._marker0Data
        if name == data0['trigger']:
            data0['isInZone'] = False
        data3 = self._marker3Data
        if name == data3['triggerOn']:
            data3['needToShow'] = True

    @staticmethod
    def _isAllVehiclesKilled(vehicles):
        return all((not vehicle.isAlive for vehicle in vehicles if vehicle))

    def _isAnyFromVehiclesDetected(self, vehicles):
        return any((vehicle in self._detectedEnemiesList for vehicle in vehicles if vehicle))

    def onPlayerDetectEnemy(self, new, lost):
        if new is not None:
            for vehicle in new:
                if vehicle not in self._detectedEnemiesList and vehicle.isAlive:
                    self._detectedEnemiesList.add(vehicle)

        if lost is not None:
            for vehicle in lost:
                if vehicle in self._detectedEnemiesList:
                    self._detectedEnemiesList.remove(vehicle)

        return
