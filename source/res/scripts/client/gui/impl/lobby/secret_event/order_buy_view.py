# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/order_buy_view.py
import sys
from zipfile import crc32
from constants import EventPackGuiTypes
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel as FrmtModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_tooltip_model import GeneralTooltipModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_buy_model import OrderBuyModel
from gui.impl.gen.view_models.views.lobby.secret_event.simple_general_model import SimpleGeneralModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from gui.impl.lobby.secret_event import EventViewMixin, EnergyMixin, RewardListMixin, convertPriceToTuple
from gui.impl.lobby.secret_event.general_info_tip import GeneralInfoTip
from gui.ingame_shop import showBuyGoldForSecretEventItem
from gui.server_events.game_event.shop import ENERGY_TOKEN_PREFIX
from gui.shared import event_dispatcher, g_eventBus, events
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.secret_event.action_hangar_view import ActionHangarView
from skeletons.gui.impl import IGuiLoader
from gui.impl.lobby.secret_event.sound_constants import SOUND, ACTION_VIEW_SETTINGS
from gui.Scaleform.framework.entities.view_sound import ViewSoundMixin

class OrderBuyView(FullScreenDialogView, EventViewMixin, EnergyMixin, RewardListMixin, ViewSoundMixin):
    gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    MAX_REWARDS_LIST_COUNT = sys.maxint
    _COMMON_SOUND_SPACE = ACTION_VIEW_SETTINGS

    def __init__(self, layoutID=R.views.lobby.secretEvent.OrderConfirmWindow(), generalID=None, orderID=None, parentID=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = OrderBuyModel()
        self.__generalID = generalID
        self.__orderID = orderID
        self.__parentID = parentID
        super(OrderBuyView, self).__init__(settings, False)
        self._initSoundManager()

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if 'rewardTooltip' in tooltipId:
                window = RewardListMixin.createToolTip(self, event)
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                item = self.gameEventController.getShop().getItem(self.__orderID)
                args = (ACTION_TOOLTIPS_TYPE.ITEM,
                 GUI_ITEM_TYPE.VEHICLE,
                 convertPriceToTuple(*item.getPrice()),
                 convertPriceToTuple(*item.getDefPrice()),
                 True)
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
            if window is None:
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId), self.getParentWindow())
            if window:
                window.load()
                return window
        return super(OrderBuyView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return GeneralInfoTip(event.contentID, event.getArgument('id', self.gameEventController.getSelectedCommanderID()), event.getArgument('type', GeneralTooltipModel.DEFAULT)) if event.contentID == R.views.lobby.secretEvent.GeneralTooltip() else None

    def _onLoading(self, *args, **kwargs):
        super(OrderBuyView, self)._onLoading(*args, **kwargs)
        self.__setParams()

    def _onAcceptClicked(self):
        super(OrderBuyView, self)._onAcceptClicked()
        if self.viewModel.orderPrice.getIsEnough():
            if self.__parentID is not None and self.__parentID == R.views.lobby.secretEvent.OrderSelectWindow():
                g_eventBus.handleEvent(events.DestroyUnboundViewEvent(self.__parentID))
            ActionHangarView.onEvenetHangarLoaded += self._buy
            guiLoader = dependency.instance(IGuiLoader)
            hangar = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.secretEvent.ActionHangarWindow())
            event_dispatcher.loadSecretEventTabMenu(ActionMenuModel.BASE)
            if hangar is not None:
                hangar.onEvenetHangarLoaded()
        else:
            showBuyGoldForSecretEventItem(self.viewModel.orderPrice.getValue())
        return

    def _buy(self, *kv, **kw):
        self.soundManager.playInstantSound(SOUND.SECRET_EVENT_ORDER_CONFIRM_SOUND_EVENT)
        self.gameEventController.getShop().buy(self.__orderID)
        ActionHangarView.onEvenetHangarLoaded -= self._buy

    def _initialize(self):
        super(OrderBuyView, self)._initialize()
        self._eventCacheSubscribe()
        self._itemsCache.onSyncCompleted += self.__setParams
        self._startSoundManager()

    def _finalize(self):
        super(OrderBuyView, self)._finalize()
        self._eventCacheUnsubscribe()
        self._itemsCache.onSyncCompleted -= self.__setParams
        self._deinitSoundManager()

    def _closeView(self):
        self._onCancelClicked()

    def _getUncompletedGenerals(self):
        return [ commander for commander in self.gameEventController.getCommanders() if not self.gameEventController.getCommander(commander).isCompleted() ]

    def __setParams(self, *args, **kwargs):
        shopItem = self.gameEventController.getShop().getItem(self.__orderID)
        isPremium = shopItem.hasSingleReward
        isMegaPack = shopItem.packGuiType == EventPackGuiTypes.MEGA_PACK.value
        dialogType = OrderBuyModel.SIMPLE if isPremium else (OrderBuyModel.MEGAPACK if isMegaPack else OrderBuyModel.PRIZE)
        cacheKey = crc32(self.__orderID)
        rewards = self.getRewards(shopItem, cacheKey)
        with self.viewModel.transaction() as vm:
            vm.setDialogType(dialogType)
            if not isMegaPack:
                self.__setTitleArgs(vm.getTitleArgs(), (('name', R.strings.event.unit.name.num(self.__generalID)()), ('item', R.strings.event.order.window.packName.dyn(shopItem.packGuiType)())))
                if isPremium:
                    vm.setTitleBody(R.strings.event.order.confirm.simpleTitle())
                    commander = self.gameEventController.getCommander(self.__generalID)
                    energyData = self.getEnergyData(commander, commander.getBuyEnergyID(), forceEnabled=True)
                    vm.setGeneralIcon(energyData.hangarIcon)
                else:
                    vm.setTitleBody(R.strings.event.order.confirm.title())
                    vm.setGeneralIcon(R.images.gui.maps.icons.secretEvent.generalIcons.c_192x192.dyn('g_icon{0}'.format(self.__generalID))())
            self.fillPriceByShopItem(vm.orderPrice, shopItem)
            vm.setIsAcceptDisabled(False)
            bonuses = []
            energyBonuses = []
            if isMegaPack:
                vm.generalList.clearItems()
                self.__setTitleArgs(vm.getTitleArgs(), (('name', R.strings.event.berlin.pack.name()),))
                vm.setTitleBody(R.strings.event.order.confirm.shortTitle())
                for comID in self._getUncompletedGenerals():
                    commanderModel = SimpleGeneralModel()
                    commanderModel.setId(comID)
                    commanderModel.setGeneralIcon(R.images.gui.maps.icons.secretEvent.generalIcons.dyn('g_icon{0}'.format(comID))())
                    vm.generalList.addViewModel(commanderModel)

                vm.generalList.invalidate()
            for idx, bonus in enumerate(rewards):
                energyID = first(bonus['specialArgs'] or [])
                if isinstance(energyID, str) and energyID.startswith(ENERGY_TOKEN_PREFIX):
                    energyBonuses.append((idx, bonus))
                bonuses.append((idx, bonus))

            if energyBonuses:
                self.fillStubRewardListWithIndex(vm.orderList, energyBonuses, cacheKey=cacheKey)
            self.fillStubRewardListWithIndex(vm.rewardList, bonuses, cacheKey=cacheKey)

    def __setTitleArgs(self, arrModel, frmtArgs):
        for name, resource in frmtArgs:
            frmtModel = FrmtModel()
            frmtModel.setName(name)
            frmtModel.setValue(resource)
            arrModel.addViewModel(frmtModel)

        arrModel.invalidate()
