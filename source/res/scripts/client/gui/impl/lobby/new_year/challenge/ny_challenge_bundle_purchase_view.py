# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_bundle_purchase_view.py
import typing
from account_helpers.AccountSettings import AccountSettings, NY_SACK_INFO_VISITED, NY_SACK_INFO_LAST_SELECTED
from adisp import adisp_process
from constants import PREMIUM_ENTITLEMENTS, Configs
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui import DialogsInterface, SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsForSackMeta
from gui.game_control.wallet import WalletController
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import BundleType
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_purchase_dialog_view_model import BundlePurchaseDialogViewModel, PurchaseState
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.bundle_sack_model import SackState, BundleSackModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import getNYSackBonusPacker
from gui.impl.lobby.new_year.ny_views_helpers import NyExecuteCtx
from gui.impl.lobby.new_year.tooltips.ny_sack_random_reward_tooltip import NySackRandomRewardTooltip
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, ADDITIONAL_BONUS_NAME_GETTERS
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import CreditsBonus
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.shop import showBuyGoldForSack
from helpers import dependency, time_utils
from helpers.server_settings import serverSettingsChangeListener
from items.components.ny_constants import NySackLootBox, NY_SACK_CATEGORY_TO_LEVEL, NY_SACK_LEVEL_TO_CATEGORY
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from new_year.celebrity.celebrity_quests_helpers import getDogLevel
from new_year.ny_constants import NYObjects, NyTabBarChallengeView, CHALLENGE_TAB_TO_CAMERA_OBJ
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_preview import getVehiclePreviewID
from new_year.ny_processor import BuySackProcessor
from shared_utils import first
from skeletons.gui.game_control import IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import Dict
_BUNDLE_TYPE_TO_CATEGORY = {NySackLootBox.LEVEL_1: BundleType.LEVEL1,
 NySackLootBox.LEVEL_2: BundleType.LEVEL2,
 NySackLootBox.LEVEL_3: BundleType.LEVEL3,
 NySackLootBox.LEVEL_4: BundleType.LEVEL4}
_LEVEL_TO_BUNDLE_TYPE = {1: BundleType.LEVEL1,
 2: BundleType.LEVEL2,
 3: BundleType.LEVEL3,
 4: BundleType.LEVEL4}
_BUNDLE_TYPE_TO_LEVEL = {v.value:k for k, v in _LEVEL_TO_BUNDLE_TYPE.iteritems()}

def __getAdditionalNameItems(bonus):
    item, _ = first(bonus.getItems().iteritems())
    return item.descriptor.name if item is not None else bonus.getName()


_BONUS_NAME_GETTERS = {'items': __getAdditionalNameItems}
_BONUS_NAME_GETTERS.update(ADDITIONAL_BONUS_NAME_GETTERS)
_BONUSES_ORDER = ('customizations_style',
 'customizations',
 'randomNy24Toy',
 'randomNyInstruction',
 'randomNyGuide',
 'randomNyBooklet',
 'freeXP',
 'tokens',
 'booster_credits',
 PREMIUM_ENTITLEMENTS.PLUS,
 PREMIUM_ENTITLEMENTS.BASIC,
 Currency.GOLD,
 Currency.CREDITS,
 'booster_xp',
 'booster_crew_xp',
 'booster_free_xp_and_crew_xp',
 'largeRepairkit',
 'largeMedkit',
 'autoExtinguishers',
 'smallRepairkit',
 'smallMedkit',
 'handExtinguishers',
 'slots')

def _bonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = _BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return _BONUSES_ORDER.index(bonusName) if bonusName in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _bonusesOrderCmp(bonus1, bonus2):
    return cmp(bonus2.getValue(), bonus1.getValue()) if isinstance(bonus1, CreditsBonus) and isinstance(bonus2, CreditsBonus) else cmp(_bonusesSortOrder(bonus1), _bonusesSortOrder(bonus2))


class BundlePurchaseDialogView(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __wallet = dependency.descriptor(IWalletController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.challenge.BundlePurchaseDialog())
        settings.args = args
        settings.kwargs = kwargs
        settings.model = BundlePurchaseDialogViewModel()
        super(BundlePurchaseDialogView, self).__init__(settings)
        self._tooltips = {}
        self.__currentBundleLevel = self.__getBundleLevelOnInit()
        self.__helper = self.__nyController.sacksHelper
        self.__isRequestToBuyProcessing = False

    @property
    def viewModel(self):
        return super(BundlePurchaseDialogView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(BundlePurchaseDialogView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return NySackRandomRewardTooltip(event.getArgument('resourceType')) if contentID == R.views.lobby.new_year.tooltips.NySackRandomRewardTooltip() else super(BundlePurchaseDialogView, self).createToolTipContent(event, contentID)

    def canBeClosed(self):
        return not self.__isRequestToBuyProcessing

    def _onLoading(self, *args, **kwargs):
        super(BundlePurchaseDialogView, self)._onLoading(*args, **kwargs)
        g_clientUpdateManager.addMoneyCallback(self.__onMoneyChangeHandler)
        self.__updateModel()

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BundlePurchaseDialogView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onBuy, self.__onBuy),
         (self.viewModel.onSwitchBundle, self.__onSwitchBundle),
         (self.viewModel.onStylePreview, self.__onShowStylePreview),
         (self.viewModel.onOpenConverter, self.__onOpenConverter),
         (self.viewModel.onBuyGold, self.__onBuyGold),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__nyController.sacksHelper.onUpdated, self.__onSacksUpdated))

    def __updateModel(self):
        with self.viewModel.transaction():
            self.__updateCurrentBundle()
            self.__updatePrice()
            self.__makeAndFillReward()
            self.__updateBundles()

    @replaceNoneKwargsModel
    def __updateCurrentBundle(self, model=None):
        model.setCurrentBundle(_LEVEL_TO_BUNDLE_TYPE.get(self.__currentBundleLevel, BundleType.LEVEL1).value)
        model.setIsBundleReceived(self.__currentBundleLevel <= self.__getCurrentLevel())
        eventEndTimeTill = getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime()
        model.setTimeTill(eventEndTimeTill)

    @replaceNoneKwargsModel
    def __updateBundles(self, model=None):
        sacks = self.__helper.getAllBoxes()
        sacksModel = model.getSacks()
        sacksModel.clear()
        for sack in sacks:
            sackModel = BundleSackModel()
            sackModel.setBundleType(_BUNDLE_TYPE_TO_CATEGORY.get(sack.getCategory(), BundleType.LEVEL1).value)
            sackModel.setSackState(self.__getSackState(NY_SACK_CATEGORY_TO_LEVEL.get(sack.getCategory(), 1)))
            sacksModel.addViewModel(sackModel)

        sacksModel.invalidate()

    @replaceNoneKwargsModel
    def __updatePrice(self, model=None):
        currentBalance = self.__itemsCache.items.stats.money
        currency, price = self.__helper.getBoxPrices(self.__currentBundleLevel)
        currencyStatus = self.__wallet.componentsStatuses.get(currency)
        currentSackState = self.__getSackState(self.__currentBundleLevel)
        if self.__wallet.isNotAvailable:
            status = PurchaseState.UNAVAILABLE
        elif currencyStatus != WalletController.STATUS.AVAILABLE:
            status = PurchaseState.UNAVAILABLE
        elif currentSackState == SackState.LOCKED:
            status = PurchaseState.LOCKED
        else:
            status = PurchaseState.AVAILABLE
        model.setCurrency(currency)
        model.setPrice(price)
        model.setBalance(int(currentBalance.get(currency, 0)))
        model.setPurchaseState(status)

    @replaceNoneKwargsModel
    def __makeAndFillReward(self, model=None):
        bonusPacker = getNYSackBonusPacker()
        bonuses = self.__helper.getBoxBonusesInfo(NY_SACK_LEVEL_TO_CATEGORY.get(self.__currentBundleLevel, 1))
        bonuses.sort(cmp=_bonusesOrderCmp)
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        packBonusModelAndTooltipData(bonuses, rewardsModel, bonusPacker, self._tooltips)
        rewardsModel.invalidate()

    def __getBundleLevelOnInit(self):
        currentLevel = self.__getCurrentLevel()
        if currentLevel < len(NySackLootBox.ALL):
            return currentLevel + 1
        isVisited = AccountSettings.getUIFlag(NY_SACK_INFO_VISITED)
        if not isVisited:
            AccountSettings.setUIFlag(NY_SACK_INFO_VISITED, True)
            return 1
        return AccountSettings.getUIFlag(NY_SACK_INFO_LAST_SELECTED)

    def __onMoneyChangeHandler(self, *_):
        self.__updatePrice()

    def __onWalletStatusChanged(self):
        self.__updatePrice()

    @serverSettingsChangeListener(Configs.NY_DOG_CONFIG.value)
    def __onServerSettingsChanged(self, *_):
        self.__updateModel()

    def __onSacksUpdated(self):
        self.__updateModel()

    @decorators.adisp_process('newYear/buyBundle')
    def __onBuy(self):
        self.__isRequestToBuyProcessing = True
        result = yield BuySackProcessor(self.__currentBundleLevel - 1).request()
        if result.success:
            self.__nyController.onBoughtToy()
            self.__nyController.setHangToyEffectEnabled(True)
            self.__nyController.hangToys()
            serviceChannel = self.__systemMessages.proto.serviceChannel
            serviceChannel.pushClientMessage(result.auxData, SCH_CLIENT_MSG_TYPE.NY_SACK_BOUGHT_MESSAGE)
        elif result.userMsg:
            SystemMessages.pushMessage(text=backport.text(R.strings.system_messages.newYear.sack.bought.error.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.system_messages.newYear.sack.bought.error.header())})
        self.__isRequestToBuyProcessing = False
        self.destroyWindow()

    def __onSwitchBundle(self, args):
        bundleType = args.get('bundleType')
        if bundleType is None:
            return
        else:
            self.__currentBundleLevel = _BUNDLE_TYPE_TO_LEVEL.get(bundleType, 1)
            if AccountSettings.getUIFlag(NY_SACK_INFO_VISITED):
                AccountSettings.setUIFlag(NY_SACK_INFO_LAST_SELECTED, self.__currentBundleLevel)
            self.__updateModel()
            return

    @adisp_process
    def __onOpenConverter(self):
        currency, price = self.__helper.getBoxPrices(self.__currentBundleLevel)
        if price and currency and currency == Currency.CREDITS:
            _, _ = yield DialogsInterface.showDialog(ExchangeCreditsForSackMeta(name=backport.text(R.strings.ny.bundlePurchaseDialog.logo.subtitle.dyn(_LEVEL_TO_BUNDLE_TYPE.get(self.__currentBundleLevel).value)()), price=price))

    def __onBuyGold(self):
        currency, price = self.__helper.getBoxPrices(self.__currentBundleLevel)
        if price and currency and currency == Currency.GOLD:
            showBuyGoldForSack(price)

    def __onShowStylePreview(self, args):
        styleIntCD = int(args.get('intCD'))
        styleItem = self.__itemsCache.items.getItemByCD(styleIntCD)
        if styleItem is None:
            return
        else:
            guestID = NyTabBarChallengeView.GUEST_D

            def _backCallback():
                if not self.__nyController.isEnabled():
                    event_dispatcher.showHangar()
                else:
                    ctx = NyExecuteCtx('showBundlePurchaseDialog', (), {'instantly': True})
                    NewYearNavigation.switchFromStyle(viewAlias=ViewAliases.CELEBRITY_VIEW, tabName=guestID, objectName=CHALLENGE_TAB_TO_CAMERA_OBJ.get(guestID, NYObjects.CELEBRITY), forceShowMainView=True, executeAfterLoaded=ctx)

            showStylePreview(getVehiclePreviewID(styleItem), styleItem, styleItem.getDescription(), backCallback=_backCallback)
            self.destroyWindow()
            return

    @classmethod
    def __getCurrentLevel(cls):
        return getDogLevel() + 1

    @classmethod
    def __getSackState(cls, sackLevel):
        currentLevel = cls.__getCurrentLevel()
        if sackLevel <= currentLevel:
            return SackState.RECEIVED
        return SackState.AVAILABLE if sackLevel == currentLevel + 1 else SackState.LOCKED


class BundlePurchaseDialogWindow(LobbyWindow):
    __slots__ = ('_blur', '_doBlur')

    def __init__(self, parent=None, doBlur=True, layer=WindowLayer.WINDOW, *args, **kwargs):
        super(BundlePurchaseDialogWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BundlePurchaseDialogView(*args, **kwargs), layer=layer, parent=parent)
        self._blur = None
        self._doBlur = doBlur
        return

    def _initialize(self):
        super(BundlePurchaseDialogWindow, self)._initialize()
        if self._doBlur:
            self._blur = CachedBlur(enabled=True, ownLayer=self.layer - 1)
        NewYearSoundsManager.setOverlayState(True)

    def _finalize(self):
        if self._blur:
            self._blur.fini()
            self._blur = None
        NewYearSoundsManager.setOverlayState(False)
        super(BundlePurchaseDialogWindow, self)._finalize()
        return
