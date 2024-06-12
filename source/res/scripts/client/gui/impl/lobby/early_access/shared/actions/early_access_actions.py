# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/shared/actions/early_access_actions.py
from adisp import adisp_async
from gui.shared.gui_items.items_actions.actions import AsyncGUIItemAction
from gui.shared.utils import decorators
from gui.impl.lobby.early_access.shared.processors.early_access_processors import BuyEarlyAccessTokensProcessor
from skeletons.gui.game_control import IEarlyAccessController
from helpers import dependency

class BuyEarlyAccessTokensAction(AsyncGUIItemAction):
    __slots__ = ('__count',)
    __earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self, count):
        super(BuyEarlyAccessTokensAction, self).__init__()
        self.__count = count

    @adisp_async
    @decorators.adisp_process('buyItem')
    def _action(self, callback):
        result = yield BuyEarlyAccessTokensProcessor(self.__count).request()
        callback(result)
