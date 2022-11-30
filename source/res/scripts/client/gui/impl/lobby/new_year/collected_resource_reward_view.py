# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/collected_resource_reward_view.py
import BigWorld
from typing import Optional
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.collected_resources_reward_view_model import CollectedResourcesRewardViewModel
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.new_year.ny_views_helpers import NyExecuteCtx
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData, getNewYearBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.event_dispatcher import hideVehiclePreview, showPiggyBankRewards
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from new_year.ny_piggy_bank_helper import PiggyBankConfigHelper
from new_year.ny_preview import getVehiclePreviewID
from gui.impl.pub import ViewImpl
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, IFriendServiceController
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.VIEW,
 WindowLayer.WINDOW,
 WindowLayer.TOP_WINDOW,
 WindowLayer.OVERLAY)
_GUEST_BONUSES_ORDER = ({'getName': 'customizations',
  'getIcon': 'inscription'},
 {'getName': 'customizations',
  'getIcon': 'emblem'},
 {'getName': 'customizations',
  'getIcon': 'projectionDecal'},
 {'getName': 'customizations',
  'getIcon': 'style'})

def guestQuestBonusSortOrder(zippedBonus):
    for index, criteria in enumerate(_GUEST_BONUSES_ORDER):
        for method, value in criteria.items():
            bonus, _, __ = zippedBonus
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_GUEST_BONUSES_ORDER)


class CollectedResourceRewardView(ViewImpl):
    __slots__ = ('__quests', '__rewards', '__ctx', '__styleIntCD', '_tooltips')
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __appLoader = dependency.instance(IAppLoader)
    __friendsService = dependency.descriptor(IFriendServiceController)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID, args=args, kwargs=kwargs)
        settings.model = CollectedResourcesRewardViewModel()
        self.__styleIntCD = None
        self.__quests = kwargs.get('quests', [])
        self.__rewards = kwargs.get('rewards', {})
        self.__ctx = kwargs.get('ctx', {})
        self._tooltips = {}
        super(CollectedResourceRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CollectedResourceRewardView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(CollectedResourceRewardView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(CollectedResourceRewardView, self)._initialize()
        setOverlayHangarGeneral(onState=True)
        self.__changeLayersVisibiliy(True, _CHANGE_LAYERS_VISIBILITY)

    def _finalize(self):
        setOverlayHangarGeneral(onState=False)
        self._tooltips.clear()
        self.__changeLayersVisibiliy(False, _CHANGE_LAYERS_VISIBILITY)
        if self.__nyController.isFinished():
            event_dispatcher.showHangar()
        super(CollectedResourceRewardView, self)._finalize()

    def _getEvents(self):
        events = super(CollectedResourceRewardView, self)._getEvents()
        return events + ((self.viewModel.onStylePreview, self.__onStylePreview),)

    def _onLoading(self, *args, **kwargs):
        super(CollectedResourceRewardView, self)._onLoading(*args, **kwargs)
        collectingCount = PiggyBankConfigHelper.getMaxCollectingResources(self.__quests)
        with self.viewModel.transaction() as model:
            model.setNumberOfCollecting(collectingCount)
            model.setRecommendedGraphicsPreset(BigWorld.detectGraphicsPresetFromSystemSettings())
            model.setIs3dSceneVisible(BigWorld.worldDrawEnabled())
            self.__fillRewards(model, self.__rewards)

    def __fillRewards(self, model, rewards):
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        bonuses = []
        for rewardName, rewardData in rewards.iteritems():
            bonuses.extend(getNonQuestBonuses(rewardName, rewardData))

        packBonusModelAndTooltipData(bonuses, rewardsModel, packer=getNewYearBonusPacker(), tooltipsData=self._tooltips, sortKey=guestQuestBonusSortOrder)
        model.setIsStyle(self.__hasBonusStyle(bonuses))
        rewardsModel.invalidate()

    def __hasBonusStyle(self, bonuses):
        for bonus in bonuses:
            if bonus.getName() != 'customizations':
                continue
            for bonusData in bonus.getList():
                if bonusData.get('itemTypeID') == GUI_ITEM_TYPE.STYLE:
                    self.__styleIntCD = bonusData.get('intCD')
                    return True

        return False

    def __onStylePreview(self):
        if self.__styleIntCD is None:
            return
        else:
            styleItem = self.__itemsCache.items.getItemByCD(self.__styleIntCD)
            if styleItem is None:
                return
            viewAlias = self.__ctx.get('viewAlias')
            cameraObject = self.__ctx.get('cameraObject')
            isNyOpened = bool(viewAlias)

            def _backCallback():
                hideVehiclePreview(back=False, close=False)
                if not self.__nyController.isEnabled():
                    event_dispatcher.showHangar()
                elif isNyOpened:
                    ctx = NyExecuteCtx('PiggyBankRewards', (self.__quests, self.__rewards), {'instantly': True})
                    NewYearNavigation.switchFromStyle(viewAlias, cameraObject, executeAfterLoaded=ctx)
                else:
                    event_dispatcher.showHangar()
                    showPiggyBankRewards(self.__quests, self.__rewards, instantly=True)

            label = R.strings.ny.collectedResourceRewardScreen.stylePreview.backLabel()
            backBtnDescrLabel = backport.text(label)
            self.__friendsService.leaveFriendHangar()
            event_dispatcher.showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback, backBtnDescrLabel=backBtnDescrLabel, showCloseBtn=False)
            NewYearNavigation.onAnchorSelected('')
            return

    def __changeLayersVisibiliy(self, isHide, layers):
        lobby = self.__appLoader.getDefLobbyApp()
        if lobby:
            if isHide:
                lobby.containerManager.hideContainers(layers, time=0.3)
            else:
                lobby.containerManager.showContainers(layers, time=0.3)
            self.__appLoader.getApp().graphicsOptimizationManager.switchOptimizationEnabled(not isHide)


class CollectingResourceRewardViewWindow(LobbyNotificationWindow):
    __slots__ = ('__blur',)

    def __init__(self, quests, rewards, ctx=None):
        super(CollectingResourceRewardViewWindow, self).__init__(content=CollectedResourceRewardView(R.views.lobby.new_year.CollectedResourcesRewardView(), quests=quests, rewards=rewards, ctx=ctx), layer=WindowLayer.FULLSCREEN_WINDOW)
        self.__blur = None
        return

    def load(self):
        if self.__blur is None:
            self.__blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        super(CollectingResourceRewardViewWindow, self).load()
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        super(CollectingResourceRewardViewWindow, self)._finalize()
        return
