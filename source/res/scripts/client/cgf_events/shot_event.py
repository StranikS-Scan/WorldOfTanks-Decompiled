# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_events/shot_event.py
import logging
import typing
import CGF
from cgf_modules import game_events
if typing.TYPE_CHECKING:
    from items import vehicle_items
_logger = logging.getLogger(__name__)

def postVehicleShotEvent(entityGo, gunGO, gunDescr, gunIndex, shellType):
    CGF.postEvent(entityGo.spaceID, game_events.VehicleShotEvent(entityGo=entityGo, gunGo=gunGO, gunIndex=gunIndex, shellType=shellType))
