# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_award_view.py
from constants import LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import WindowFlags, ViewSettings, WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_award_view_model import WtEventAwardViewModel
from white_tiger.gui.impl.lobby.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from white_tiger.gui.impl.lobby.wt_event_sound import WTEventAwardsScreenSound
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow, LobbyWindow
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.shared import event_dispatcher
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import isWTEventProgressionQuest
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from gui.server_events.bonuses import getNonQuestBonuses
from white_tiger.gui.wt_event_helpers import backportTooltipDecorator

class WTEventAwardView(ViewImpl):
    __slots__ = ('_tooltipItems', '_isFinalReward', '_questData')
    __gameController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.white_tiger.lobby.AwardsView(), model=WtEventAwardViewModel())
        settings.args = args
        settings.kwargs = kwargs
        self._tooltipItems = {}
        self._isFinalReward = False
        self._questData = kwargs.get('questData', None)
        super(WTEventAwardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(WTEventAwardView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventAwardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return WtEventLootBoxTooltipView(isHunterLootBox=event.getArgument('isHunterLootBox')) if contentID == R.views.white_tiger.lobby.tooltips.LootBoxTooltipView() else super(WTEventAwardView, self).createToolTipContent(event, contentID)

    def _onLoading(self, questId, *args, **kwargs):
        super(WTEventAwardView, self)._onLoading(*args, **kwargs)
        bonuses = []
        if self._questData:
            for key, value in self._questData.iteritems():
                bonuses.extend(getNonQuestBonuses(key, value))

        else:
            bonuses = self.__gameController.getQuestRewards(questId)
        rAwardsView = R.strings.event.WTEventAwardsView
        hasBoxReward = self.__hasBoxReward(bonuses)
        isPostBattle = not isWTEventProgressionQuest(questId)
        if isPostBattle:
            statusText = backport.text(rAwardsView.status.postBattle())
        else:
            elementsCount = self.__gameController.getDisplayedCollectionProgress(questId)
            self._isFinalReward = elementsCount == self.__gameController.getTotalLevelsCount()
            if self._isFinalReward:
                statusText = backport.text(rAwardsView.status.all())
                WTEventAwardsScreenSound.playProgressionDoneSound()
            else:
                statusText = backport.text(rAwardsView.status.part(), elements=elementsCount)
                WTEventAwardsScreenSound.playProgressionProgressSound()
        with self.getViewModel().transaction() as model:
            model.setIsEventAvailable(self.__gameController.isAvailable())
            model.setIsFinalReward(self._isFinalReward)
            model.setIsBoxReward(hasBoxReward)
            model.setIsPostBattle(isPostBattle)
            model.setTitle(backport.text(rAwardsView.title()))
            model.setStatus(statusText)
            packBonusModelAndTooltipData(bonuses, model.mainRewards, self._tooltipItems, getWtEventBonusPacker())
        self.__addListeners()

    def _finalize(self):
        super(WTEventAwardView, self)._finalize()
        WTEventAwardsScreenSound.playProgressionClosed()
        self.__removeListeners()
        self._tooltipItems = None
        if self._isFinalReward and self.__gameController.needToShowOutroVideo():
            self.__gameController.showOutroVideo()
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

    def __init__(self, questId, questData=None, parent=None):
        super(WTEventSpecialAwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN, content=WTEventAwardView(questId=questId, questData=questData), layer=WindowLayer.OVERLAY, parent=parent)
