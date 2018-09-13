# Embedded file name: scripts/client/gui/prb_control/factories/__init__.py
from debug_utils import LOG_ERROR
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.factories.PreQueueFactory import PreQueueFactory
from gui.prb_control.factories.PrebattleFactory import PrebattleFactory
from gui.prb_control.factories.UnitFactory import UnitFactory
from gui.prb_control.settings import CTRL_ENTITY_TYPE

class ControlFactoryDecorator(ControlFactory):

    def __init__(self):
        self.__factories = {CTRL_ENTITY_TYPE.PREBATTLE: PrebattleFactory(),
         CTRL_ENTITY_TYPE.UNIT: UnitFactory(),
         CTRL_ENTITY_TYPE.PREQUEUE: PreQueueFactory()}

    def start(self, dispatcher, ctx):
        setItem = dispatcher.getFunctionalCollection().setItem
        result = 0
        for ctrlType, factory in self.__factories.iteritems():
            ctx.setEntityType(ctrlType)
            result |= setItem(ctrlType, factory.createFunctional(dispatcher, ctx))

        return result

    def clear(self):
        self.__factories.clear()

    def get(self, ctrlType):
        factory = None
        if ctrlType in self.__factories:
            factory = self.__factories[ctrlType]
        return factory

    def getIterator(self):
        return self.__factories.itervalues()

    def createEntry(self, ctx):
        item = None
        ctrlType = ctx.getEntityType()
        if ctrlType in self.__factories:
            item = self.__factories[ctrlType].createEntry(ctx)
        else:
            LOG_ERROR('Entry factory is not found', ctx)
        return item

    def createFunctional(self, dispatcher, ctx):
        item = None
        ctrlType = ctx.getEntityType()
        if ctrlType in self.__factories:
            item = self.__factories[ctrlType].createFunctional(dispatcher, ctx)
            dispatcher.getFunctionalCollection().setItem(ctrlType, item, ctx.getInitParams())
        else:
            LOG_ERROR('Functional factory is not found', ctrlType, ctx)
        ctx.clear()
        del ctx
        return item

    def getLeaveCtxByAction(self, action):
        for factory in self.__factories.itervalues():
            ctx = factory.getLeaveCtxByAction(action)
            if ctx:
                return ctx

        return None

    def getOpenListCtxByAction(self, action):
        for factory in self.__factories.itervalues():
            ctx = factory.getEntryCtxByAction(action)
            if ctx:
                return ctx

        return None
