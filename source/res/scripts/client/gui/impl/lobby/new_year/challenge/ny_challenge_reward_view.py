# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_reward_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.Scaleform.framework.application import AppEntry
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import Celebrity
from gui.impl.lobby.new_year.challenge.ny_challenge_reward_base_view import ChallengeRewardBaseView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.backport.backport_pop_over import createPopOverData, BackportPopOverContent
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel as Discount
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_reward_view_model import ChallengeRewardViewModel, Type
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker, packBonusModelAndTooltipData
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_constants import CELEBRITY_MARATHON_PREFIX
from gui.shared.event_dispatcher import hideVehiclePreview, showCelebrityChallengeReward, showHangar
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency, uniprof
from new_year.celebrity.celebrity_quests_helpers import marathonTokenCountExtractor, getCelebrityQuestBonusesByFullQuestID
from new_year.ny_constants import SyncDataKeys
from new_year.variadic_discount import VARIADIC_DISCOUNT_NAME, updateSelectedVehicleForBonus
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import INewYearController
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import NyCelebrityRewardEvent, NyGladeVisibilityEvent
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.VIEW, WindowLayer.WINDOW)

class ChallengeRewardView(ChallengeRewardBaseView):
    __slots__ = ('__blur', '__prevAppBackgroundAlpha')
    __appLoader = dependency.descriptor(IAppLoader)
    __eventsCache = dependency.descriptor(IEventsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, layoutID, questID, instantly, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = ChallengeRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__questID = questID
        self.__instantly = instantly
        self.__celebrity = None
        self.__blur = None
        self.__prevAppBackgroundAlpha = 0
        self._tooltips = {}
        super(ChallengeRewardView, self).__init__(settings, *args, **kwargs)
        return

    @uniprof.regionDecorator(label='ny_challenge_reward', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(ChallengeRewardView, self)._initialize(*args, **kwargs)
        self.__blur = CachedBlur(enabled=False)
        app = self.__appLoader.getApp()
        self.__prevAppBackgroundAlpha = app.getBackgroundAlpha()
        app.setBackgroundAlpha(0)
        self._changeLayersVisibility(True, _CHANGE_LAYERS_VISIBILITY)
        ctx = {'guestName': self.__celebrity.value,
         'isSaveCamera': not self.__instantly}
        g_eventBus.handleEvent(NyCelebrityRewardEvent(NyCelebrityRewardEvent.REWARD_CHALLENGE_VIEW_OPENED, ctx=ctx))

    def _onLoaded(self, *args, **kwargs):
        super(ChallengeRewardView, self)._onLoaded(*args, **kwargs)
        self.__nyController.onDataUpdated += self.__onDataUpdated

    @uniprof.regionDecorator(label='ny_challenge_reward', scope='exit')
    def _finalize(self):
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        g_eventBus.handleEvent(NyGladeVisibilityEvent(eventType=NyGladeVisibilityEvent.START_FADE_OUT), scope=EVENT_BUS_SCOPE.DEFAULT)
        if self.__blur is not None:
            self.__blur.fini()
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(self.__prevAppBackgroundAlpha)
        self._changeLayersVisibility(False, _CHANGE_LAYERS_VISIBILITY)
        if not self.isInPreview and self.__celebrity is not None:
            ctx = {'guestName': self.__celebrity.value}
            g_eventBus.handleEvent(NyCelebrityRewardEvent(NyCelebrityRewardEvent.REWARD_CHALLENGE_VIEW_CLOSED, ctx=ctx))
        super(ChallengeRewardView, self)._finalize()
        return

    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            if event.getArgument('popoverId') == Discount.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID:
                alias = VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER
                variadicID = event.getArgument('variadicID')
                data = createPopOverData(alias, {'variadicID': variadicID,
                 'parentWindow': self.getParentWindow()})
                return BackportPopOverContent(popOverData=data)
        return super(ChallengeRewardView, self).createPopOverContent(event)

    def _onLoading(self, *args, **kwargs):
        if self.__questID.startswith(CELEBRITY_MARATHON_PREFIX):
            self.__celebrity = Celebrity.GUESTM
        else:
            self.__celebrity = Celebrity.GUESTA
        super(ChallengeRewardView, self)._onLoading(*args, **kwargs)

    def _fillModel(self, model):
        super(ChallengeRewardView, self)._fillModel(model)
        model.setType(Type.CHALLENGE)
        model.setCelebrity(self.__celebrity.value)
        if self.__celebrity == Celebrity.GUESTM:
            quest = self.__eventsCache.getQuestByID(self.__questID)
            tokenCount = marathonTokenCountExtractor(quest)
            model.setCompletedQuests(tokenCount)
            packBonusModelAndTooltipData(quest.getBonuses(), model.getRewards(), getChallengeBonusPacker(), self._tooltips)
        else:
            packBonusModelAndTooltipData(getCelebrityQuestBonusesByFullQuestID(self.__questID), model.getRewards(), getChallengeBonusPacker(), self._tooltips)

    def __updateVariadicRewards(self):
        with self.viewModel.transaction() as model:
            for reward in model.getRewards():
                if reward.getName() == VARIADIC_DISCOUNT_NAME:
                    result = updateSelectedVehicleForBonus(reward)
                    model.setIsDiscountSelected(result)

    def __onDataUpdated(self, keys, _):
        if SyncDataKeys.SELECTED_DISCOUNTS in keys:
            self.__updateVariadicRewards()

    def _backCallback(self):
        hideVehiclePreview(back=False, close=True)
        if self._nyController.isEnabled():
            showCelebrityChallengeReward(self.__questID, instantly=True)
        else:
            showHangar()
        super(ChallengeRewardView, self)._backCallback()


class ChallengeRewardViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, questID, instantly, parent=None, *args, **kwargs):
        layout = R.views.lobby.new_year.ChallengeRewardView()
        super(ChallengeRewardViewWindow, self).__init__(content=ChallengeRewardView(layout, questID, instantly, *args, **kwargs), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
