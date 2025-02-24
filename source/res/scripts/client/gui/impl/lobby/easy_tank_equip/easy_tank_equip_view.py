# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/easy_tank_equip/easy_tank_equip_view.py
from BWUtil import AsyncReturn
import logging
import weakref
from collections import OrderedDict
from typing import TYPE_CHECKING, NamedTuple, Type
import BigWorld
from CurrentVehicle import g_currentVehicle
from adisp import adisp_async, adisp_process
from frameworks.wulf import ViewFlags, ViewSettings
from gui.SystemMessages import pushMessagesFromResult
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.common.proposal_model import ProposalType, ProposalModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.easy_tank_equip_view_model import EasyTankEquipViewModel
from gui.impl.gen.view_models.views.lobby.easy_tank_equip.tooltip_constants import TooltipConstants
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.easy_tank_equip.cards.base_card import BaseCard
from gui.impl.lobby.easy_tank_equip.cards.consumables_card import ConsumablesCard
from gui.impl.lobby.easy_tank_equip.cards.crew_card import CrewCard
from gui.impl.lobby.easy_tank_equip.cards.opt_devices_card import OptDevicesCard
from gui.impl.lobby.easy_tank_equip.cards.shells_card import ShellsCard
from gui.impl.lobby.easy_tank_equip.cards.styles_card import StylesCard
from gui.impl.lobby.easy_tank_equip.data_providers.consumables_data_provider import ConsumablesDataProvider
from gui.impl.lobby.easy_tank_equip.data_providers.crew_data_provider import CrewDataProvider
from gui.impl.lobby.easy_tank_equip.data_providers.opt_devices_data_provider import OptDevicesDataProvider
from gui.impl.lobby.easy_tank_equip.data_providers.shells_data_provider import ShellsDataProvider
from gui.impl.lobby.easy_tank_equip.data_providers.styles_data_provider import StylesDataProvider
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_deal_panel import EasyTankEquipBottomContent
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_vehicle import g_easyTankEquipCopyVehicle
from gui.impl.lobby.hangar.sub_views.vehicle_params_view import EasyTankEquipVehicleParamsView
from gui.impl.pub import ViewImpl
from gui.sounds.filters import States, StatesGroup
from gui.shared import event_dispatcher as shared_events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.close_confiramtor_helper import CloseConfirmatorsHelper
from gui.shared.event_dispatcher import animateHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items.processors.vehicle import EasyTankEquipApplyProcessor
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Currency, ZERO_MONEY
from gui.shared.tooltips.contexts import EasyTankEquipParamContext
from gui.shared.utils import decorators
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from sound_gui_manager import CommonSoundSpaceSettings
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEasyTankEquipController
from skeletons.gui.shared import IItemsCache
from uilogging.easy_tank_equip.loggers import EasyTankEquipLogger, LOGGING_ITEMS_MAP
from wg_async import wg_async, wg_await, await_callback
if TYPE_CHECKING:
    from frameworks.wulf.view.submodel_presenter import SubModelPresenter
    from gui.impl.lobby.easy_tank_equip.data_providers.base_data_provider import BaseDataProvider
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import List, Optional
_logger = logging.getLogger(__name__)
PROVIDERS_PRIORITIES_MAP = OrderedDict(((ProposalType.CREW, CrewDataProvider),
 (ProposalType.SHELLS, ShellsDataProvider),
 (ProposalType.CONSUMABLES, ConsumablesDataProvider),
 (ProposalType.OPT_DEVICES, OptDevicesDataProvider),
 (ProposalType.STYLES, StylesDataProvider)))
GUI_ITEM_TYPE_TO_PROPOSAL_MAP = {GUI_ITEM_TYPE.EQUIPMENT: ProposalType.CONSUMABLES,
 GUI_ITEM_TYPE.SHELL: ProposalType.SHELLS,
 GUI_ITEM_TYPE.OPTIONALDEVICE: ProposalType.OPT_DEVICES}
CardInfo = NamedTuple('CardInfo', [('card', Type[BaseCard]), ('model', ProposalModel)])

class _EasyTankEquipCloseConfirmatorsHelper(CloseConfirmatorsHelper):

    def start(self, closeConfirmator):
        super(_EasyTankEquipCloseConfirmatorsHelper, self).start(closeConfirmator)
        self._addPlatoonCreationConfirmator()

    def stop(self):
        self._deletePlatoonCreationConfirmator()
        super(_EasyTankEquipCloseConfirmatorsHelper, self).stop()


class EasyTankEquipView(ViewImpl):
    __appLoader = dependency.descriptor(IAppLoader)
    __easyTankEquipCtrl = dependency.descriptor(IEasyTankEquipController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='easy_tank_equip', entranceStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_ON}, exitStates={StatesGroup.OVERLAY_HANGAR_GENERAL: States.OVERLAY_HANGAR_GENERAL_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='', parentSpace='')

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID, flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=EasyTankEquipViewModel(), args=args, kwargs=kwargs)
        super(EasyTankEquipView, self).__init__(settings)
        self.__blur = CachedBlur()
        self.__closeConfirmatorHelper = _EasyTankEquipCloseConfirmatorsHelper()
        self.__bottomContent = None
        self.__vehicleParamsView = None
        self.__cards = []
        self.__providers = OrderedDict()
        self.__isApplyInProcess = False
        self.__uiLogger = EasyTankEquipLogger()
        return

    @property
    def viewModel(self):
        return super(EasyTankEquipView, self).getViewModel()

    @property
    def copyVehicle(self):
        if not g_easyTankEquipCopyVehicle.isPresent() and g_currentVehicle.isPresent():
            g_easyTankEquipCopyVehicle.setVehicle(self.__itemsCache.items.getVehicleCopy(g_currentVehicle.item))
        return g_easyTankEquipCopyVehicle.item

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            targetId = event.getArgument('targetId')
            if tooltipId == TooltipConstants.PRICE_DISCOUNT:
                specialArgs = (event.getArgument('price'), event.getArgument('defPrice'), event.getArgument('currencyType'))
                if all(specialArgs):
                    return self.__createSpecialTooltip(tooltipId, specialArgs)
            elif tooltipId == TooltipConstants.TANKMAN:
                if targetId is not None:
                    toolTipMgr = self.__appLoader.getApp().getToolTipMgr()
                    toolTipMgr.onCreateWulfTooltip(tooltipId, [targetId], event.mouse.positionX, event.mouse.positionY, parent=self.getParentWindow())
                    return tooltipId
            elif tooltipId in (TooltipConstants.HANGAR_MODULE, TooltipConstants.TECH_MAIN_SHELL):
                slotId = event.getArgument('slotId')
                if None not in [targetId, slotId]:
                    historicalBattleID = -1
                    specialArgs = (targetId,
                     slotId,
                     historicalBattleID,
                     self.copyVehicle)
                    return self.__createSpecialTooltip(tooltipId, specialArgs)
        return super(EasyTankEquipView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(EasyTankEquipView, self)._onLoading()
        if self.copyVehicle:
            self.__initializeProviders()
            self.__initializeCards()
            fillVehicleInfo(self.viewModel.vehicleInfo, self.copyVehicle)
            self.__initializeBottomContent()
            self._setTTC()
            self.__uiLogger.onViewOpen(self.__getCardsLogInfo())

    def __getCardsLogInfo(self):
        info = {}
        for proposalType, provider in self.__providers.items():
            info[LOGGING_ITEMS_MAP[proposalType].value] = self.__uiLogger.createCardInfo(status=provider.getCardLogStatus().value, presetNumber=provider.currentPresetIndex + 1, ids=provider.getCurrentPresetItemsIds())

        return info

    def _initialize(self, *args, **kwargs):
        super(EasyTankEquipView, self)._initialize()
        self.__closeConfirmatorHelper.start(self.__closeConfirmator)

    def _finalize(self):
        self.__closeConfirmatorHelper.stop()
        self.__clear()
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': False,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        super(EasyTankEquipView, self)._finalize()

    def _getEvents(self):
        return super(EasyTankEquipView, self)._getEvents() + ((self.__easyTankEquipCtrl.onUpdated, self.__onSettingsChange),
         (self.__itemsCache.onSyncCompleted, self.__onItemsCacheSyncCompleted),
         (self.viewModel.onEnableBlur, self.__onEnableBlur),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onSelectProposal, self.__onSelectProposal),
         (self.viewModel.onSwitchPreset, self.__onSwitchPreset),
         (self.viewModel.onSwapSlots, self.__onSwapSlots),
         (self.viewModel.dealPanel.onDealConfirmed, self.__onDealPanelConfirmed),
         (self.viewModel.dealPanel.onDealCancelled, self.__onDealPanelCancelled))

    def _getCallbacks(self):
        currencies = [Currency.CREDITS,
         Currency.GOLD,
         Currency.CRYSTAL,
         Currency.EQUIP_COIN]
        moneyCallbacks = tuple((('stats.{}'.format(c), self.__onMoneyUpdated) for c in currencies))
        return super(EasyTankEquipView, self)._getCallbacks() + moneyCallbacks + (('inventory', self.__onInventoryUpdate),)

    def _setTTC(self):
        currentVehicle = g_currentVehicle.item
        self.__vehicleParamsView = EasyTankEquipVehicleParamsView(currentVehicle, self.copyVehicle)
        self.__vehicleParamsView.setContext(EasyTankEquipParamContext())
        self.setChildView(R.views.lobby.hangar.subViews.VehicleParams(), self.__vehicleParamsView)

    def __createSpecialTooltip(self, tooltipId, specialArgs):
        tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs)
        window = BackportTooltipWindow(tooltipData, self.getParentWindow())
        if window is not None:
            window.load()
        return window

    def __initializeProviders(self):
        balance = self.__itemsCache.items.stats.money
        notSelectedCards = []
        for cardType, providerClass in PROVIDERS_PRIORITIES_MAP.items():
            provider = providerClass(self.copyVehicle, balance)
            provider.initialize()
            self.__providers[cardType] = provider
            balance = provider.getBalanceRemains()
            if not provider.isProposalSelected:
                notSelectedCards.append(provider)

        for provider in notSelectedCards:
            provider.updateBalance(balance)

    def __initializeCards(self):
        cardsLoadingMap = {ProposalType.CREW: CardInfo(CrewCard, self.viewModel.crewProposal),
         ProposalType.SHELLS: CardInfo(ShellsCard, self.viewModel.shellsProposal),
         ProposalType.CONSUMABLES: CardInfo(ConsumablesCard, self.viewModel.consumablesProposal),
         ProposalType.OPT_DEVICES: CardInfo(OptDevicesCard, self.viewModel.optDevicesProposal),
         ProposalType.STYLES: CardInfo(StylesCard, self.viewModel.styleProposal)}
        for cardType, cardInfo in cardsLoadingMap.items():
            card = cardInfo.card(cardInfo.model, weakref.proxy(self), self.__providers[cardType])
            card.initialize()
            self.__cards.append(card)

    def __initializeBottomContent(self):
        self.__bottomContent = EasyTankEquipBottomContent(viewModel=self.viewModel.dealPanel, parentView=self.viewModel, providers=self.__providers)
        self.__bottomContent.initialize()

    def __finalizeCards(self):
        for card in self.__cards:
            card.finalize()

        self.__cards = []

    def __finalizeProviders(self):
        for provider in self.__providers.values():
            provider.finalize()

        self.__providers.clear()

    def __finalizeBottomContent(self):
        if self.__bottomContent is not None:
            self.__bottomContent.finalize()
        return

    def __onSettingsChange(self):
        if not self.__easyTankEquipCtrl.config.enabled:
            self.__onClose()

    def __onItemsCacheSyncCompleted(self, reason, diff):
        if self.__isApplyInProcess:
            return
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            for provider in self.__providers.values():
                provider.updatePresets(fullUpdate=True)

            self.__update()

    def __onEnableBlur(self):
        if self.__blur is not None:
            self.__blur.enable()
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, ctx={'isDisable': True,
         'setIdle': True,
         'setParallax': True}), EVENT_BUS_SCOPE.LOBBY)
        return

    def __onMoneyUpdated(self, _):
        isDisableReasonChanged = False
        for provider in self.__providers.values():
            if provider.isCurrentPresetDisableReasonChanged():
                isDisableReasonChanged = True

        if isDisableReasonChanged:
            self.__update()
        else:
            self.__updateCardsBalances()
            self.__updateDealPanelPrices()

    def __updateCardsBalances(self):
        balance = self.__itemsCache.items.stats.money
        notSelectedCards = []
        balanceSelected = sum([ provider.getPresetPrice() for provider in self.__providers.values() if provider.isProposalSelected ], ZERO_MONEY)
        balanceRemains = balance - balanceSelected
        for provider in self.__providers.values():
            if provider.isProposalSelected:
                provider.updateBalance((balanceRemains + provider.getPresetPrice()).toNonNegative())
            notSelectedCards.append(provider)

        for provider in notSelectedCards:
            provider.updateBalance(balanceRemains.toNonNegative())

    def __updateDealPanelPrices(self):
        self.__bottomContent.updatePrices()

    def __updateTTC(self):
        self.__vehicleParamsView.update()

    def __onClose(self, isApplyBtnClicked=False):
        if self.__isApplyInProcess:
            return
        self.__uiLogger.onViewClose(isApplyBtnClicked, self.__getCardsLogInfo())
        animateHangar(True)
        self.destroyWindow()

    def __clear(self):
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        self.__finalizeBottomContent()
        self.__finalizeCards()
        self.__finalizeProviders()
        self.__vehicleParamsView = None
        self.__closeConfirmatorHelper = None
        self.__uiLogger = None
        g_easyTankEquipCopyVehicle.clear()
        return

    @args2params(ProposalType)
    def __onSelectProposal(self, proposalType):
        provider = self.__providers.get(proposalType)
        if not provider:
            _logger.warning('The provider for the card was not found when selecting card. ProposalType: %s.', proposalType)
            return
        if provider.isProposalDisabled() or provider.isCurrentPresetDisabled():
            _logger.warning('The disabled card can not be selected. ProposalType: %s.', proposalType)
            return
        provider.selectProposal()
        self.__update()

    @args2params(ProposalType, int)
    def __onSwitchPreset(self, proposalType, presetIndex):
        provider = self.__providers.get(proposalType)
        if not provider:
            _logger.warning('The provider for the card was not found when switching preset. ProposalType: %s.', proposalType)
            return
        self.__uiLogger.onSwitchPreset(proposalType, provider.currentPresetIndex + 1, presetIndex + 1)
        provider.switchPreset(presetIndex)
        self.__update()

    @args2params(ProposalType, int, int, bool)
    def __onSwapSlots(self, proposalType, firstSlot, secondSlot, isDndUsed):
        provider = self.__providers.get(proposalType)
        if provider:
            provider.swapSlots(firstSlot, secondSlot)
            if proposalType == ProposalType.OPT_DEVICES:
                self.__updateTTC()
            self.__uiLogger.onSwapSlots(proposalType, isDndUsed, firstSlot + 1, secondSlot + 1)

    @wg_async
    def __onDealPanelConfirmed(self):
        price = self.__bottomContent.getTotalPrice()
        balance = self.__itemsCache.items.stats.money
        if price.credits > 0 and balance.credits < price.credits:
            result = yield wg_await(shared_events.showExchangeToApplyEasyTankEquipDialog(price=price, availableGoldAmount=max(balance.gold - price.gold, 0), parent=self.getParentWindow()))
            if result is None or result.busy or not result.result:
                return
        yield await_callback(self.__apply)()
        self.__isApplyInProcess = False
        self.__onClose(isApplyBtnClicked=True)
        return

    def __onDealPanelCancelled(self):
        for provider in self.__providers.values():
            if provider.isProposalSelected:
                provider.selectProposal()

        self.__update()
        self.__uiLogger.onCancel()

    def __update(self):
        self.__updateCardsBalances()
        self.__bottomContent.update()
        self.__updateTTC()

    def __onInventoryUpdate(self, diff):
        if self.__isApplyInProcess:
            return
        isUpdateNeeded = False
        for guiItemType, proposalType in GUI_ITEM_TYPE_TO_PROPOSAL_MAP.items():
            if guiItemType in diff:
                provider = self.__providers.get(proposalType)
                if not provider:
                    _logger.warning('The provider for the card was not found when updating inventory. ProposalType: %s.', proposalType)
                    continue
                provider.updatePresets()
                isUpdateNeeded = True

        if isUpdateNeeded:
            self.__update()

    @decorators.adisp_process('easyTankEquipApply')
    def __apply(self, callback):
        self.__isApplyInProcess = True
        self.__saveAccountSettings()
        result = None
        data = self.__getPresetsDataForApplying()
        if data:
            result = yield self.__applyEasyTankEquipPresets(data)
            pushMessagesFromResult(result)
        if result and not result.success:
            callback(result)
            return
        else:
            crew = self.__getCrewPresetDataForApplying()
            self.__applyCrew(crew)
            callback(result)
            return

    @adisp_async
    @adisp_process
    def __applyEasyTankEquipPresets(self, data, callback):
        result = yield EasyTankEquipApplyProcessor(g_currentVehicle.item, self.copyVehicle, **data).request()
        callback(result)

    def __applyCrew(self, crew):
        if not crew:
            return
        else:
            actions = []
            for index, tankman in crew:
                if tankman is None:
                    factory.doAction(factory.BUY_AND_EQUIP_TANKMAN, g_currentVehicle.item, index)
                actions.append((factory.EQUIP_TANKMAN,
                 tankman.invID,
                 g_currentVehicle.item.invID,
                 index))

            if actions:
                BigWorld.player().doActions(actions)
            return

    def __getPresetsDataForApplying(self):
        applyingParamsMap = {ProposalType.SHELLS: 'shellsData',
         ProposalType.CONSUMABLES: 'eqsData',
         ProposalType.OPT_DEVICES: 'optDevicesData',
         ProposalType.STYLES: 'styleData'}
        applyingData = {}
        for proposalType, provider in self.__providers.items():
            applyingPresetData = provider.getPresetDataForApplying()
            if applyingPresetData is not None and proposalType in applyingParamsMap:
                applyingData[applyingParamsMap[proposalType]] = applyingPresetData

        return applyingData

    def __getCrewPresetDataForApplying(self):
        provider = self.__providers.get(ProposalType.CREW)
        if not provider:
            _logger.warning('The crew provider for the card was not found when applying preset.')
            return
        return provider.getPresetDataForApplying()

    def __saveAccountSettings(self):
        for provider in self.__providers.values():
            provider.saveAccountSettings()

    @wg_async
    def __onExit(self):
        self.__onClose()
        raise AsyncReturn(True)

    @wg_async
    def __closeConfirmator(self):
        result = yield wg_await(self.__onExit())
        raise AsyncReturn(result)
