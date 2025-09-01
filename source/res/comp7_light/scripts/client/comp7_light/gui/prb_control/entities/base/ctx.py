# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/base/ctx.py
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared.utils.decorators import ReprInjector

@ReprInjector.withParent(('getSquadSize', 'squadSize'))
class Comp7LightPrbAction(PrbAction):

    def __init__(self, actionName, squadSize, mmData=0, accountsToInvite=None):
        super(Comp7LightPrbAction, self).__init__(actionName, mmData, accountsToInvite)
        self.__squadSize = squadSize

    def getSquadSize(self):
        return self.__squadSize
