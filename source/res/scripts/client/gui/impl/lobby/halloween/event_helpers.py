# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/event_helpers.py
import logging
from adisp import process
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from account_helpers.AccountSettings import EVENT_CURRENT_VEHICLE, AccountSettings
_logger = logging.getLogger(__name__)
_IMAGE_FORMAT = '.png'

@process
def closeEvent():
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher is None:
        _logger.error('Prebattle dispatcher is not defined')
        return
    else:
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        return


def moveCamera(dx, dy, dz):
    g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
     'dy': dy,
     'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
     'dy': dy,
     'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)


def notifyCursorOver3DScene(isOver3DScene):
    g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': isOver3DScene}), EVENT_BUS_SCOPE.DEFAULT)


def getCurrentVehicle(itemsCache):
    vehId = AccountSettings.getFavorites(EVENT_CURRENT_VEHICLE)
    if vehId == 0:
        return None
    else:
        return g_currentVehicle.item if vehId > 0 else itemsCache.items.getVehicleCopyByCD(-vehId)


def isEvent():
    dispatcher = g_prbLoader.getDispatcher()
    if dispatcher:
        state = dispatcher.getFunctionalState()
        if state.isInUnit(PREBATTLE_TYPE.EVENT) or state.isInPreQueue(QUEUE_TYPE.EVENT_BATTLES):
            return True
    return False


def filterVehicleBonuses(bonuses, vehiclesToExclude):
    return [ bonus for bonus in bonuses if bonus.getName() == 'vehicles' and not any((True for v, _ in bonus.getVehicles() if v.intCD in vehiclesToExclude)) ]


def getImgName(path):
    return '' if path is None else path.split('/')[-1].replace(_IMAGE_FORMAT, '')
