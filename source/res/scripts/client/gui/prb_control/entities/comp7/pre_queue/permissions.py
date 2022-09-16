# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/comp7/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7Permissions(PreQueuePermissions):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def canCreateSquad(self):
        if self.__comp7Controller.isOffline or self.__comp7Controller.isBanned:
            return False
        return False if not self.__comp7Controller.hasPlayableVehicle() else super(Comp7Permissions, self).canCreateSquad()
