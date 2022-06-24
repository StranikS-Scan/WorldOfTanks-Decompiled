# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from helpers import dependency
from skeletons.gui.game_control import IMapboxController

class MapboxPermissions(PreQueuePermissions):
    __mapboxController = dependency.descriptor(IMapboxController)

    def canCreateSquad(self):
        return super(MapboxPermissions, self).canCreateSquad() if self.__mapboxController.isInPrimeTime() else False
