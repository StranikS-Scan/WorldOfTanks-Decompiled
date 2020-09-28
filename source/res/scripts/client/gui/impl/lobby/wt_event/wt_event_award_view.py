# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_award_view.py
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from constants import LOOTBOX_TOKEN_PREFIX
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_award_view_model import WtEventAwardViewModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.lobby.wt_event.tooltips.wt_event_carousel_tooltip_view import WtEventCarouselTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showWtEventLootboxOpenWindow
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.server_events import IEventsCache

class WTEventAwardView(ViewImpl):
    __slots__ = ('__tooltipItems', '__isFinalReward')
    __gameController = dependency.descriptor(IGameEventController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventAward(), flags=ViewFlags.OVERLAY_VIEW, model=WtEventAwardViewModel())
        self.__tooltipItems = {}
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventAwardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            tooltipData = self.__tooltipItems.get(tooltipId)
            if tooltipData is None:
                return
            if tooltipData.specialAlias == TOOLTIPS_CONSTANTS.WT_EVENT_BOSS_TICKET:
                ticketsCount = self.__gameController.getWtEventTokensCount()
                window = DecoratedTooltipWindow(WtEventCarouselTooltipView(ticketsCount), parent=self.getParentWindow(), useDecorator=False)
                window.move(event.mouse.positionX, event.mouse.positionY)
            else:
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(WTEventAwardView, self).createToolTip(event)

    def _onLoading(self, questId, *args, **kwargs):
        super(WTEventAwardView, self)._onLoading(*args, **kwargs)
        rAwardsView = R.strings.wt_event.WTEventAwardsView
        elementsCount, bonuses, isFinalReward = self.__gameController.getDataByQuestName(questId)
        if elementsCount == 0:
            bonuses = self.__getRewardFromQuest(questId)
        hasBoxReward = self.__hasBoxReward(bonuses)
        if hasBoxReward and elementsCount == 0:
            statusText = backport.text(rAwardsView.status.special_box())
        elif isFinalReward:
            statusText = backport.text(rAwardsView.status.all())
        else:
            statusText = backport.text(rAwardsView.status.part(), elements=elementsCount)
        with self.getViewModel().transaction() as model:
            model.setIsFinalReward(isFinalReward)
            model.setIsBoxReward(hasBoxReward)
            model.setTitle(backport.text(rAwardsView.title()))
            model.setStatus(statusText)
            packBonusModelAndTooltipData(bonuses, model.mainRewards, self.__tooltipItems, getWtEventBonusPacker)
        self.__isFinalReward = isFinalReward
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventAwardView, self)._onLoaded(*args, **kwargs)
        wt_event_sound.playCollectionAward(self.__isFinalReward)

    def _finalize(self):
        super(WTEventAwardView, self)._finalize()
        self.__removeListeners()
        self.__tooltipItems = None
        return

    def __getRewardFromQuest(self, questId):
        quests = self.__eventsCache.getAllQuests(lambda quest: quest.getID() == questId)
        bonuses = quests[questId].getBonuses() if questId in quests else []
        return [ bonus for bonus in bonuses if bonus.getName() != 'dossier' ]

    def __addListeners(self):
        self.viewModel.onAwardOpen += self.__onAwardOpen

    def __removeListeners(self):
        self.viewModel.onAwardOpen -= self.__onAwardOpen

    @staticmethod
    def __hasBoxReward(bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'battleToken':
                value = bonus.getValue()
                for name in value.iterkeys():
                    if name.startswith(LOOTBOX_TOKEN_PREFIX):
                        return True

        return False

    def __onAwardOpen(self):
        showWtEventLootboxOpenWindow(boxType='wt_special')
        self.destroyWindow()


class WTEventAwardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, questId, parent=None):
        super(WTEventAwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=WTEventAwardView(questId=questId), parent=parent, decorator=None)
        return
