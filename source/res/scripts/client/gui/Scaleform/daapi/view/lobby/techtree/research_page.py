# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/research_page.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.go_back_helper import BackButtonContextKeys, getBackBtnLabel
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation, NODE_STATE
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.Scaleform.genConsts.RESEARCH_ALIASES import RESEARCH_ALIASES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.lobby.buy_vehicle_view import VehicleBuyActionTypes
from gui.ingame_shop import canBuyGoldForVehicleThroughWeb
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import event_dispatcher as shared_events
from gui.shared import events
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import getDueDateOrTimeStr, RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.money import Currency
from helpers import int2roman
from items import getTypeOfCompactDescr

class Research(ResearchMeta):

    def __init__(self, ctx=None, skipConfirm=False):
        super(Research, self).__init__(ResearchItemsData(dumpers.ResearchItemsObjDumper()))
        self._resolveLoadCtx(ctx=ctx)
        self._exitEvent = ctx.get(BackButtonContextKeys.EXIT, None)
        self._skipConfirm = skipConfirm
        return

    def __del__(self):
        LOG_DEBUG('ResearchPage deleted')

    def goToVehicleView(self, itemCD):
        vehicle = self._itemsCache.items.getItemByCD(int(itemCD))
        if vehicle:
            if vehicle.isPreviewAllowed():
                shared_events.showVehiclePreview(int(itemCD), self.alias)
            elif vehicle.isInInventory:
                shared_events.selectVehicleInHangar(itemCD)

    def requestResearchData(self):
        self.redraw()

    def goToNextVehicle(self, vehCD):
        self._data.setRootCD(vehCD)
        self.redraw()

    def redraw(self):
        self._data.load()
        self.as_setRootDataS(self._getRootData())
        self.as_setResearchItemsS(SelectedNation.getName(), self._data.dump())

    def request4Unlock(self, itemCD, topLevel):
        itemCD = int(itemCD)
        if topLevel:
            node = self._data.getTopLevelByItemCD(itemCD)
        else:
            node = self._data.getNodeByItemCD(itemCD)
        unlockProps = node.getUnlockProps() if node is not None else None
        if unlockProps is not None:
            ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, itemCD, unlockProps, skipConfirm=self._skipConfirm)
        return

    def request4Buy(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            vehicle = self._itemsCache.items.getItemByCD(itemCD)
            if canBuyGoldForVehicleThroughWeb(vehicle):
                shared_events.showVehicleBuyDialog(vehicle, actionType=VehicleBuyActionTypes.BUY)
            else:
                ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD, False, VehicleBuyActionTypes.BUY, skipConfirm=self._skipConfirm)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM, itemCD, self._data.getRootCD(), skipConfirm=self._skipConfirm)

    def request4Rent(self, itemCD):
        itemCD = int(itemCD)
        vehicle = self._itemsCache.items.getItemByCD(itemCD)
        if canBuyGoldForVehicleThroughWeb(vehicle):
            shared_events.showVehicleBuyDialog(vehicle, actionType=VehicleBuyActionTypes.RENT)
        else:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD, False, VehicleBuyActionTypes.RENT, skipConfirm=self._skipConfirm)

    def request4Restore(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD, False, VehicleBuyActionTypes.RESTORE, skipConfirm=self._skipConfirm)

    def exitFromResearch(self):
        if self._canBeClosed:
            self.fireEvent(events.LoadEvent(events.LoadEvent.EXIT_FROM_RESEARCH), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateVehCompare(self):
        super(Research, self).invalidateVehCompare()
        self.as_setRootDataS(self._getRootData())

    def invalidateUnlocks(self, unlocks):
        if self._data.isRedrawNodes(unlocks):
            self.redraw()
        else:
            super(Research, self).invalidateUnlocks(unlocks)

    def invalidateInventory(self, data):
        if self._data.isRedrawNodes(data):
            self.redraw()
        else:
            super(Research, self).invalidateInventory(data)
            result = self._data.invalidateInstalled()
            if result:
                self.as_setInstalledItemsS(result)

    def invalidatePrbState(self):
        self.redraw()
        super(Research, self).invalidatePrbState()

    def invalidateFreeXP(self):
        self.as_setFreeXPS(self._itemsCache.items.stats.actualFreeXP)
        super(Research, self).invalidateFreeXP()

    def invalidateRent(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def invalidateVehLocks(self, locks):
        if self._data.invalidateLocks(locks):
            self.redraw()

    def invalidateWalletStatus(self, status):
        self.invalidateFreeXP()
        self.as_setWalletStatusS(status)

    def invalidateRestore(self, vehicles):
        if self._data.getRootCD() in vehicles:
            self.redraw()

    def invalidateElites(self, elites):
        super(Research, self).invalidateElites(elites)
        if self._data.getRootCD() in elites:
            self.redraw()

    def invalidateBlueprintMode(self, _):
        if not self._itemsCache.items.blueprints.isBlueprintsAvailable():
            blueprintModeInTechtree = self._exitEvent.ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
            if blueprintModeInTechtree:
                self._exitEvent.ctx[BackButtonContextKeys.BLUEPRINT_MODE] = False
                self.as_setDataS(self.__getBackBtnData())
        self.redraw()

    def compareVehicle(self, itemCD):
        self._cmpBasket.addVehicle(int(itemCD))

    def _populate(self):
        super(Research, self)._populate()
        self.as_setDataS(self.__getViewLayoutData())
        self.as_setXpInfoLinkageS(self._getExperienceInfoLinkage())
        self.as_setWalletStatusS(self._wallet.componentsStatuses)
        self.as_setFreeXPS(self._itemsCache.items.stats.actualFreeXP)

    def _blueprintExitEvent(self, vehicleCD):
        return events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={BackButtonContextKeys.ROOT_CD: vehicleCD,
         BackButtonContextKeys.EXIT: self._exitEvent or events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)})

    def _resolveLoadCtx(self, ctx=None):
        exitEvent = ctx[BackButtonContextKeys.EXIT] if ctx is not None and BackButtonContextKeys.EXIT in ctx else None
        if exitEvent is not None:
            self._previewAlias = exitEvent.name
        else:
            self._previewAlias = VIEW_ALIAS.LOBBY_HANGAR
        rootCD = ctx[BackButtonContextKeys.ROOT_CD] if ctx is not None and BackButtonContextKeys.ROOT_CD in ctx else None
        if rootCD is None:
            if g_currentVehicle.isPresent():
                self._data.setRootCD(g_currentVehicle.item.intCD)
        else:
            self._data.setRootCD(rootCD)
        SelectedNation.select(self._data.getNationID())
        return

    def _getExperienceInfoLinkage(self):
        return RESEARCH_ALIASES.EXPERIENCE_INFO

    def _getRootData(self):
        root = self._data.getRootItem()
        rootNode = self._data.getRootNode()
        bpfProps = rootNode.getBpfProps()
        isNext2Unlock = NODE_STATE.isNext2Unlock(rootNode.getState())
        comparisonState, comparisonTooltip = resolveStateTooltip(self._cmpBasket, root, enabledTooltip='', fullTooltip=TOOLTIPS.RESEARCHPAGE_VEHICLE_BUTTON_COMPARE_DISABLED)
        tankTier = int2roman(root.level)
        result = {'tankTierStr': text_styles.grandTitle(tankTier),
         'tankNameStr': text_styles.grandTitle(root.userName),
         'tankTierStrSmall': text_styles.promoTitle(tankTier),
         'tankNameStrSmall': text_styles.promoTitle(root.userName),
         'typeIconPath': getTypeBigIconPath(root.type, root.isElite),
         'shopIconPath': RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_MEDIUM, root.name.split(':')[1]),
         'buttonLabel': self.__getMainButtonLabel(root, rootNode),
         'blueprintLabel': self.__getResearchPageBlueprintLabel(rootNode),
         'blueprintProgress': rootNode.getBlueprintProgress(),
         'blueprintCanConvert': bpfProps.canConvert if bpfProps is not None else False,
         'bpbGlowEnabled': isNext2Unlock,
         'itemPrices': rootNode.getItemPrices(),
         'compareBtnEnabled': comparisonState,
         'compareBtnLabel': backport.text(R.strings.menu.research.labels.button.addToCompare()),
         'compareBtnTooltip': comparisonTooltip,
         'previewBtnEnabled': root.isPreviewAllowed(),
         'previewBtnLabel': backport.text(R.strings.menu.research.labels.button.vehiclePreview()),
         'isElite': root.isElite,
         'statusStr': self.__getRootStatusStr(root),
         'discountStr': self.__getDiscountBannerStr(root, rootNode),
         'rentBtnLabel': self.__getRentButtonLabel(rootNode)}
        return result

    @staticmethod
    def __getRootStatusStr(root):
        status = ''
        if root.isRented and not root.rentalIsOver and not root.isTelecom and not root.isPremiumIGR:
            status = text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.ClockIcon_1()), width=38, height=38, vSpace=-14), RentLeftFormatter(root.rentInfo).getRentLeftStr(strForSpecialTimeFormat=backport.text(R.strings.menu.research.status.rentLeft())))
        elif root.canTradeIn:
            status = text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.trade_in()), width=36, height=36, vSpace=-13), backport.text(R.strings.menu.research.status.tradeIn()))
        return status

    def __getDiscountBannerStr(self, root, rootNode):
        htmlStr = ''
        nodeState = rootNode.getState()
        if NODE_STATE.isRestoreAvailable(nodeState):
            restoreDueDate = getDueDateOrTimeStr(rootNode.getRestoreFinishTime())
            if restoreDueDate:
                htmlStr = text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.menu.research.restore.commmonInfo())), text_styles.mainBig(backport.text(R.strings.menu.research.restore.dueDate(), date=restoreDueDate)))
        elif not root.isUnlocked:
            unlockDiscount = self._itemsCache.items.blueprints.getBlueprintDiscount(root.intCD, root.level)
            if unlockDiscount > 0:
                htmlStr = text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.blueprints.blueprintScreen.researchSale.label())), text_styles.grandTitle(''.join(('-', str(unlockDiscount), '%'))))
        elif root.isRented:
            discount = rootNode.getActionDiscount()
            if discount:
                htmlStr = text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.menu.research.premium.discount())), text_styles.grandTitle(''.join(('-', str(discount), '%'))))
        elif not NODE_STATE.inInventory(nodeState) and NODE_STATE.isActionVehicle(nodeState):
            actionDueDate = getDueDateOrTimeStr(rootNode.getActionFinishTime())
            if actionDueDate:
                htmlStr = text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.menu.barracks.notRecruitedActivateBefore(), date=actionDueDate)), text_styles.grandTitle(''.join(('-', str(rootNode.getActionDiscount()), '%'))))
        return htmlStr

    def __getViewLayoutData(self):
        root = self._data.getRootItem()
        result = self.__getBackBtnData()
        result['isPremiumLayout'] = root.isPremium
        if root.isPremium:
            benefitIconPattern = 'benefit%dIconSrc'
            benefitLabelPattern = 'benefit%dLabelStr'
            benefitData = [(RES_SHOP.MAPS_SHOP_KPI_STAR_ICON_BENEFITS, VEHICLE_PREVIEW.INFOPANEL_PREMIUM_FREEEXPMULTIPLIER, VEHICLE_PREVIEW.INFOPANEL_PREMIUM_FREEEXPTEXT)]
            if not root.isSpecial:
                benefitData.append((RES_SHOP.MAPS_SHOP_KPI_MONEY_BENEFITS, VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREDITSMULTIPLIER, VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREDITSTEXT))
            benefitData.append((RES_SHOP.MAPS_SHOP_KPI_CROW_BENEFITS, VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREWTRANSFERTITLE, VEHICLE_PREVIEW.INFOPANEL_PREMIUM_CREWTRANSFERTEXT))
            for i, (icon, title, body) in enumerate(benefitData, 1):
                result[benefitIconPattern % i] = icon
                result[benefitLabelPattern % i] = text_styles.concatStylesToMultiLine(text_styles.highTitle(title), text_styles.main(body))

        return result

    def __getBackBtnData(self):
        result = {'backBtnLabel': backport.text(R.strings.menu.viewHeader.backBtn.label()),
         'backBtnDescrLabel': getBackBtnLabel(self._exitEvent, self._previewAlias)}
        return result

    @staticmethod
    def __getMainButtonLabel(rootItem, rootNode):
        if not rootItem.isUnlocked:
            btnLabel = backport.text(R.strings.menu.unlocks.unlockButton())
        elif NODE_STATE.isRestoreAvailable(rootNode.getState()):
            btnLabel = backport.text(R.strings.menu.research.labels.button.restore())
        elif NODE_STATE.inInventory(rootNode.getState()) and not rootItem.isRented or rootItem.isHidden:
            btnLabel = backport.text(R.strings.menu.research.labels.button.showInHangar())
        elif NODE_STATE.canTradeIn(rootNode.getState()):
            btnLabel = text_styles.concatStylesWithSpace(icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.button_tradein())), backport.text(R.strings.menu.research.labels.button.buy()))
        else:
            btnLabel = backport.text(R.strings.menu.research.labels.button.buy())
        return btnLabel

    @staticmethod
    def __getRentButtonLabel(rootNode):
        btnLabel = ''
        if NODE_STATE.isRentAvailable(rootNode.getState()):
            minRentPrice, currency = rootNode.getRentInfo()
            if currency == Currency.CREDITS:
                btnLabel = text_styles.concatStylesWithSpace(backport.text(R.strings.menu.research.labels.button.rent()), text_styles.credits(BigWorld.wg_getIntegralFormat(minRentPrice.credits)), icons.credits())
            elif currency == Currency.GOLD:
                btnLabel = text_styles.concatStylesWithSpace(backport.text(R.strings.menu.research.labels.button.rent()), text_styles.gold(BigWorld.wg_getGoldFormat(minRentPrice.gold)), icons.gold())
        return btnLabel

    @staticmethod
    def __getResearchPageBlueprintLabel(rootNode):
        bpfProps = rootNode.getBpfProps()
        label = ''
        if bpfProps is not None:
            if bpfProps.filledCount != bpfProps.totalCount:
                label = text_styles.concatStylesWithSpace(text_styles.credits(str(bpfProps.filledCount)), text_styles.main(''.join(('/ ', str(bpfProps.totalCount)))))
                label = '    '.join((text_styles.credits(backport.text(R.strings.menu.research.labels.blueprint())), label))
            else:
                label = text_styles.concatStylesWithSpace(icons.makeImageTag(backport.image(R.images.gui.maps.icons.blueprints.blueCheck()), width=16, height=16, vSpace=-1), text_styles.credits(backport.text(R.strings.menu.research.labels.blueprintComplete())))
        return label
