# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/tank_setup_helper.py
import logging
from gui.prb_control.dispatcher import g_prbLoader
from th_async import th_async, th_await, await_callback
from BWUtil import AsyncReturn
from constants import QUEUE_TYPE
from gui.impl.lobby.tank_setup.tank_setup_sounds import playSlotActionSound
from items.components.supply_slot_categories import SlotCategories
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from helpers.dependency import replace_none_kwargs
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
ECONOMIC_DIRECTIVE_QUEUES = (QUEUE_TYPE.RANDOMS,
 QUEUE_TYPE.MAPBOX,
 QUEUE_TYPE.COMP7,
 QUEUE_TYPE.RANKED,
 QUEUE_TYPE.EPIC,
 QUEUE_TYPE.VERSUS_AI)
NONE_ID = -1
_CATEGORY_MASK = {category:1 << idx for idx, category in enumerate(SlotCategories.ORDER)}

def getCategoriesMask(categories):
    return sum((_CATEGORY_MASK[category] for category in categories))


def setLastSlotAction(viewModel, vehicle, setupName, actionType, intCD=NONE_ID, slotID=NONE_ID, leftID=NONE_ID, rightID=NONE_ID, leftIntCD=NONE_ID, rightIntCD=NONE_ID):
    with viewModel.lastSlotAction.transaction() as tx:
        tx.setActionType(actionType)
        tx.setIntCD(intCD)
        tx.setInstalledSlotId(slotID)
        tx.setLeftID(leftID)
        tx.setRightID(rightID)
        tx.setLeftIntCD(leftIntCD)
        tx.setRightIntCD(rightIntCD)
    playSlotActionSound(setupName, actionType, vehicle, int(intCD), leftIntCD, rightIntCD)


def clearLastSlotAction(viewModel):
    with viewModel.lastSlotAction.transaction() as tx:
        tx.setActionType('')
        tx.setIntCD(NONE_ID)
        tx.setInstalledSlotId(NONE_ID)
        tx.setLeftID(NONE_ID)
        tx.setRightID(NONE_ID)
        tx.setLeftIntCD(NONE_ID)
        tx.setRightIntCD(NONE_ID)


def __isQueueSelected(queueType):
    dispatcher = g_prbLoader.getDispatcher()
    return dispatcher.getFunctionalState().isQueueSelected(queueType) if dispatcher is not None else False


@replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def isEconomicDirBattleEnabled(sessionProvider=None):
    ctrl = sessionProvider.shared.prebattleSetups
    isArenaLoaded = ctrl.isArenaLoaded() if ctrl is not None else False
    return ARENA_BONUS_TYPE_CAPS.checkAny(sessionProvider.arenaVisitor.getArenaBonusType(), ARENA_BONUS_TYPE_CAPS.ECONOMIC_DIRECTIVES) if isArenaLoaded else any((__isQueueSelected(queueType) for queueType in ECONOMIC_DIRECTIVE_QUEUES))


class TankSetupAsyncCommandLock(object):
    __slots__ = ('__inProcess',)

    def __init__(self):
        self.__inProcess = False

    @property
    def isLocked(self):
        return self.__inProcess

    @th_async
    def tryAsyncCommand(self, func, *args, **kwargs):
        if not self.__inProcess:
            try:
                self._lock()
                result = yield th_await(func(*args, **kwargs))
                raise AsyncReturn(result)
            finally:
                self._unlock()

        else:
            _logger.warning('Action in process')
            raise AsyncReturn(None)
        return

    @th_async
    def tryAsyncCommandWithCallback(self, func, *args, **kwargs):
        if not self.__inProcess:
            try:
                self._lock()
                result = yield await_callback(func)(*args, **kwargs)
                raise AsyncReturn(result)
            finally:
                self._unlock()

        else:
            _logger.debug('Action in process')
            raise AsyncReturn(None)
        return

    def _lock(self):
        self.__inProcess = True

    def _unlock(self):
        self.__inProcess = False
