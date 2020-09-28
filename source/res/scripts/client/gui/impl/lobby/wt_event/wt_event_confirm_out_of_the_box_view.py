# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_confirm_out_of_the_box_view.py
import typing
from async import async, await, BrokenPromiseError, AsyncScope, AsyncEvent, AsyncReturn
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_confirm_out_of_the_box_view_model import WtEventConfirmOutOfTheBoxViewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.wt_event.wt_event_award import WTEventLootBoxAwardsManager
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import backportTooltipDecorator, vehCompCreateToolTipContentDecorator
from shared_utils import findFirst
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus

class WtEventConfirmOutOfTheBoxView(ViewImpl):
    __slots__ = ('__rewards', '_tooltipItems', '__event', '__scope', '__result')

    def __init__(self, layoutID, rewards):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = WtEventConfirmOutOfTheBoxViewModel()
        self.__rewards = rewards
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = False
        self._tooltipItems = {}
        super(WtEventConfirmOutOfTheBoxView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventConfirmOutOfTheBoxView, self).getViewModel()

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            pass

        raise AsyncReturn(self.__result)

    @vehCompCreateToolTipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(WtEventConfirmOutOfTheBoxView, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WtEventConfirmOutOfTheBoxView, self).createToolTip(event)

    def _onLoaded(self, *args, **kwargs):
        super(WtEventConfirmOutOfTheBoxView, self)._onLoaded(self, *args, **kwargs)
        Waiting.hide('loadPage')

    def _onLoading(self, *args, **kwargs):
        super(WtEventConfirmOutOfTheBoxView, self)._onLoading(*args, **kwargs)
        Waiting.show('loadPage')
        with self.viewModel.transaction() as model:
            bonuses = WTEventLootBoxAwardsManager.composeBonuses([self.__rewards])
            self.__filterBonuses(bonuses)
            packBonusModelAndTooltipData(bonuses, model.rewards, self._tooltipItems, getWtEventBonusPacker)

    def _initialize(self, *args, **kwargs):
        super(WtEventConfirmOutOfTheBoxView, self)._initialize(*args, **kwargs)
        self.viewModel.onPickReward += self.__onPickReward

    def _finalize(self):
        self.viewModel.onPickReward -= self.__onPickReward
        self.__scope.destroy()
        self._tooltipItems = None
        super(WtEventConfirmOutOfTheBoxView, self)._finalize()
        return

    @staticmethod
    def __filterBonuses(bonuses):
        vehicle = findFirst(lambda bonus: bonus.getName() == 'vehicles', bonuses)
        if vehicle is None:
            return
        else:
            slot = findFirst(lambda bonus: bonus.getName() == 'slots', bonuses)
            if slot is None:
                return
            bonuses.remove(slot)
            return

    def __onPickReward(self):
        self.__result = True
        self.__event.set()


class WtEventConfirmOutOfTheBoxWindow(WindowImpl):
    __slots__ = ('__content',)

    def __init__(self, rewards, parent):
        self.__content = WtEventConfirmOutOfTheBoxView(R.views.lobby.wt_event.WtEventConfirmOutOfTheBoxView(), rewards=rewards)
        super(WtEventConfirmOutOfTheBoxWindow, self).__init__(WindowFlags.WINDOW, content=self.__content, parent=parent)

    def wait(self):
        return self.__content.wait()
