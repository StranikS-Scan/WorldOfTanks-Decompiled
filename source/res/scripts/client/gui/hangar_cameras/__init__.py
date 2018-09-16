# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/__init__.py
from skeletons.gui.hangar_cameras import IHangarCameraSounds
__all__ = ('getHangarCamerasConfig',)

def getHangarCamerasConfig(manager):
    from gui.hangar_cameras.hangar_camera_sounds import HangarCameraSounds
    ctrl = HangarCameraSounds()
    ctrl.init()
    manager.addInstance(IHangarCameraSounds, ctrl, finalizer='fini')
