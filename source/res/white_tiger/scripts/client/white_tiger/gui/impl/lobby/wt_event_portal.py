# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_portal.py
from shared_utils import first
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LAUNCH_ANIMATED
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, Array
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.Waiting import Waiting
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.app_loader import IAppLoader
from skeletons.prebattle_vehicle import IPrebattleVehicle
from gui.server_events.bonuses import CustomizationsBonus, CreditsBonus
from skeletons.gui.game_control import IWhiteTigerController
from gui.wt_event.wt_event_helpers import getPortalCost
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.wt_event_base_portals_view import WtEventBasePortalsView
from white_tiger.gui.impl.lobby.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from white_tiger.gui.impl.lobby.wt_event_sound import changePortalState, playLootBoxPortalExit
from white_tiger.gui.impl.lobby.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtUIBonusPacker
from white_tiger.gui.impl.gen.view_models.views.common.wt_common_consts import PortalType
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_view_model import WtPortalViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_rewardList import WtPortalRewardlist, slotType
from white_tiger.gui.wt_event_models_helper import setGuaranteedReward, hasUnclaimedLoot
from white_tiger.gui.shared.event_dispatcher import showEventStorageWindow
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_portal_bonus_model import WtPortalBonusModel
from white_tiger.gui.impl.lobby.tooltips.wt_bonus_group_tooltip import WtBonusGroupTooltip
from white_tiger.gui.wt_event_helpers import extendBonusesByLootboxCustomSettings
from vehicle_systems.camouflages import getStyleProgressionOutfit
from gui.shared.event_dispatcher import showVehiclePreviewWithoutBottomPanel
_UNCLAIMED_RUN_DELAY = 1
_BoxTypesForPortals = {PortalType.HUNTER: WhiteTigerLootBoxes.WT_HUNTER,
 PortalType.BOSS: WhiteTigerLootBoxes.WT_BOSS}

class WTEventPortalView(WtEventBasePortalsView, CallbackDelayer):
    __slots__ = ('__portalType', '__bonusesPacker', '__boxCount', '__groupedBonuses')
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __appLoader = dependency.descriptor(IAppLoader)
    __wtController = dependency.descriptor(IWhiteTigerController)
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, portalType):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.WtPortalView(), model=WtPortalViewModel())
        super(WTEventPortalView, self).__init__(settings)
        self.__portalType = portalType
        self.__tooltipData = {}
        self.__bonusesPacker = getWtUIBonusPacker()
        self.__boxCount = 1
        self.__groupedBonuses = {}

    @property
    def viewModel(self):
        return super(WTEventPortalView, self).getViewModel()

    @property
    def portalType(self):
        return self.__portalType

    def createToolTipContent(self, event, contentID):
        tooltipId = None
        if event.getArgument('tooltipId') is not None:
            tooltipId = int(event.getArgument('tooltipId'))
        if tooltipId in self.__groupedBonuses:
            bonuses = self.__groupedBonuses[tooltipId]
            return WtBonusGroupTooltip(event.getArgument('name'), bonuses, '')
        elif contentID == R.views.white_tiger.lobby.tooltips.GuaranteedRewardTooltipView():
            return WtGuaranteedRewardTooltipView()
        else:
            return WtEventTicketTooltipView() if contentID == R.views.white_tiger.lobby.tooltips.TicketTooltipView() else super(WTEventPortalView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventPortalView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = None
        if event.getArgument('tooltipId') is not None:
            tooltipId = int(event.getArgument('tooltipId'))
        return self.__tooltipData.get(str(tooltipId)) if tooltipId is not None else None

    def _onLoaded(self, *args, **kwargs):
        super(WTEventPortalView, self)._onLoaded(*args, **kwargs)
        changePortalState(self.__portalType)
        portalType = WhiteTigerLootBoxes.WT_HUNTER
        if self.__portalType == PortalType.BOSS:
            portalType = WhiteTigerLootBoxes.WT_BOSS
        if hasUnclaimedLoot(portalType):
            self.delayCallback(_UNCLAIMED_RUN_DELAY, self.__openPortal)

    def _finalize(self):
        self.stopCallback(self.__openPortal)
        self.__bonusesPacker = None
        super(WTEventPortalView, self)._finalize()
        return

    def _updateModel(self):
        if not self._eventCtrl.isEnabled():
            return
        super(WTEventPortalView, self)._updateModel()
        with self.viewModel.transaction() as model:
            self.__fillPortalMain(model)

    def _addListeners(self):
        super(WTEventPortalView, self)._addListeners()
        self._lootBoxesCtrl.onUpdatedConfig += self.__updateBoxesConfig
        self.viewModel.onGoBack += self.__onGoBack
        self.viewModel.onRunPortal += self.__onRunPortal
        self.viewModel.onSwitchAnimation += self.__switchAnimation
        self.viewModel.onPreview += self.__onPreview
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        self._lootBoxesCtrl.onUpdatedConfig -= self.__updateBoxesConfig
        self.viewModel.onGoBack -= self.__onGoBack
        self.viewModel.onRunPortal -= self.__onRunPortal
        self.viewModel.onSwitchAnimation -= self.__switchAnimation
        self.viewModel.onPreview -= self.__onPreview
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)
        super(WTEventPortalView, self)._removeListeners()

    def _onClosedByUser(self):
        super(WTEventPortalView, self)._onClosedByUser()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onPortalAwardsViewClose(self, _):
        self.destroyWindow()

    def _onCacheResync(self, *_):
        if not self._eventCtrl.isEnabled():
            return
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self._lootBoxesCtrl.isEnabled())
            self._updateModel()

    def __onGoBack(self):
        playLootBoxPortalExit()
        parent = self.getParentWindow()
        self.destroyWindow()
        showEventStorageWindow(parent)

    def __onPortalAwardsViewClosed(self, *args):
        self.viewModel.setIsViewActive(True)
        selectedBoxNumber = 0
        if args and args[0].ctx:
            selectedBoxNumber = int(args[0].ctx.get('runCounter', 0))
        with self.viewModel.transaction() as model:
            self._updateModel()
            setGuaranteedReward(model.guaranteedReward)
            model.setSelectedLootBoxesCount(selectedBoxNumber)

    def __onRunPortal(self, args=None):
        Waiting.show('updating')
        boxCount = args.get('runCounter')
        lootBoxType = self.__getLootBoxType()
        lootBoxesCount = self._lootBoxesCtrl.getLootBoxesCountByType(lootBoxType)
        self.__boxCount = 1 if not boxCount else min(lootBoxesCount, int(boxCount))
        self.__openPortal(self.__boxCount)

    def __openPortal(self, boxCount=1):
        lootBoxType = self.__getLootBoxType()
        self.viewModel.setIsViewActive(False)
        self._lootBoxesCtrl.onPortalOpened(lootBoxType, boxCount=boxCount, parentWindow=self.getParentWindow(), callbackFailure=self.__handleRequestFailure)

    def __previewBackCb(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.VEHICLE_PREVIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        showEventStorageWindow()
        self.__prebattleVehicle.selectAny()

    def __handleRequestFailure(self):
        Waiting.hide('updating')
        self.destroyWindow()

    def __switchAnimation(self):
        newState = not self.viewModel.getIsLaunchAnimated()
        AccountSettings.setSettings(IS_LAUNCH_ANIMATED, newState)
        self.viewModel.setIsLaunchAnimated(newState)

    def __onPreview(self, args):
        vehicleCD = args.get('vehicleCD')
        vehicleCD = int(vehicleCD) if vehicleCD else 0
        styleCD = args.get('styleCD')
        styleCD = int(styleCD) if styleCD else 0
        style = None
        maxLevelOutfit = None
        if styleCD:
            style = self._itemsCache.items.getItemByCD(styleCD)
            vehicle = self._itemsCache.items.getVehicleCopyByCD(vehicleCD)
            season = first(style.seasons)
            outfit = style.getOutfit(season, vehicleCD=vehicle.descriptor.makeCompactDescr())
            maxLevelOutfit = getStyleProgressionOutfit(outfit, style.getMaxProgressionLevel(), season)
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import OptionalBlocks
        args = {'backBtnLabel': backport.text(R.strings.event.vehiclePortal.backToPortalButton()),
         'hiddenBlocks': (OptionalBlocks.BUYING_PANEL,)}
        showVehiclePreviewWithoutBottomPanel(vehicleCD, backCallback=self.__previewBackCb, style=style, **args)
        self._eventCtrl.setVehicleForPreview(vehicleCD, maxLevelOutfit)
        self._eventCtrl.getLootBoxAreaSoundMgr().leave()
        return

    def __updateBoxesConfig(self):
        with self.viewModel.transaction() as model:
            isBoxesEnabled = self._lootBoxesCtrl.isEnabled()
            model.setIsBoxesEnabled(isBoxesEnabled)
            setGuaranteedReward(model.guaranteedReward)
            self._updateModel()

    def __getLootBoxType(self):
        return _BoxTypesForPortals.get(self.__portalType)

    def __fillPortalMain(self, model):
        model.setPortalType(self.__portalType.value)
        model.setBackButtonText(backport.text(R.strings.wt_portals.insidePortal.backButton()))
        model.setIsLaunchAnimated(AccountSettings.getSettings(IS_LAUNCH_ANIMATED))
        setGuaranteedReward(model.guaranteedReward)
        self.__fillRewards(model, self.__portalType)

    def __fillRewards(self, model, portalType):
        boxType = WhiteTigerLootBoxes.WT_HUNTER if portalType == PortalType.HUNTER else WhiteTigerLootBoxes.WT_BOSS
        lootBox = self._itemsCache.items.tokens.getLootBoxByType(boxType)
        model.portalRun.setAttemptPrice(getPortalCost(boxType))
        lootBoxesCount = self._lootBoxesCtrl.getLootBoxesCountByType(boxType)
        model.portalRun.setLootBoxesCount(lootBoxesCount)
        slotsList = model.getRewardList()
        slotsList.clear()
        bonuses = self._lootBoxesCtrl.getLootBoxesRewards(boxType)
        bonusesByProb = bonuses.get('byProbabilities', [])
        index = 0
        self.__groupedBonuses.clear()
        customBonusData = lootBox.getCustomBonusData()
        for probability, bonuses in bonusesByProb:
            slot = WtPortalRewardlist()
            extendedBonuses = extendBonusesByLootboxCustomSettings(bonuses, customBonusData)
            self.__fillSlot(slot, probability, extendedBonuses, index, customBonusData)
            slotsList.addViewModel(slot)
            index = index + 1

        slotsList.invalidate()

    def __fillSlot(self, slot, probability, bonuses, index, customBonusData):
        probability = probability if probability % 1 != 0 else int(probability)
        slot.setProbability(str(probability))
        slot.setSlotType(slotType.DEFAULT)
        slot.setTitle('')
        probIcon = backport.image(R.images.white_tiger.gui.maps.icons.portals.probabilities.icon_random())
        slot.setProbabilityIconPath(probIcon)
        slot.setIndex(index)
        lootBoxSlots = self.__getSlotsData(probability, customBonusData)
        if lootBoxSlots:
            sType = lootBoxSlots.get('slotType')
            slot.setSlotType(slotType(sType))
            probIconName = lootBoxSlots.get('icon')
            probIcon = R.images.white_tiger.gui.maps.icons.portals.probabilities.dyn(probIconName)()
            slot.setProbabilityIconPath(backport.image(probIcon))
        rewardsModel = Array()
        groupedBonuses = customBonusData.get('bonusGroupes', {})
        self.__packBonuses(bonuses, groupedBonuses, rewardsModel)
        slot.setRewards(rewardsModel)

    def __getSlotsData(self, probability, customBonusData):
        for data in customBonusData.get('lootBoxSlots', {}):
            if data.get('probability') == probability:
                return data

        return {}

    def __packBonuses(self, bonuses, groupedBonuses, model):
        grouped = []
        common = []
        for bonus in bonuses:
            groupId, _ = getattr(bonus, 'wtExtendData', {}).get('group', (0, 0))
            if groupId:
                grouped.append(bonus)
            common.append(bonus)

        if common:
            self.__packCommon(model, common)
        if grouped:
            self.__packGrouped(model, grouped, groupedBonuses)

    def __packCommon(self, model, bonuses):
        tooltipIndex = 0 if self.__tooltipData is None else len(self.__tooltipData)
        for bonus in bonuses:
            bonusList = self.__bonusesPacker.pack(bonus)
            withTooltips = bonusList and self.__tooltipData is not None
            bTooltipList = self.__bonusesPacker.getToolTip(bonus) if withTooltips else []
            bContentIdList = self.__bonusesPacker.getContentId(bonus) if withTooltips else []
            for bIndex, bModel in enumerate(bonusList):
                bModel.setIndex(bIndex + tooltipIndex)
                if withTooltips:
                    tooltipIndex = self.__packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipIndex)
                model.addViewModel(bModel)

        return

    def __packGrouped(self, model, bonuses, bonusGroupes):
        for bonus in bonuses:
            groupId, bonusGroupData = self.__getGroupIdData(bonus, bonusGroupes)
            self.__groupedBonuses.setdefault(groupId, [])
            if not self.__groupedBonuses[groupId]:
                item = WtPortalBonusModel()
                item.setName(bonusGroupData.get('icon', ''))
                item.setIndex(groupId)
                if hasattr(item, 'setTooltipId'):
                    item.setTooltipId(str(groupId))
                item.setTooltipContentId(str(groupId))
                model.addViewModel(item)
            self.__groupedBonuses[groupId].append(bonus)

    def __getGroupIdData(self, bonus, bonusGroupes):
        value = bonus.getValue()
        if isinstance(value, dict):
            keys = value.keys()
            intCD = keys[0]
            for key, data in bonusGroupes.items():
                if intCD in data.get('itemIDs'):
                    return (key, data)

        elif isinstance(bonus, CustomizationsBonus):
            item = bonus.getCustomizations()[0]
            styleId = bonus.getC11nItem(item).id
            for key, data in bonusGroupes.items():
                if styleId in data.get('itemIDs'):
                    return (key, data)

        elif isinstance(bonus, CreditsBonus):
            for key, data in bonusGroupes.items():
                if bonus.getName() == data.get('type'):
                    return (key, data)

        return (None, None)

    def __packBonusTooltip(self, bonusModel, bonusIndex, bonusTooltipList, bonusContentIdList, tooltipIndex):
        if self.__tooltipData is None or not bonusTooltipList and not bonusContentIdList:
            return tooltipIndex
        else:
            tooltipIdx = str(tooltipIndex)
            bonusModel.setTooltipId(tooltipIdx)
            if bonusTooltipList:
                self.__tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
            if bonusContentIdList:
                bonusModel.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
            return tooltipIndex + 1


class WtEventPortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, portalType, parent=None):
        super(WtEventPortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTEventPortalView(portalType), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _initialize(self):
        super(WtEventPortalWindow, self)._initialize()
        if Waiting.isOpened('updating'):
            Waiting.hide('updating')
