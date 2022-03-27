# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/vehicle_specs/rts_roster_vehicle.py


class _RtsRosterVehicle(object):
    __slots__ = ('__vehicle',)

    def __init__(self):
        super(_RtsRosterVehicle, self).__init__()
        self.__vehicle = None
        return

    def setVehicle(self, value):
        self.__vehicle = value

    @property
    def item(self):
        return self.__vehicle

    @property
    def defaultItem(self):
        return None

    def isPresent(self):
        return self.__vehicle is not None

    def dispose(self):
        self.__vehicle = None
        return


g_rtsRosterVehicle = _RtsRosterVehicle()
