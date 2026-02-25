# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/gui_items/vehicle.py
from __future__ import absolute_import
import typing
from fun_random.gui.fun_gui_constants import VEHICLE_TAGS
from gui.shared.gui_items import checkForTags
from gui.shared.utils.requesters import REQ_CRITERIA
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

def isOnlyFunRandomVehicle(vehicle):
    return checkForTags(vehicle.tags, VEHICLE_TAGS.FUN_RANDOM)


ONLY_FUN_RANDOM_VEHICLE_CRITERIA = REQ_CRITERIA.CUSTOM(isOnlyFunRandomVehicle)
