# Embedded file name: scripts/client/gui/prb_control/factories/ControlFactory.py
from debug_utils import LOG_DEBUG
from gui.prb_control.items import PlayerDecorator

class ControlFactory(object):

    def __del__(self):
        LOG_DEBUG('ControlFactory is deleted', self)

    def createEntry(self, ctx):
        raise NotImplementedError()

    def createFunctional(self, dispatcher, ctx):
        raise NotImplementedError()

    def createPlayerInfo(self, functional):
        return PlayerDecorator()

    def createStateEntity(self, functional):
        raise NotImplementedError()

    def createLeaveCtx(self):
        raise NotImplementedError()

    def getLeaveCtxByAction(self, action):
        raise NotImplementedError()

    def getOpenListCtxByAction(self, action):
        raise NotImplementedError()
