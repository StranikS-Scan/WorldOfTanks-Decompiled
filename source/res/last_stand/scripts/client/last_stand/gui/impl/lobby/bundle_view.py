# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/bundle_view.py
from adisp import adisp_process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.server_events.awards_formatters import AWARDS_SIZES
from gui.shared.money import Currency
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from last_stand.gui.impl.lobby.ls_helpers.bonuses_formatters import LSBonusesAwardsComposer, getLSMetaAwardFormatter, getImgName
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from last_stand.gui.impl.lobby.tooltips.key_tooltip import KeyTooltipView
from last_stand.gui.shared.event_dispatcher import showLSShopBundle
from last_stand.gui.shop import showBuyGoldForBundle
from last_stand.gui.sounds.sound_constants import BUNDLE_VIEW_ENTER, BUNDLE_VIEW_EXIT
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_shop_controller import ILSShopController
from last_stand_common.last_stand_constants import ArtefactsSettings
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.impl.gen import R
from last_stand.gui.impl.lobby.base_view import BaseView, EventLobbyWindow
from frameworks.wulf import ViewSettings, WindowLayer
from frameworks.wulf import WindowFlags
from last_stand.gui.impl.gen.view_models.views.lobby.bundle_view_model import BundleViewModel, WindowType, TitleStates
from last_stand.gui.impl.gen.view_models.views.lobby.bundle_model import BundleModel
from last_stand.gui.game_control.ls_artefacts_controller import compareBonusesByPriority
from ids_generators import SequenceIDGenerator
from last_stand.gui.sounds import playSound
MAX_BONUSES_IN_VIEW = 10
AMOUNT_OF_KEYS_DEFAULT = 1
KEY_TOKEN = ArtefactsSettings.KEY_TOKEN.replace(':', '_')
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class BundleView(BaseView):
    _itemsCache = dependency.descriptor(IItemsCache)
    lsCtrl = dependency.descriptor(ILSController)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    lsShopCtrl = dependency.descriptor(ILSShopController)

    def __init__(self, layoutID=R.views.last_stand.mono.lobby.bundle_view(), artefactID=''):
        settings = ViewSettings(layoutID, model=BundleViewModel())
        super(BundleView, self).__init__(settings)
        self.__artefactID = artefactID
        self.__bonusCache = {}
        self.__tooltipCtx = {}
        self.__idGen = SequenceIDGenerator()

    @property
    def viewModel(self):
        return super(BundleView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(BundleView, self)._initialize()
        playSound(BUNDLE_VIEW_ENTER)

    def _finalize(self):
        playSound(BUNDLE_VIEW_EXIT)
        super(BundleView, self)._finalize()

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
        if contentID == R.views.last_stand.mono.lobby.tooltips.key_tooltip():
            return KeyTooltipView(isPostBattle=False)
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(BundleView, self).createToolTipContent(event, contentID)

    def _subscribe(self):
        super(BundleView, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'stats.gold': self.__fillMoneyBalance})

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
        balanceLayoutID = R.aliases.last_stand.shared.MoneyBalance()
        self.setChildView(balanceLayoutID, MoneyBalance(layoutID=balanceLayoutID))

    def __fillViewModel(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            artefact = self.lsArtifactsCtrl.getArtefact(self.__artefactID)
            if artefact and not self.lsArtifactsCtrl.isArtefactOpened(artefact.artefactID):
                tx.setWindowType(WindowType.DECRYPT if self.lsArtifactsCtrl.isArtefactReceived(artefact.artefactID) else WindowType.SKIP)
                tx.setLackOfKeys(self.lsArtifactsCtrl.getLackOfKeysForArtefact(artefact.artefactID))
            else:
                tx.setWindowType(WindowType.KEYWIDGET)
                tx.setLackOfKeys(AMOUNT_OF_KEYS_DEFAULT)
            self._loadBundles(tx, artefact)

    def _loadBundles(self, model, artefact):
        bundles = self.lsShopCtrl.keyBundles()
        bundlesModel = model.getBundles()
        bundlesModel.clear()
        processedGroups = []
        lackKeys = self.lsArtifactsCtrl.getLackOfKeysForArtefacts()
        hasShopBundle = False
        hasKeyBundle = False
        model.setSlide(self.lsArtifactsCtrl.getIndex(self.lsArtifactsCtrl.selectedArtefactID))
        for bundle in sorted(bundles, key=lambda bundle: (bundle.groupID, bundle.orderInGroup)):
            if bundle.isWebShopBundle:
                if bundle.limit is not None and self.lsShopCtrl.getPurchaseCount(bundle.bundleID) >= bundle.limit:
                    continue
            elif self.lsArtifactsCtrl.getLackOfKeysForArtefacts() == 0:
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
                elif bundle.limit is None:
                    keys = self.lsShopCtrl.getKeysInBundle(bundle.bundleID)
                    bundleModel.setKeysInBundle(keys)
                    bundleModel.price.setName(bundle.price.currency)
                    bundleModel.price.setValue(bundle.price.amount)
                else:
                    continue
                hasKeyBundle = True
            else:
                keys = self.lsShopCtrl.getKeysInBundle(bundle.bundleID)
                bundleModel.setKeysInBundle(keys)
                bundleModel.setMaximumBundleCount(keys)
                hasShopBundle = True
            processedGroups.append(bundle.groupID)
            sortedBonuses = sorted(bundle.bonuses, cmp=compareBonusesByPriority)
            formatter = LSBonusesAwardsComposer(MAX_BONUSES_IN_VIEW, getLSMetaAwardFormatter())
            bonusRewards = formatter.getFormattedBonuses(sortedBonuses, AWARDS_SIZES.BIG)
            rewards = bundleModel.getBonuses()
            rewards.clear()
            for bonus in bonusRewards:
                if bonus.bonusName in (KEY_TOKEN, ArtefactsSettings.KEY_NOTIFY_TOKEN):
                    continue
                tooltipId = '{}'.format(self.__idGen.next())
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

            bundlesModel.addViewModel(bundleModel)

        model.setTitleState(self.__getTitleState(hasShopBundle, hasKeyBundle))
        bundlesModel.invalidate()
        return

    def _onPurchaseBundle(self, args):
        bundleId = args.get('id', None)
        count = int(args.get('amount', 1))
        if bundleId is None:
            return
        elif count <= 0:
            return
        else:
            bundle = self.lsShopCtrl.getBundleByID(bundleId)
            if not bundle:
                return
            count = min(count, self.lsArtifactsCtrl.getLackOfKeysForArtefacts())
            if bundle.isWebShopBundle and bundle.url:
                showLSShopBundle(bundle.url)
                return
            elif not self.__isEnoughMoney(bundle, count=count):
                showBuyGoldForBundle(bundle.price.amount, {})
                return
            self.__processPurchase(bundleId, count)
            self._onClose()
            return

    def _getEvents(self):
        return [(self.viewModel.onClose, self._onClose),
         (self.viewModel.onPurchase, self._onPurchaseBundle),
         (self.lsShopCtrl.onBundlesUpdated, self.__onBundlesUpdated),
         (self.lsArtifactsCtrl.onArtefactKeyUpdated, self.__onArtefactKeyUpdated)]

    def __isEnoughMoney(self, bundle, count):
        return self._itemsCache.items.stats.mayConsumeWalletResources and self.__getMoney(bundle.price.currency) >= bundle.price.amount * count

    def __onArtefactKeyUpdated(self):
        self.__fillViewModel()

    def __getTitleState(self, hasShopBundle, hasKeyBundle):
        if hasShopBundle and not hasKeyBundle:
            return TitleStates.ONLYSHOPBUNDLE
        return TitleStates.ONLYKEYSBUNDLE if not hasShopBundle and hasKeyBundle else TitleStates.DEFAULT

    @adisp_process
    def __processPurchase(self, bundleID, count):
        yield self.lsShopCtrl.purchaseBundle(bundleID, count)

    def __onBundlesUpdated(self):
        self.__fillViewModel()

    def __getMoney(self, currency):
        return self._itemsCache.items.stats.money.get(currency, 0)


class BundleWindow(EventLobbyWindow):

    def __init__(self, layoutID, artefactID, parent=None):
        super(BundleWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=BundleView(layoutID=layoutID, artefactID=artefactID), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
