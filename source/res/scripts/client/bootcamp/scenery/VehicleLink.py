# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/VehicleLink.py
import Math

class VehicleLink(object):

    def __str__(self):
        return '((Vehicle)Name:' + self.name + ', id:' + str(self.id) + ', isValid:' + str(self.isValid) + ', isAlive:' + str(self.isAlive) + ', isEnemy:' + str(self.isEnemy) + ')'

    def __repr__(self):
        return self.__str__()

    def __init__(self, data):
        self.data = data
        self._vehicleInfo = None
        self._vehicle = None
        self._enemy = False
        self._id = -1
        return

    def resolve(self, avatar):
        for id, vehicle in avatar.arena.vehicles.items():
            if vehicle['name'] == self.data['name']:
                self._id = id
                self._vehicleInfo = vehicle
                self._enemy = self._vehicleInfo['team'] != avatar.team
                break

    def setVehicle(self, vehicle):
        self._vehicle = vehicle

    id = property(lambda self: self._id)
    name = property(lambda self: self.data['name'])
    isValid = property(lambda self: self._vehicleInfo is not None)
    isAlive = property(lambda self: self.isValid and self._vehicleInfo['isAlive'])
    isEnemy = property(lambda self: self._enemy)
    isVisible = property(lambda self: self._vehicle is not None)
    maxHealth = property(lambda self: self._vehicleInfo['vehicleType'].maxHealth if self.isValid else -1)
    position = property(lambda self: self._vehicle.position if self.isVisible else Math.Vector3(0.0, 0.0, 0.0))
    health = property(lambda self: self._vehicle.health if self.isVisible else -1.0)
    team = property(lambda self: self._vehicleInfo['team'] if self.isValid else -1)
