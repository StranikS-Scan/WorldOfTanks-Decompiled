# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/bundle_view.py
from __future__ import absolute_import
from adisp import adisp_process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.money import Currency
from halloween.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from halloween.gui.impl.lobby.hw_helpers.bonuses_formatters import HalloweenBonusesAwardsComposer, getHWMetaAwardFormatter, getImgName
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from halloween.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from halloween.gui.impl.lobby.tooltips.vehicle_tooltip import VehicleTooltipView
from halloween.gui.shared.event_dispatcher import showHalloweenShopBundle
from halloween.gui.shop import showHWBuyGoldForBundle
from halloween.gui.sounds.sound_constants import BUNDLE_ENTER, BUNDLE_EXIT
from halloween.gui.game_control.halloween_artefacts_controller import getBonusPriority
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_shop_controller import IHalloweenShopController
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys, HWLogActions
from halloween_common.halloween_constants import ArtefactsSettings
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from gui.impl.gen import R
from halloween.gui.impl.lobby.base_view import BaseView
from frameworks.wulf import ViewSettings, ViewFlags
from halloween.gui.impl.gen.view_models.views.lobby.bundle_view_model import BundleViewModel, WindowType, TitleStates
from halloween.gui.impl.gen.view_models.views.lobby.bundle_model import BundleModel
from ids_generators import SequenceIDGenerator
from halloween.gui.sounds import playSound
MAX_BONUSES_IN_VIEW = 10
AMOUNT_OF_KEYS_DEFAULT = 1
KEY_TOKEN = ArtefactsSettings.KEY_TOKEN.replace(':', '_')
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class BundleView(BaseView):
    _appLoader = dependency.descriptor(IAppLoader)
    _itemsCache = dependency.descriptor(IItemsCache)
    _hwController = dependency.descriptor(IHalloweenController)
    _hwArtefactCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwShopCtrl = dependency.descriptor(IHalloweenShopController)

    def __init__(self, layoutID=R.views.halloween.mono.lobby.bundles_shop(), artefactID='', *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=BundleViewModel())
        super(BundleView, self).__init__(settings)
        self.__artefactID = artefactID
        self.__bonusCache = {}
        self.__tooltipCtx = {}
        self.__idGen = SequenceIDGenerator()
        self.__uiLogger = HWMetricsLogger(HWLogKeys.EXCHANGE_VIEW)
        source = kwargs.get('source')
        if source:
            self.__uiLogger.onLog(HWLogActions.OPEN, HWLogKeys.EXCHANGE_VIEW, source)

    @property
    def viewModel(self):
        return super(BundleView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs, isWulfTooltip=bonus.isWulfTooltip), self.getParentWindow(), event=event)
                window.load()
                return window
        return super(BundleView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.halloween.mono.lobby.tooltips.key_tooltip():
            return KeyTooltipView(isPostBattle=False)
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        if contentID == R.views.halloween.mono.lobby.tooltips.vehicle_tooltip():
            tooltipId = event.getArgument('tooltipId')
            bonus = self.__bonusCache.get(tooltipId)
            vehicleCD = bonus.specialArgs[0]
            return VehicleTooltipView(vehicleCD=vehicleCD)
        return super(BundleView, self).createToolTipContent(event, contentID)

    def _subscribe(self):
        super(BundleView, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'stats.gold': self.__fillMoneyBalance})

    def _initialize(self, *args, **kwargs):
        super(BundleView, self)._initialize(*args, **kwargs)
        playSound(BUNDLE_ENTER)

    def _finalize(self):
        playSound(BUNDLE_EXIT)
        super(BundleView, self)._finalize()

    def _unsubscribe(self):
        super(BundleView, self)._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _onLoading(self, *args, **kwargs):
        super(BundleView, self)._onLoading(*args, **kwargs)
        self.__fillBalance()
        self.__fillMoneyBalance()
        self.__fillViewModel()

    def __fillMoneyBalance(self, *args, **kwargs):
        self.viewModel.setGoldCount(int(self.__getMoney(Currency.GOLD)))

    def __fillBalance(self, *args, **kwargs):
        balanceLayoutID = R.aliases.halloween.shared.MoneyBalance()
        self.setChildView(balanceLayoutID, MoneyBalance(layoutID=balanceLayoutID))

    def __fillViewModel(self, *args, **kwargs):
        self.__fillBalance()
        with self.viewModel.transaction() as tx:
            artefact = self._hwArtefactCtrl.getArtefact(self.__artefactID)
            if artefact and not self._hwArtefactCtrl.isArtefactOpened(artefact.artefactID):
                tx.setWindowType(WindowType.DECRYPT if self._hwArtefactCtrl.isArtefactReceived(artefact.artefactID) else WindowType.SKIP)
                tx.setLackOfKeys(self._hwArtefactCtrl.getLackOfKeysForArtefact(artefact.artefactID))
            else:
                tx.setWindowType(WindowType.KEYWIDGET)
                tx.setLackOfKeys(AMOUNT_OF_KEYS_DEFAULT)
            self._loadBundles(tx, artefact)

    def _loadBundles(self, model, artefact):
        bundles = self._hwShopCtrl.keyBundles()
        bundlesModel = model.getBundles()
        bundlesModel.clear()
        processedGroups = []
        lackKeys = self._hwArtefactCtrl.getLackOfKeysForArtefacts()
        hasShopBundle = False
        hasKeyBundle = False
        model.setSlide(self._hwArtefactCtrl.getIndex(self._hwArtefactCtrl.selectedArtefactID))
        for bundle in sorted(bundles, key=lambda bundle: (bundle.groupID, bundle.orderInGroup)):
            if bundle.isWebShopBundle:
                if bundle.limit is not None and self._hwShopCtrl.getPurchaseCount(bundle.bundleID) >= bundle.limit:
                    continue
            elif self._hwArtefactCtrl.getLackOfKeysForArtefacts() == 0:
                continue
            if bundle.groupID in processedGroups:
                continue
            bundleModel = BundleModel()
            bundleModel.setId(bundle.bundleID)
            bundleModel.setIsShopBundle(bundle.isWebShopBundle)
            bundleModel.setDescrGroupKey(str(bundle.descrGroupKey))
            if not bundle.isWebShopBundle:
                bundleModel.setMaximumBundleCount(lackKeys)
                if bundle.limit > 0:
                    bundleModel.setKeysInBundle(lackKeys)
                    bundleModel.price.setName(bundle.price.currency)
                    bundleModel.price.setValue(lackKeys * bundle.price.amount)
                    bundleModel.price.setIsEnough(self.__isEnoughMoney(bundle, lackKeys))
                elif bundle.limit is None:
                    keys = self._hwShopCtrl.getKeysInBundle(bundle.bundleID)
                    bundleModel.setKeysInBundle(keys)
                    bundleModel.price.setName(bundle.price.currency)
                    bundleModel.price.setValue(bundle.price.amount)
                    bundleModel.price.setIsEnough(self.__isEnoughMoney(bundle, keys))
                else:
                    continue
                hasKeyBundle = True
            else:
                keys = self._hwShopCtrl.getKeysInBundle(bundle.bundleID)
                bundleModel.setKeysInBundle(keys)
                bundleModel.setMaximumBundleCount(keys)
                hasShopBundle = True
            processedGroups.append(bundle.groupID)
            sortedBonuses = sorted(bundle.bonuses, key=getBonusPriority)
            formatter = HalloweenBonusesAwardsComposer(MAX_BONUSES_IN_VIEW, getHWMetaAwardFormatter())
            bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
            rewards = bundleModel.getBonuses()
            rewards.clear()
            for bonus in bonusRewards:
                if bonus.bonusName in (KEY_TOKEN, ArtefactsSettings.KEY_NOTIFY_TOKEN):
                    continue
                tooltipId = '{}'.format(next(self.__idGen))
                self.__bonusCache[tooltipId] = bonus
                reward = BonusItemViewModel()
                reward.setUserName(str(bonus.userName))
                reward.setName(bonus.bonusName)
                reward.setValue(str(bonus.label))
                reward.setLabel(str(bonus.label))
                reward.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                reward.setOverlayType(bonus.getOverlayType(AWARDS_SIZES.SMALL))
                reward.setTooltipId(tooltipId)
                rewards.addViewModel(reward)
                reward.setTooltipContentId(str(bonus.tooltip))

            bundlesModel.addViewModel(bundleModel)

        model.setTitleState(self.__getTitleState(hasShopBundle, hasKeyBundle))
        bundlesModel.invalidate()
        return

    def _onPurchaseBundle(self, args):
        bundleId = args.get('id', None)
        count = int(args.get('amount', 1))
        if count <= 0:
            return
        elif bundleId is None:
            return
        else:
            bundle = self._hwShopCtrl.getBundleByID(bundleId)
            if not bundle:
                return
            count = min(count, self._hwArtefactCtrl.getLackOfKeysForArtefacts())
            if bundle.isWebShopBundle and bundle.url:
                showHalloweenShopBundle(bundle.url)
                self.__uiLogger.onClick(HWLogKeys.BUNDLE, bundleId)
                return
            elif not self.__isEnoughMoney(bundle, count=count):
                showHWBuyGoldForBundle(bundle.price.amount, {})
                return
            self.__processPurchase(bundleId, count)
            self._onClose()
            return

    def _getEvents(self):
        return [(self.viewModel.onClose, self._onClose),
         (self.viewModel.onPurchase, self._onPurchaseBundle),
         (self._hwShopCtrl.onBundlesUpdated, self.__onBundlesUpdated),
         (self._hwArtefactCtrl.onArtefactKeyUpdated, self.__onArtefactKeyUpdated)]

    def __isEnoughMoney(self, bundle, count):
        return self._itemsCache.items.stats.isResourcesConsumptionAllowed and self.__getMoney(bundle.price.currency) >= bundle.price.amount * count

    def __onArtefactKeyUpdated(self):
        self.__fillViewModel()

    @adisp_process
    def __processPurchase(self, bundleID, count):
        yield self._hwShopCtrl.purchaseBundle(bundleID, count)

    def __onBundlesUpdated(self):
        self.__fillViewModel()

    def __getMoney(self, currency):
        return self._itemsCache.items.stats.money.get(currency, 0)

    def __getTitleState(self, hasShopBundle, hasKeyBundle):
        if hasShopBundle and not hasKeyBundle:
            return TitleStates.ONLYSHOPBUNDLE
        return TitleStates.ONLYKEYSBUNDLE if not hasShopBundle and hasKeyBundle else TitleStates.DEFAULT
