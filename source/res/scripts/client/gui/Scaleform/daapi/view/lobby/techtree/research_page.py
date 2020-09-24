# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/research_page.py
from logging import getLogger
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.go_back_helper import BackButtonContextKeys, getBackBtnLabel
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation, NODE_STATE
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import resolveStateTooltip
from gui.Scaleform.daapi.view.meta.ResearchMeta import ResearchMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.RESEARCH_ALIASES import RESEARCH_ALIASES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.lobby.buy_vehicle_view import VehicleBuyActionTypes
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import event_dispatcher as shared_events
from gui.shared import events
from gui.shared.events import LoadViewEvent
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import getDueDateOrTimeStr, RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeBigIconPath
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.money import Currency
from gui.shared.utils.functions import makeTooltip
from gui.shop import canBuyGoldForVehicleThroughWeb
from helpers import int2roman, dependency
from helpers.i18n import makeString as _ms
from items import getTypeOfCompactDescr
from nation_change.nation_change_helpers import iterVehTypeCDsInNationGroup
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.game_control import ITradeInController
from skeletons.gui.shared import IItemsCache
_logger = getLogger(__name__)
_BENEFIT_ITEMS_LIMIT = 3

class _VehicleState(object):
    CAN_UNLOCK = 0
    CAN_BUY = 1
    CAN_RENT = 2
    CAN_RESTORE = 3


def _getPremiumBaseBenefit(benefits, root, _=None):
    if not root.isEpicActionVehicle:
        benefits.append((backport.image(R.images.gui.maps.shop.kpi.star_icon_benefits()), backport.text(R.strings.vehicle_preview.infoPanel.premium.freeExpMultiplier()), backport.text(R.strings.vehicle_preview.infoPanel.premium.freeExpText())))


def _getMoneyBenefits(benefits, root, _=None):
    if not (root.isSpecial or root.isEpicActionVehicle):
        benefits.append((backport.image(R.images.gui.maps.shop.kpi.money_benefits()), backport.text(R.strings.vehicle_preview.infoPanel.premium.creditsMultiplier()), backport.text(R.strings.vehicle_preview.infoPanel.premium.creditsText())))


def _getCrewBenefits(benefits, root, _=None):
    if not root.isCrewLocked:
        benefits.append((backport.image(R.images.gui.maps.shop.kpi.crow_benefits()), backport.text(R.strings.vehicle_preview.infoPanel.premium.crewTransferTitle()), backport.text(R.strings.vehicle_preview.infoPanel.premium.crewTransferText())))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getEquipmentBenefits(benefits, root, itemsCache=None):
    builtInEquipmentIDs = root.getBuiltInEquipmentIDs()
    builtInCount = len(builtInEquipmentIDs) if builtInEquipmentIDs else 0
    if builtInCount > 0:
        if builtInCount == 1:
            equipment = itemsCache.items.getItemByCD(builtInEquipmentIDs[0])
            mainText = equipment.userName
        else:
            mainText = backport.text(R.strings.vehicle_preview.infoPanel.premium.builtInEqupmentText(), value=builtInCount)
        benefits.append((backport.image(R.images.gui.maps.shop.kpi.infinity_benefits()), text_styles.concatStylesToMultiLine(text_styles.highTitle(backport.text(R.strings.vehicle_preview.infoPanel.premium.builtInEqupmentTitle()))), text_styles.main(mainText)))


def _formatBenefits(benefitData):
    formattedBenefits = []
    for i, (icon, title, body) in enumerate(benefitData, 1):
        if i > _BENEFIT_ITEMS_LIMIT:
            break
        formattedBenefits.append({'iconSrc': icon,
         'labelStr': text_styles.concatStylesToMultiLine(text_styles.highTitle(title), text_styles.main(body))})

    return formattedBenefits


def _getRestoreBannerStr(param):
    return text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.menu.research.restore.commmonInfo())), text_styles.mainBig(backport.text(R.strings.menu.research.restore.dueDate(), date=param)))


def _getUnlockedBannerStr(param):
    return text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.blueprints.blueprintScreen.researchSale.label())), text_styles.grandTitle(''.join(('-', str(param), '%'))))


def _getRentBannerStr(param):
    return text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.menu.research.premium.discount())), text_styles.grandTitle(''.join(('-', str(param), '%'))))


def _getActionBannerStr(paramDate, paramDiscount):
    return text_styles.concatStylesToMultiLine(text_styles.mainBig(backport.text(R.strings.menu.barracks.notRecruitedActivateBefore(), date=paramDate)), text_styles.grandTitle(''.join(('-', str(paramDiscount), '%'))))


_BENEFIT_GETTERS = (_getPremiumBaseBenefit,
 _getMoneyBenefits,
 _getCrewBenefits,
 _getEquipmentBenefits)

class States(object):
    RESTORE = 'restore'
    UNLOCKED = 'unlocked'
    RENT = 'rent'
    ACTION = 'action'


_BANNER_GETTERS = {States.RESTORE: _getRestoreBannerStr,
 States.UNLOCKED: _getUnlockedBannerStr,
 States.RENT: _getRentBannerStr,
 States.ACTION: _getActionBannerStr}

class Research(ResearchMeta):
    __tradeIn = dependency.descriptor(ITradeInController)
    __bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, ctx=None, skipConfirm=False):
        super(Research, self).__init__(ResearchItemsData(dumpers.ResearchItemsObjDumper()))
        self._resolveLoadCtx(ctx=ctx)
        self._exitEvent = ctx.get(BackButtonContextKeys.EXIT, None)
        self._skipConfirm = skipConfirm
        return

    def __del__(self):
        _logger.debug('ResearchPage deleted')

    def goToVehicleView(self, itemCD):
        vehicle = self._itemsCache.items.getItemByCD(int(itemCD))
        if vehicle:
            if vehicle.isPreviewAllowed():
                shared_events.showVehiclePreview(int(itemCD), self.alias)
            elif vehicle.isInInventory:
                if not vehicle.activeInNationGroup:
                    itemCD = iterVehTypeCDsInNationGroup(vehicle.intCD).next()
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
            self._doUnlockItemAction(itemCD, unlockProps)
        return

    def _doUnlockItemAction(self, itemCD, unlockProps):
        ItemsActionsFactory.doAction(ItemsActionsFactory.UNLOCK_ITEM, itemCD, unlockProps, skipConfirm=self._skipConfirm)

    def request4Buy(self, itemCD):
        itemCD = int(itemCD)
        if getTypeOfCompactDescr(itemCD) == GUI_ITEM_TYPE.VEHICLE:
            vehicle = self._itemsCache.items.getItemByCD(itemCD)
            if canBuyGoldForVehicleThroughWeb(vehicle):
                shared_events.showVehicleBuyDialog(vehicle, actionType=VehicleBuyActionTypes.BUY)
            else:
                self._doBuyVehicleAction(itemCD)
        else:
            self._doBuyAndInstallItemAction(itemCD)

    def _doBuyAndInstallItemAction(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_AND_INSTALL_ITEM, itemCD, self._data.getRootCD(), skipConfirm=self._skipConfirm)

    def _doBuyVehicleAction(self, itemCD):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, itemCD, False, VehicleBuyActionTypes.BUY, skipConfirm=self._skipConfirm)

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
            self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EXIT_FROM_RESEARCH)), scope=EVENT_BUS_SCOPE.LOBBY)

    def invalidateVehCompare(self):
        super(Research, self).invalidateVehCompare()
        self.as_setRootDataS(self._getRootData())

    def invalidateUnlocks(self, unlocks):
        if self._data.isRedrawNodes(unlocks):
            self.redraw()
        else:
            super(Research, self).invalidateUnlocks(unlocks)

    def invalidateInventory(self, data):
        if not self._data.getRootItem().activeInNationGroup:
            self.__redrawPageAfterNationWasChanged()
            return
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

    def invalidateBlueprints(self, blueprints):
        if blueprints:
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
        rootNode = self._data.getRootNode()
        if rootNode.getBpfProps() is None:
            return
        else:
            if not self._itemsCache.items.blueprints.isBlueprintsAvailable():
                blueprintModeInTechtree = self._exitEvent.ctx.get(BackButtonContextKeys.BLUEPRINT_MODE, False)
                if blueprintModeInTechtree:
                    self._exitEvent.ctx[BackButtonContextKeys.BLUEPRINT_MODE] = False
                    self.as_setDataS(self.__getBackBtnData())
            self.redraw()
            return

    def invalidateVehicleCollectorState(self):
        rootNode = self._data.getRootNode()
        if not NODE_STATE.isCollectible(rootNode.getState()):
            return
        super(Research, self).invalidateVehicleCollectorState()

    def compareVehicle(self, itemCD):
        self._cmpBasket.addVehicle(int(itemCD))

    def _populate(self):
        super(Research, self)._populate()
        self.as_setDataS(self.__getViewLayoutData())
        self.as_setXpInfoLinkageS(self._getExperienceInfoLinkage())
        self.as_setWalletStatusS(self._wallet.componentsStatuses)
        self.as_setFreeXPS(self._itemsCache.items.stats.actualFreeXP)
        self.addListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)

    def _dispose(self):
        self.removeListener(events.VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged)
        super(Research, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == VEHPREVIEW_CONSTANTS.TRADE_OFF_WIDGET_ALIAS:
            viewPy.setTradeInVehicle(self._data.getRootItem())

    def _blueprintExitEvent(self, vehicleCD):
        return events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_RESEARCH), ctx={BackButtonContextKeys.ROOT_CD: vehicleCD,
         BackButtonContextKeys.EXIT: self._exitEvent or events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR))})

    def _resolveLoadCtx(self, ctx=None):
        exitEvent = ctx[BackButtonContextKeys.EXIT] if ctx is not None and BackButtonContextKeys.EXIT in ctx else None
        self._previewAlias = exitEvent.name if exitEvent is not None else VIEW_ALIAS.LOBBY_HANGAR
        rootCD = ctx[BackButtonContextKeys.ROOT_CD] if ctx is not None and BackButtonContextKeys.ROOT_CD in ctx else None
        if rootCD is None and g_currentVehicle.isPresent():
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
        tankHasNationGroup = (root.isInInventory or root.isRented) and root.hasNationGroup
        isNationChangeAvailable = root.isNationChangeAvailable
        isShownNationChangeTooltip = tankHasNationGroup and not isNationChangeAvailable
        result = {'tankTierStr': text_styles.grandTitle(tankTier),
         'tankNameStr': text_styles.grandTitle(root.userName),
         'tankTierStrSmall': text_styles.promoTitle(tankTier),
         'tankNameStrSmall': text_styles.promoTitle(root.userName),
         'typeIconPath': getTypeBigIconPath(root.type, root.isElite),
         'shopIconPath': RES_SHOP.getVehicleIcon(STORE_CONSTANTS.ICON_SIZE_MEDIUM, root.name.split(':')[1]),
         'isInteractive': self.__getIsInteractive(root, rootNode),
         'buttonLabel': self.__getMainButtonLabel(root, rootNode),
         'blueprintLabel': self.__getResearchPageBlueprintLabel(rootNode),
         'blueprintProgress': rootNode.getBlueprintProgress(),
         'blueprintCanConvert': bpfProps.canConvert if bpfProps is not None else False,
         'bpbGlowEnabled': isNext2Unlock,
         'itemPrices': rootNode.getItemPrices(),
         'compareBtnVisible': not self.__bootcamp.isInBootcamp(),
         'compareBtnEnabled': comparisonState,
         'compareBtnLabel': backport.text(R.strings.menu.research.labels.button.addToCompare()),
         'compareBtnTooltip': comparisonTooltip,
         'previewBtnEnabled': root.isPreviewAllowed(),
         'previewBtnLabel': backport.text(R.strings.menu.research.labels.button.vehiclePreview()),
         'isElite': root.isElite,
         'statusStr': self.__getRootStatusStr(root),
         'discountStr': self.__getDiscountBannerStr(root, rootNode),
         'rentBtnLabel': self.__getRentButtonLabel(rootNode),
         'changeNationBtnVisibility': tankHasNationGroup,
         'isTankNationChangeAvailable': isNationChangeAvailable,
         'nationChangeIsNew': not AccountSettings.getSettings(NATION_CHANGE_VIEWED),
         'nationChangeTooltip': self.__getNationChangeTooltip(root) if isShownNationChangeTooltip else ''}
        return result

    def __getIsInteractive(self, root, rootNode):
        return self.__tradeIn.getActiveTradeOffVehicle() is None or self.__tradeIn.tradeOffSelectedApplicableForLevel(root.level) if NODE_STATE.canTradeIn(rootNode.getState()) else True

    def __getDiscountBannerStr(self, root, rootNode):
        htmlStr = ''
        nodeState = rootNode.getState()
        if NODE_STATE.canTradeIn(nodeState) and self.__tradeIn.tradeOffSelectedApplicableForLevel(root.level):
            return htmlStr
        if NODE_STATE.isRestoreAvailable(nodeState):
            restoreDueDate = getDueDateOrTimeStr(rootNode.getRestoreFinishTime())
            if restoreDueDate:
                return _BANNER_GETTERS[States.RESTORE](restoreDueDate)
        if not root.isUnlocked and not root.isCollectible:
            unlockDiscount = self._itemsCache.items.blueprints.getBlueprintDiscount(root.intCD, root.level)
            if unlockDiscount > 0:
                return _BANNER_GETTERS[States.UNLOCKED](unlockDiscount)
        if root.isRented:
            discount = rootNode.getActionDiscount()
            if discount != 0:
                return _BANNER_GETTERS[States.RENT](discount)
        if not NODE_STATE.inInventory(nodeState) and NODE_STATE.isActionVehicle(nodeState) or NODE_STATE.isCollectibleActionVehicle(nodeState):
            actionDueDate = getDueDateOrTimeStr(rootNode.getActionFinishTime())
            if actionDueDate:
                return _BANNER_GETTERS[States.ACTION](actionDueDate, rootNode.getActionDiscount())
        return htmlStr

    def __getViewLayoutData(self):
        root = self._data.getRootItem()
        result = self.__getBackBtnData()
        result['isPremiumLayout'] = root.isPremium
        if root.isPremium:
            benefitData = []
            for benefitGetter in _BENEFIT_GETTERS:
                benefitGetter(benefitData, root)

            result['benefitsData'] = _formatBenefits(benefitData)
        return result

    def __getBackBtnData(self):
        result = {'backBtnLabel': backport.text(R.strings.menu.viewHeader.backBtn.label()),
         'backBtnDescrLabel': getBackBtnLabel(self._exitEvent, self._previewAlias)}
        return result

    def __redrawPageAfterNationWasChanged(self):
        targetVehicleCD = iterVehTypeCDsInNationGroup(self._data.getRootCD()).next()
        self._data.setRootCD(targetVehicleCD)
        SelectedNation.select(self._data.getNationID())
        self.redraw()

    def __getMainButtonLabel(self, rootItem, rootNode):
        if NODE_STATE.isCollectible(rootNode.getState()):
            btnLabel = R.strings.menu.research.labels.button.toCollection()
        elif not rootItem.isUnlocked:
            btnLabel = R.strings.menu.unlocks.unlockButton()
        elif NODE_STATE.isRestoreAvailable(rootNode.getState()):
            btnLabel = R.strings.menu.research.labels.button.restore()
        elif NODE_STATE.inInventory(rootNode.getState()) and not rootItem.isRented or rootItem.isHidden:
            btnLabel = R.strings.menu.research.labels.button.showInHangar()
        elif NODE_STATE.canTradeIn(rootNode.getState()) and self.__tradeIn.getActiveTradeOffVehicle() is not None:
            btnLabel = R.strings.menu.research.labels.button.trade_in()
        else:
            btnLabel = R.strings.menu.research.labels.button.buy()
        return backport.text(btnLabel)

    def __onTradeOffSelectedChanged(self, _=None):
        self.redraw()

    @staticmethod
    def __getRootStatusStr(root):
        return text_styles.concatStylesToSingleLine(icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.ClockIcon_1()), width=38, height=38, vSpace=-14), RentLeftFormatter(root.rentInfo).getRentLeftStr(strForSpecialTimeFormat=backport.text(R.strings.menu.research.status.rentLeft()))) if root.isRented and not root.rentalIsOver and not root.isTelecom and not root.isPremiumIGR else ''

    @staticmethod
    def __getNationChangeTooltip(root):
        if root.isBroken:
            body = TOOLTIPS.HANGAR_NATIONCHANGE_DISABLED_BODY_DESTROYED
        elif root.isInBattle:
            body = TOOLTIPS.HANGAR_NATIONCHANGE_DISABLED_BODY_INBATTLE
        elif root.isInUnit:
            body = TOOLTIPS.HANGAR_NATIONCHANGE_DISABLED_BODY_INSQUAD
        else:
            body = ''
        return makeTooltip(_ms(TOOLTIPS.HANGAR_NATIONCHANGE_DISABLED_HEADER), body)

    @staticmethod
    def __getRentButtonLabel(rootNode):
        btnLabel = ''
        if NODE_STATE.isRentAvailable(rootNode.getState()):
            minRentPrice, currency = rootNode.getRentInfo()
            if currency == Currency.CREDITS:
                btnLabel = text_styles.concatStylesWithSpace(backport.text(R.strings.menu.research.labels.button.rent()), text_styles.credits(backport.getIntegralFormat(minRentPrice.credits)), icons.credits())
            elif currency == Currency.GOLD:
                btnLabel = text_styles.concatStylesWithSpace(backport.text(R.strings.menu.research.labels.button.rent()), text_styles.gold(backport.getGoldFormat(minRentPrice.gold)), icons.gold())
        return btnLabel

    @staticmethod
    def __getResearchPageBlueprintLabel(rootNode):
        bpfProps = rootNode.getBpfProps()
        label = ''
        if bpfProps is not None:
            if bpfProps.filledCount != bpfProps.totalCount:
                values = text_styles.main(backport.text(R.strings.blueprints.blueprintProgressBar.inProgress.values()).format(current=text_styles.credits(str(bpfProps.filledCount)), total=str(bpfProps.totalCount)))
                label = text_styles.credits(backport.text(R.strings.blueprints.blueprintProgressBar.inProgress()).format(values=values))
            else:
                label = text_styles.concatStylesWithSpace(icons.makeImageTag(backport.image(R.images.gui.maps.icons.blueprints.blueCheck()), width=16, height=16, vSpace=-1), text_styles.credits(backport.text(R.strings.blueprints.blueprintProgressBar.complete())))
        return label
