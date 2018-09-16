# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/composite.py
from debug_utils import LOG_ERROR
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.factories.PreQueueFactory import PreQueueFactory
from gui.prb_control.factories.LegacyFactory import LegacyFactory
from gui.prb_control.factories.UnitFactory import UnitFactory
from gui.prb_control.settings import CTRL_ENTITY_TYPE, FUNCTIONAL_FLAG
_ORDER_TO_CREATE = (CTRL_ENTITY_TYPE.LEGACY, CTRL_ENTITY_TYPE.UNIT, CTRL_ENTITY_TYPE.PREQUEUE)

class ControlFactoryComposite(ControlFactory):

    def __init__(self):
        self.__factories = {CTRL_ENTITY_TYPE.LEGACY: LegacyFactory(),
         CTRL_ENTITY_TYPE.UNIT: UnitFactory(),
         CTRL_ENTITY_TYPE.PREQUEUE: PreQueueFactory()}

    def clear(self):
        self.__factories.clear()

    def get(self, ctrlType):
        return self.__factories[ctrlType] if ctrlType in self.__factories else None

    def createEntry(self, ctx):
        ctrlType = ctx.getCtrlType()
        if ctrlType in self.__factories:
            return self.__factories[ctrlType].createEntry(ctx)
        else:
            LOG_ERROR('Entry factory is not found', ctx)
            return None

    def createEntryByAction(self, action):
        for ctrlType in _ORDER_TO_CREATE:
            result = self.__factories[ctrlType].createEntryByAction(action)
            if result is not None:
                return result

        return

    def createEntity(self, ctx):
        for ctrlType in _ORDER_TO_CREATE:
            result = self.__factories[ctrlType].createEntity(ctx)
            if result is not None:
                return result

        return

    def createLeaveCtx(self, flags=FUNCTIONAL_FLAG.UNDEFINED, entityType=0):
        raise UserWarning('This method should not be reached in this context')

    def createStateEntity(self, entity):
        raise UserWarning('This method should not be reached in this context')
