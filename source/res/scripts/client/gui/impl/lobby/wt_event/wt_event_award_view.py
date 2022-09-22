# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_award_view.py
from constants import LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import WindowFlags, ViewSettings, WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_award_view_model import WtEventAwardViewModel
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.lobby.wt_event.wt_event_sound import WTEventAwardsScreenSound
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow, LobbyWindow
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.shared import event_dispatcher
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import isWTEventProgressionQuest, backportTooltipDecorator
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController

class WTEventAwardView(ViewImpl):
    __slots__ = ('_tooltipItems',)
    __gameController = dependency.descriptor(IEventBattlesController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventAward(), model=WtEventAwardViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self._tooltipItems = {}
        super(WTEventAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventAwardView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return WtEventLootBoxTooltipView(isHunterLootBox=event.getArgument('isHunterLootBox')) if contentID == R.views.lobby.wt_event.tooltips.WtEventLootBoxTooltipView() else super(WTEventAwardView, self).createToolTipContent(event, contentID)

    def _onLoading(self, questId, *args, **kwargs):
        super(WTEventAwardView, self)._onLoading(*args, **kwargs)
        rAwardsView = R.strings.event.WTEventAwardsView
        bonuses = self.__gameController.getQuestRewards(questId)
        hasBoxReward = self.__hasBoxReward(bonuses)
        isPostBattle = not isWTEventProgressionQuest(questId)
        description = ''
        isFinalReward = False
        if isPostBattle:
            statusText = backport.text(rAwardsView.status.postBattle())
            description = backport.text(rAwardsView.desciption())
        else:
            elementsCount = self.__gameController.getDisplayedCollectionProgress(questId)
            isFinalReward = elementsCount == 40
            if isFinalReward:
                statusText = backport.text(rAwardsView.status.all())
                WTEventAwardsScreenSound.playProgressionDoneSound()
            else:
                statusText = backport.text(rAwardsView.status.part(), elements=elementsCount)
                WTEventAwardsScreenSound.playProgressionProgressSound()
        with self.getViewModel().transaction() as model:
            model.setIsFinalReward(isFinalReward)
            model.setIsBoxReward(hasBoxReward)
            model.setIsPostBattle(isPostBattle)
            model.setTitle(backport.text(rAwardsView.title()))
            model.setStatus(statusText)
            model.setDescription(description)
            packBonusModelAndTooltipData(bonuses, model.mainRewards, self._tooltipItems, getWtEventBonusPacker())
        self.__addListeners()

    def _finalize(self):
        super(WTEventAwardView, self)._finalize()
        WTEventAwardsScreenSound.playProgressionClosed()
        self.__removeListeners()
        self._tooltipItems = None
        return

    def __addListeners(self):
        self.viewModel.onAwardOpen += self.__goToStorage
        self.__gameController.onEventPrbChanged += self.__onEventPrbChanged

    def __removeListeners(self):
        self.viewModel.onAwardOpen -= self.__goToStorage
        self.__gameController.onEventPrbChanged -= self.__onEventPrbChanged

    @staticmethod
    def __hasBoxReward(bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'battleToken':
                value = bonus.getValue()
                for name in value.iterkeys():
                    if name.startswith(LOOTBOX_TOKEN_PREFIX):
                        return True

        return False

    def __goToStorage(self):
        self.destroyWindow()
        parent = self.getParentWindow()
        event_dispatcher.showEventStorageWindow(parent)

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()


class WTEventAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, questId, parent=None):
        super(WTEventAwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTEventAwardView(questId=questId), parent=parent)


class WTEventSpecialAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, questId, parent=None):
        super(WTEventSpecialAwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=WTEventAwardView(questId=questId), layer=WindowLayer.OVERLAY, parent=parent)
