# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/veh_post_progression/veh_post_progression_vehicle.py
import typing
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class _PostProgressionVehicle(object):
    __slots__ = ('__customVehicle', '__defaultVehicle', '__diffVehicle')

    def __init__(self):
        super(_PostProgressionVehicle, self).__init__()
        self.__customVehicle = None
        self.__defaultVehicle = None
        self.__diffVehicle = None
        return

    def setCustomVehicle(self, value):
        self.__customVehicle = value

    def setDefaultVehicle(self, value):
        self.__defaultVehicle = value

    def setDiffVehicle(self, value):
        self.__diffVehicle = value

    @property
    def defaultItem(self):
        return self.__defaultVehicle

    @property
    def diffItem(self):
        result = self.__diffVehicle or self.__defaultVehicle
        self.__diffVehicle = None
        return result

    @property
    def item(self):
        return self.__customVehicle or self.__defaultVehicle

    def isPresent(self):
        return self.item is not None

    def clear(self):
        self.__customVehicle = None
        self.__defaultVehicle = None
        self.__diffVehicle = None
        return


g_postProgressionVehicle = _PostProgressionVehicle()
