# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge_reward_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.view_lifecycle_watcher import ViewLifecycleWatcher
from gui.impl.backport.backport_pop_over import createPopOverData, BackportPopOverContent
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.bonuses.discount_bonus_model import DiscountBonusModel as Discount
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_reward_view_model import ChallengeRewardViewModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.new_year import DiscountPopoverHandler
from gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, nyCreateToolTipContentDecorator
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import showNewYearVehiclesView
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from new_year.celebrity.celebrity_quests_helpers import marathonTokenCountExtractor, getFinalCelebrityMarathonQuest
from new_year.ny_constants import SyncDataKeys
from new_year.variadic_discount import VARIADIC_DISCOUNT_NAME, updateSelectedVehicleForBonus
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import INewYearController
from uilogging.decorators import loggerEntry, simpleLog, loggerTarget
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger

@loggerTarget(logKey=NY_LOG_KEYS.NY_CELEBRITY_CHALLENGE, loggerCls=NYLogger)
class ChallengeRewardView(ViewImpl):
    __eventsCache = dependency.descriptor(IEventsCache)
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, layoutID, questID):
        settings = ViewSettings(layoutID)
        settings.model = ChallengeRewardViewModel()
        self.__questID = questID
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        self._tooltips = {}
        super(ChallengeRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ChallengeRewardView, self).getViewModel()

    @simpleLog(argsIndex=0, argMap={True: NY_LOG_ACTIONS.NY_DISCOUNT_FROM_REWARD_VIEW}, preProcessAction=lambda x: x.getArgument('popoverId') == Discount.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID)
    def createPopOverContent(self, event):
        if event.contentID == R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent():
            if event.getArgument('popoverId') == Discount.NEW_YEAR_DISCOUNT_APPLY_POPOVER_ID:
                alias = VIEW_ALIAS.NY_SELECT_VEHICLE_FOR_DISCOUNT_POPOVER
                variadicID = event.getArgument('variadicID')
                data = createPopOverData(alias, {'variadicID': variadicID})
                return BackportPopOverContent(popOverData=data)
        return super(ChallengeRewardView, self).createPopOverContent(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        return super(ChallengeRewardView, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(ChallengeRewardView, self).createToolTip(event)

    @loggerEntry
    def _onLoaded(self, *args, **kwargs):
        setOverlayHangarGeneral(onState=True)
        NewYearSoundsManager.playEvent(NewYearSoundEvents.CELEBRITY_SCREEN_REWARD)
        super(ChallengeRewardView, self)._onLoaded(*args, **kwargs)

    def _onLoading(self, *args, **kwargs):
        quest = self.__eventsCache.getQuestByID(self.__questID)
        with self.viewModel.transaction() as model:
            packBonusModelAndTooltipData(quest.getBonuses(), model.getRewards(), getNewYearBonusPacker(), self._tooltips)
            tokenCount = marathonTokenCountExtractor(quest)
            self.viewModel.setCompletedQuests(tokenCount)
            finalQuest = getFinalCelebrityMarathonQuest()
            self.viewModel.setIsFinal(finalQuest.getID() == quest.getID())

    def _initialize(self, *args, **kwargs):
        super(ChallengeRewardView, self)._initialize()
        g_messengerEvents.onLockPopUpMessages(lockHigh=True)
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        g_messengerEvents.onUnlockPopUpMessages()
        setOverlayHangarGeneral(onState=False)

    def __updateVariadicRewards(self):
        with self.viewModel.transaction() as model:
            for reward in model.getRewards():
                if reward.getName() == VARIADIC_DISCOUNT_NAME:
                    updateSelectedVehicleForBonus(reward)

            model.setSyncInitiator((model.getSyncInitiator() + 1) % 1000)

    def __addListeners(self):
        model = self.viewModel
        model.sendCloseEvent += self.__onClose
        self.viewModel.goToNyVehicleBranch += self.__onToVehicleBranch
        self.__nyController.onDataUpdated += self.__onDataUpdated
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        self.__viewLifecycleWatcher.start(app.containerManager, [DiscountPopoverHandler(self.__onDiscountPopoverOpened, self.__onDiscountPopoverClosed)])

    def __removeListeners(self):
        model = self.viewModel
        model.sendCloseEvent -= self.__onClose
        self.viewModel.goToNyVehicleBranch -= self.__onToVehicleBranch
        self.__nyController.onDataUpdated -= self.__onDataUpdated
        self.__viewLifecycleWatcher.stop()

    def __onDataUpdated(self, keys):
        if SyncDataKeys.SELECTED_DISCOUNTS in keys:
            self.__updateVariadicRewards()

    def __onToVehicleBranch(self):
        showNewYearVehiclesView()
        self.__onClose()

    def __onClose(self, *_):
        self.destroyWindow()

    def __onDiscountPopoverOpened(self):
        self.viewModel.setIsDiscountPopoverOpened(True)

    def __onDiscountPopoverClosed(self):
        self.viewModel.setIsDiscountPopoverOpened(False)


class ChallengeRewardViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, questID, parent=None):
        super(ChallengeRewardViewWindow, self).__init__(content=ChallengeRewardView(R.views.lobby.new_year.ChallengeRewardView(), questID), parent=parent, layer=WindowLayer.TOP_WINDOW)
