# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/vehicle_mechanic_item.py
from __future__ import absolute_import
import typing
from gui import GUI_SETTINGS
from gui.impl.gen.view_models.common.vehicle_mechanic_model import MechanicsEnum, MechanicsRank
from gui.shared.gui_items.gui_item import GUIItem
from gui.shared.gui_items.vehicle_mechanics.constants import VEHICLE_MECHANICS_GUI_MAP
from gui.shared.utils.decorators import ReprInjector
from items import vehicles
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

@ReprInjector.simple('guiName', 'priority', 'rank')
class VehicleMechanicItem(GUIItem):
    __slots__ = ('__mechanic', '__vehIntCD')

    def __init__(self, mechanic, vehIntCD):
        super(VehicleMechanicItem, self).__init__()
        self.__mechanic = mechanic
        self.__vehIntCD = vehIntCD

    @property
    def isHidden(self):
        return self.__mechanic not in VEHICLE_MECHANICS_GUI_MAP

    @property
    def hasVideo(self):
        urlDict = GUI_SETTINGS.lookup('mechanicsVideoUrls')
        return urlDict and self.__mechanic.value in urlDict

    @property
    def guiName(self):
        return VEHICLE_MECHANICS_GUI_MAP.get(self.__mechanic, MechanicsEnum.UNKNOWN)

    @property
    def priority(self):
        return self.__getMechanicProperties().get('priority', 0)

    @property
    def rank(self):
        return MechanicsRank(self.__getMechanicProperties().get('rank', MechanicsRank.UNDEFINED.value))

    @property
    def staticParams(self):
        return self.__getMechanicProperties().get('params', ())

    def __getMechanicProperties(self):
        mechanics = vehicles.g_cache.vehicleMechanics.get(self.__vehIntCD, {})
        return mechanics.get(self.__mechanic.value, {})
