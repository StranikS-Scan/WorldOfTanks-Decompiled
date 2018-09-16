# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_common.py
from gui.shared.events import HasCtxEvent

class CameraMovementStates(object):
    ON_OBJECT = 0
    MOVING_TO_OBJECT = 1
    FROM_OBJECT = 2


class CameraRelatedEvents(HasCtxEvent):
    CAMERA_ENTITY_UPDATED = 'CameraEntityUpdate'
    IDLE_CAMERA = 'IdleCamera'
    VEHICLE_LOADING = 'VehicleLoading'
    LOBBY_VIEW_MOUSE_MOVE = 'MouseMove'
