# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/easy_tank_equip_vehicle.py


class _EasyTankEquipCopyVehicle(object):
    __slots__ = ('__vehicle',)

    def __init__(self):
        super(_EasyTankEquipCopyVehicle, self).__init__()
        self.__vehicle = None
        return

    def setVehicle(self, value):
        self.__vehicle = value

    @property
    def item(self):
        return self.__vehicle

    def isPresent(self):
        return self.__vehicle is not None

    def clear(self):
        self.__vehicle = None
        return


g_easyTankEquipCopyVehicle = _EasyTankEquipCopyVehicle()
