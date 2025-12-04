# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/gui_items/items_actions/actions.py
from adisp import adisp_process, adisp_async
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_view_model import State
from armory_yard.gui.window_events import showArmoryYardRewardWindow
from gui.shared.gui_items.items_actions.actions import AsyncGUIItemAction
from armory_yard.gui.shared.gui_items.processors.armory_yard_processors import CollectRewardsProcessor, BuyStepTokens
from armory_yard.gui.shared.gui_items.processors.armory_yard_reroll_processors import RerollQuest, AcceptReroll
from gui.shared.utils import decorators

class CollectRewardsAction(AsyncGUIItemAction):

    def __init__(self, stageCount, closeCallback=None):
        super(CollectRewardsAction, self).__init__()
        self.skipConfirm = True
        self.__stageCount = stageCount
        self.__closeCallback = closeCallback

    @adisp_async
    @adisp_process
    def _action(self, callback):
        result = yield CollectRewardsProcessor().request()
        if result.success and result.auxData is not None:
            showArmoryYardRewardWindow(bonuses=result.auxData, state=State.STAGE, stage=self.__stageCount, closeCallback=self.__closeCallback)
        callback(result)
        return


class BuyStepTokensAction(AsyncGUIItemAction):
    __slots__ = ('__count', '__currency')

    def __init__(self, count, currency):
        super(BuyStepTokensAction, self).__init__()
        self.skipConfirm = True
        self.__count = count
        self.__currency = currency

    @adisp_async
    @decorators.adisp_process('buyItem')
    def _action(self, callback):
        result = yield BuyStepTokens(self.__count, self.__currency).request()
        callback(result)

    def _showResult(self, result):
        pass


class RerollQuestAction(AsyncGUIItemAction):
    __slots__ = ('__questID', '__rerollCurrency')

    def __init__(self, questID, rerollCurrency=''):
        super(RerollQuestAction, self).__init__()
        self.skipConfirm = True
        self.__questID = questID
        self.__rerollCurrency = rerollCurrency

    @adisp_async
    @adisp_process
    def doAction(self, callback):
        result = yield self._action()
        callback(result)

    @adisp_async
    @decorators.adisp_process('loading')
    def _action(self, callback):
        result = yield RerollQuest(self.__questID, self.__rerollCurrency).request()
        callback(result)


class AcceptRerollAction(AsyncGUIItemAction):
    __slots__ = ('__conditionID', '__questID', '__rerollCurrency')

    def __init__(self, conditionID, questID):
        super(AcceptRerollAction, self).__init__()
        self.skipConfirm = True
        self.__conditionID = conditionID
        self.__questID = questID

    @adisp_async
    @decorators.adisp_process('armoryYard/waitReroll')
    def _action(self, callback):
        result = yield AcceptReroll(self.__conditionID, self.__questID).request()
        callback(result)

    def _showResult(self, result):
        pass
