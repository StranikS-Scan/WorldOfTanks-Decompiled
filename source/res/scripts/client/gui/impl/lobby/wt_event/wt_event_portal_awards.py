# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_portal_awards.py
import logging
from functools import partial
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import PortalType
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_model import WtEventPortalAwardsModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_multiopen_renderer_model import WtEventMultiopenRendererModel
from gui.impl.lobby.wt_event.wt_event_constants import SpecialVehicleSource
from gui.impl.lobby.wt_event.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from gui.impl.lobby.wt_event.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.lobby.wt_event.wt_event_sound import playLootboxBackToPortalsExitEvent, WTEventAwardsScreenVideoSound
from gui.impl.pub.lobby_window import LobbyWindow
from gui.game_control.loot_boxes_controller import LootBoxAwardsManager
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.Waiting import Waiting
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.wt_event.wt_event_simple_bonus_packers import sortBonuses, HUNTER_BONUSES_ORDER
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker, BOSS_ALL_BONUSES_ORDER
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, setGuaranteedAward, fillAdditionalAwards, fillVehicleAward
from gui.wt_event.wt_event_helpers import isSpecialVehicleReceived
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class WtEventPortalAwards(WtEventBasePortalAwards):
    __slots__ = ('__lootBoxType', '__count', '__openedCount', '__allOpenedBoxesCount')
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, lootBoxType, awards, count, openedCount, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventPortalAwards(), model=WtEventPortalAwardsModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventPortalAwards, self).__init__(settings, awards)
        self.__lootBoxType = lootBoxType
        self.__count = count
        self.__openedCount = openedCount
        self.__allOpenedBoxesCount = openedCount

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        return WtGuaranteedRewardTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtGuaranteedRewardTooltipView() else super(WtEventPortalAwards, self).createToolTipContent(event, contentID)

    def _onLoaded(self, *args, **kwargs):
        super(WtEventPortalAwards, self)._onLoaded(*args, **kwargs)
        WTEventAwardsScreenVideoSound.playVideoSound(self.__lootBoxType)

    def _finalize(self):
        wt_event_sound.playLootBoxAwardsExit()
        super(WtEventPortalAwards, self)._finalize()

    def _updateModel(self):
        super(WtEventPortalAwards, self)._updateModel()
        with self.viewModel.transaction() as model:
            _clearRewardsModels(model)
            isBossLootBox = self.__isBossLootBox()
            model.setIsBossLootBox(isBossLootBox)
            model.setOpenedBoxesCount(self.__allOpenedBoxesCount)
            setLootBoxesCount(model.portalAvailability, self.__lootBoxType)
            if self.__openedCount > 1:
                model.setIsMultipleOpening(True)
                self.__setMultipleAwards(model)
            elif isBossLootBox:
                _fillBossAwards(model, self._awards, self._tooltipItems)
                setGuaranteedAward(model.guaranteedAward)
            else:
                _fillMainAwards(EventLootBoxes.WT_HUNTER, model.rewards, self._awards, self._tooltipItems)
            wt_event_sound.playLootBoxAwardsReceived(self.__count)

    def _addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__onCacheResync
        self.viewModel.onAnimationEnded += self.__animationEnded
        self.viewModel.onOpenMore += self.__openMore
        self.viewModel.onBackToPortal += self.__goToPortal
        super(WtEventPortalAwards, self)._addListeners()

    def _removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__onCacheResync
        self.viewModel.onBackToPortal -= self.__goToPortal
        self.viewModel.onAnimationEnded -= self.__animationEnded
        self.viewModel.onOpenMore -= self.__openMore
        super(WtEventPortalAwards, self)._removeListeners()

    def _getBoxType(self):
        return self.__lootBoxType

    def _goToPreview(self, args):
        intCD = int(args.get('intCD', 0))
        if intCD == 0:
            _logger.error('Invalid intCD to preview the bonus')
            return
        else:
            item = self.__itemsCache.items.getItemByCD(intCD)
            if item is None:
                _logger.error('Invalid intCD to preview the bonus vehicle')
                return
            itemType = item.itemTypeID
            if itemType == GUI_ITEM_TYPE.VEHICLE:
                self._showVehiclePreview(intCD)
            elif itemType == GUI_ITEM_TYPE.STYLE:
                vehicleCD = getVehicleCDForStyle(item)
                event_dispatcher.showStylePreview(vehicleCD, item, item.getDescription(), partial(_backToAwardView, self.__lootBoxType, self._awards), backBtnDescrLabel=backport.text(R.strings.event.awardView.backToAwards()))
            return

    def _goToStorage(self):
        playLootboxBackToPortalsExitEvent()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        event_dispatcher.showEventStorageWindow()

    def __goToPortal(self):
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL), scope=EVENT_BUS_SCOPE.LOBBY)
        portalType = PortalType.BOSS if self.__lootBoxType == EventLootBoxes.WT_BOSS else PortalType.HUNTER
        event_dispatcher.showEventPortalWindow(portalType, self.__count)
        self.destroyWindow()

    def __onCacheResync(self, _, diff):
        self.__updateLimits()

    def __updateLimits(self):
        with self.viewModel.transaction() as model:
            setGuaranteedAward(model.guaranteedAward)

    def __animationEnded(self, args):
        isAnimationEnded = args.get('isAnimationEnd')
        if isAnimationEnded:
            event_dispatcher.showVehicleAwardWindow(vehicleSource=SpecialVehicleSource.MULTIPLE_OPENING, parent=self.getParentWindow())

    def __openMore(self):
        parent = self.getParentWindow()
        self._boxesCtrl.requestLootBoxOpen(self.__lootBoxType, self.__count, parentWindow=parent, callbackUpdate=self.__updateData)

    def __updateData(self, data):
        if data:
            WTEventAwardsScreenVideoSound.playVideoSound(self.__lootBoxType)
            self._awards = data.get('awards', [])
            self.__openedCount = data.get('openedBoxes', 0)
            self.__allOpenedBoxesCount += self.__openedCount
            self._updateModel()

    def __isBossLootBox(self):
        return self.__lootBoxType == EventLootBoxes.WT_BOSS

    def __setMultipleAwards(self, model):
        rewardGroups = model.getMultiRewards()
        rewardGroups.clear()
        for group in self._awards:
            rewardGroups.addViewModel(self.__createLootBoxRewardsGroup(group))

        rewardGroups.invalidate()

    def __createLootBoxRewardsGroup(self, bonuses):
        groupModel = WtEventMultiopenRendererModel()
        groupModel.setHasSpecialVehicle(isSpecialVehicleReceived(bonuses))
        _fillMainAwards(self.__lootBoxType, groupModel.rewards, bonuses, self._tooltipItems)
        return groupModel


class WtEventPortalAwardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, lootBoxType, awards, count, openedCount, parent=None):
        super(WtEventPortalAwardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventPortalAwards(lootBoxType=lootBoxType, awards=awards, count=count, openedCount=openedCount), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


def _backToAwardView(lootBoxType, awards):
    Waiting.show('updating')
    event_dispatcher.showHangar()
    event_dispatcher.showEventPortalAwardsWindow(lootBoxType, awards)
    Waiting.hide('updating')


def _fillBossAwards(model, bonuses, tooltipItems):
    groupedBonuses = LootBoxAwardsManager.getBossGroupedBonuses(bonuses)
    _fillMainAwards(EventLootBoxes.WT_BOSS, model.rewards, groupedBonuses.main, tooltipItems)
    fillAdditionalAwards(model.additionalRewards, groupedBonuses.additional, tooltipItems)
    fillVehicleAward(model, groupedBonuses.vehicle)


def _fillMainAwards(lootBoxType, model, bonuses, tooltipItems):
    model.clearItems()
    order = BOSS_ALL_BONUSES_ORDER if lootBoxType == EventLootBoxes.WT_BOSS else HUNTER_BONUSES_ORDER
    packBonusModelAndTooltipData(sorted(bonuses, key=lambda bonus: sortBonuses(bonus, order)), model, tooltipItems, getWtEventBonusPacker)


def _clearRewardsModels(model):
    model.setIsMultipleOpening(False)
    rewardGroups = model.getMultiRewards()
    rewardGroups.clear()
    model.rewards.clearItems()
    model.additionalRewards.clearItems()
