# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/lobby_cm.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.hangar.hangar_cm_handlers import VehicleContextMenuHandler

class EPVehicleContextMenuHandler(VehicleContextMenuHandler):

    def __init__(self, cmProxy, ctx=None):
        LOG_ERROR('INIT -- EPVehicleContextMenuHandler')
        super(EPVehicleContextMenuHandler, self).__init__(cmProxy, ctx)
