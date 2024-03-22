# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_pickup_component.py


class VehiclePickupComponent(object):
    MAX_ANGLE_DEVIATION = 5.0
    MAX_LIFETIME = 1.0

    def __init__(self, appearance):
        self.__appearance = appearance
        self.time = 0.0

    @property
    def appearance(self):
        return self.__appearance
