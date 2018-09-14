# Embedded file name: scripts/client/gui/prb_control/factories/decorator.py
from debug_utils import LOG_ERROR
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.factories.PreQueueFactory import PreQueueFactory
from gui.prb_control.factories.PrebattleFactory import PrebattleFactory
from gui.prb_control.factories.UnitFactory import UnitFactory
from gui.prb_control.settings import CTRL_ENTITY_TYPE
_ORDER_TO_CREATE = (CTRL_ENTITY_TYPE.PREBATTLE, CTRL_ENTITY_TYPE.UNIT, CTRL_ENTITY_TYPE.PREQUEUE)

class ControlFactoryDecorator(ControlFactory):

    def __init__(self):
        self.__factories = {CTRL_ENTITY_TYPE.PREBATTLE: PrebattleFactory(),
         CTRL_ENTITY_TYPE.UNIT: UnitFactory(),
         CTRL_ENTITY_TYPE.PREQUEUE: PreQueueFactory()}

    def start(self, ctx):
        for ctrlType in _ORDER_TO_CREATE:
            yield self.__factories[ctrlType].createFunctional(ctx)

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
        ctrlType = ctx.getCtrlType()
        if ctrlType in self.__factories:
            item = self.__factories[ctrlType].createEntry(ctx)
        else:
            LOG_ERROR('Entry factory is not found', ctx)
        return item

    def createEntryByAction(self, action):
        for factory in self.__factories.itervalues():
            result = factory.createEntryByAction(action)
            if result:
                return result

        return None

    def createFunctional(self, ctx):
        for ctrlType in _ORDER_TO_CREATE:
            item = self.__factories[ctrlType].createFunctional(ctx)
            if item is not None:
                yield item

        return
