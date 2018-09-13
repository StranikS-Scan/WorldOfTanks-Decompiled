# Embedded file name: scripts/client/gui/prb_control/factories/ControlFactory.py
from debug_utils import LOG_DEBUG
from gui.prb_control.items import PlayerDecorator
from gui.prb_control.settings import FUNCTIONAL_EXIT

class ControlFactory(object):

    def __del__(self):
        LOG_DEBUG('ControlFactory is deleted', self)

    def createEntry(self, ctx):
        raise NotImplementedError()

    def createEntryByAction(self, action):
        raise NotImplementedError()

    def createFunctional(self, dispatcher, ctx):
        raise NotImplementedError()

    def createPlayerInfo(self, functional):
        return PlayerDecorator()

    def createStateEntity(self, functional):
        raise NotImplementedError()

    def createLeaveCtx(self, funcExit = FUNCTIONAL_EXIT.NO_FUNC):
        raise NotImplementedError()

    def getLeaveCtxByAction(self, action):
        raise NotImplementedError()

    def _createEntryByAction(self, action, available):
        result = None
        if action in available:
            clazz, args = available[action]
            if args:
                result = clazz(*args)
            else:
                result = clazz()
        return result
