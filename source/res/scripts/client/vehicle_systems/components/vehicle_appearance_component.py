# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_appearance_component.py


class VehicleAppearanceComponent(object):
    appearance = property(lambda self: self.__appearance)

    def __init__(self, appearance):
        self.__appearance = appearance
