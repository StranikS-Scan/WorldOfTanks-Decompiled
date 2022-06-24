# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fun_random/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController

class FunRandomPermissions(PreQueuePermissions):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def canCreateSquad(self):
        return super(FunRandomPermissions, self).canCreateSquad() if self.__funRandomController.isInPrimeTime() else False
