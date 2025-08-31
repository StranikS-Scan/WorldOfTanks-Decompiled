# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_event_portal.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LAUNCH_ANIMATED
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.Waiting import Waiting
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.wt_event.wt_event_helpers import getPortalCost
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui.shared.event_dispatcher import showEventStorageWindow
from gui.server_events.bonuses import CustomizationsBonus, CreditsBonus
from white_tiger.gui.impl.gen.view_models.views.lobby.portal_reward import PortalReward
from white_tiger.gui.impl.gen.view_models.views.common.wt_common_consts import WTVehicleType
from white_tiger.gui.impl.lobby.wt_event_constants import BonusGroup, WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.wt_event_base_portals_view import WtEventBasePortalsView
from white_tiger.gui.impl.lobby.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from white_tiger.gui.impl.lobby.wt_event_sound import changePortalState, playLootBoxPortalExit
from white_tiger.gui.impl.lobby.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from white_tiger.gui.impl.lobby.tooltips.wt_bonus_group_tooltip import WtBonusGroupTooltip
from white_tiger.gui.impl.lobby.packers.wt_event_bonuses_packers import getWtUIBonusPacker
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_model import WtEventPortalModel, PortalType, EventTankType
from white_tiger.gui.wt_event_models_helper import setLootBoxesCount, setGuaranteedAward, hasUnclaimedLoot, fillFirstLaunchReward
from white_tiger.gui.impl.lobby.packers.wt_event_simple_bonus_packers import sortBonuses, HUNTER_BONUSES_ORDER, BOSS_BONUSES_ORDER, packBossMainVehicleBonus, TANK_BONUSES_ORDER
from skeletons.gui.game_control import ILootBoxesController
_logger = logging.getLogger(__name__)
_DEFAULT_RUN_PORTAL_TIMES = 1
_UNCLAIMED_RUN_DELAY = 1
_BoxTypesForPortals = {PortalType.HUNTER: WhiteTigerLootBoxes.WT_HUNTER,
 PortalType.BOSS: WhiteTigerLootBoxes.WT_BOSS}

class WTEventPortalView(WtEventBasePortalsView, CallbackDelayer):
    __slots__ = ('__portalType', '__tooltipItems', '__defaultRunPortalTimes', '__groupedBonuses', '__bonusesPacker')
    __lootBoxesCtrl = dependency.descriptor(ILootBoxesController)
    __TICKET_TO_BOSS = {'wtevent_ticket': WTVehicleType.BOSS.value,
     'wtevent_ticket2025': WTVehicleType.BOSS_2025.value}

    def __init__(self, portalType, defaultRunPortalTimes=1):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.InsidePortalView(), model=WtEventPortalModel())
        super(WTEventPortalView, self).__init__(settings)
        self.__portalType = portalType
        self.__tooltipItems = {}
        self.__defaultRunPortalTimes = defaultRunPortalTimes
        self.__groupedBonuses = {}
        self.__tooltipData = {}
        self.__bonusesPacker = getWtUIBonusPacker()

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
        elif contentID == R.views.white_tiger.lobby.tooltips.TicketTooltipView():
            name = event.getArgument('name')
            bossType = self.__TICKET_TO_BOSS.get(name, WTVehicleType.BOSS.value)
            return WtEventTicketTooltipView(bossType)
        else:
            return super(WTEventPortalView, self).createToolTipContent(event, contentID)

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
        self.__tooltipItems = None
        self.__bonusesPacker = None
        super(WTEventPortalView, self)._finalize()
        return

    def _updateModel(self):
        if not self._eventCtrl.isEnabled():
            return
        super(WTEventPortalView, self)._updateModel()
        portalType = self.__portalType
        with self.viewModel.transaction() as model:
            model.setPortalType(portalType)
            model.setPrimaryEventTank(EventTankType.PRIMARY)
            model.setSecondaryEventTank(EventTankType.SECONDARY)
            model.setBackButtonText(backport.text(R.strings.wt_portals.insidePortal.backButton()))
            model.setIsLaunchAnimated(AccountSettings.getSettings(IS_LAUNCH_ANIMATED))
            if portalType == PortalType.HUNTER:
                self.__updatePortalInfo(model, lootBoxType=WhiteTigerLootBoxes.WT_HUNTER)
            elif portalType == PortalType.BOSS:
                self.__updatePortalInfo(model, lootBoxType=WhiteTigerLootBoxes.WT_BOSS)
                setGuaranteedAward(model.guaranteedAward)
                fillFirstLaunchReward(model, self.__getLootBoxType())

    def _addListeners(self):
        super(WTEventPortalView, self)._addListeners()
        self._lootBoxesCtrl.onUpdatedConfig += self.__updateBoxesConfig
        self.viewModel.onBackButtonClick += self.__onBackClick
        self.viewModel.onRunPortalClick += self.__onRunPortal
        self.viewModel.onAnimationSettingChange += self.__switchAnimationSetting
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        self._lootBoxesCtrl.onUpdatedConfig -= self.__updateBoxesConfig
        self.viewModel.onBackButtonClick -= self.__onBackClick
        self.viewModel.onRunPortalClick -= self.__onRunPortal
        self.viewModel.onAnimationSettingChange -= self.__switchAnimationSetting
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
        self._updateLootBoxesPurchaseCount()
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self.__lootBoxesCtrl.isEnabled())
            if self.__portalType == PortalType.HUNTER:
                self.__updatePortalInfo(model, lootBoxType=WhiteTigerLootBoxes.WT_HUNTER)
            elif self.__portalType == PortalType.BOSS:
                self.__updatePortalInfo(model, lootBoxType=WhiteTigerLootBoxes.WT_BOSS)

    def __onBackClick(self, isEsc=False):
        if isEsc and Waiting.isOpened('updating'):
            return
        playLootBoxPortalExit()
        parent = self.getParentWindow()
        self.destroyWindow()
        event_dispatcher.showEventStorageWindow(parent)

    def __onPortalAwardsViewClosed(self, *args):
        with self.viewModel.transaction() as model:
            self._updateModel()
            setGuaranteedAward(model.guaranteedAward)

    def __onRunPortal(self, args=None):
        Waiting.show('updating')
        self.__openPortal()

    def __openPortal(self):
        lootBoxType = self.__getLootBoxType()
        self._lootBoxesCtrl.onPortalOpened(lootBoxType, parentWindow=self.getParentWindow(), callbackFailure=self.__handleRequestFailure)

    def __previewBackCb(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.VEHICLE_PREVIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        showEventStorageWindow()

    def __handleRequestFailure(self):
        Waiting.hide('updating')
        self.destroyWindow()

    def __switchAnimationSetting(self):
        newState = not self.viewModel.getIsLaunchAnimated()
        AccountSettings.setSettings(IS_LAUNCH_ANIMATED, newState)
        self.viewModel.setIsLaunchAnimated(newState)

    def __getDefaultRunPortalTimes(self, lootBoxType):
        lootBoxesCount = self._lootBoxesCtrl.getLootBoxesCountByTypeForUI(lootBoxType)
        return self.__defaultRunPortalTimes if lootBoxesCount >= self.__defaultRunPortalTimes else _DEFAULT_RUN_PORTAL_TIMES

    def __updatePortalInfo(self, model, lootBoxType):
        model.portalAvailability.setAttemptPrice(getPortalCost(lootBoxType))
        model.setDefaultRunPortalTimes(self.__getDefaultRunPortalTimes(lootBoxType))
        setLootBoxesCount(model.portalAvailability, lootBoxType)
        self.__setBonuses(lootBoxType, model)

    def __updateBoxesConfig(self):
        with self.viewModel.transaction() as model:
            isBoxesEnabled = self.__lootBoxesCtrl.isEnabled()
            model.setIsBoxesEnabled(isBoxesEnabled)
            setGuaranteedAward(model.guaranteedAward)
            if isBoxesEnabled and self.__portalType in (PortalType.HUNTER, PortalType.BOSS):
                self.__setBonuses(self.__getLootBoxType(), model)

    def __getLootBoxType(self):
        return _BoxTypesForPortals.get(self.__portalType)

    def __setBonuses(self, lootBoxType, model):
        bonuses = self._lootBoxesCtrl.getLootBoxesRewards(lootBoxType)
        if lootBoxType == WhiteTigerLootBoxes.WT_HUNTER:
            self.__fillHunter(bonuses, model)
        elif lootBoxType == WhiteTigerLootBoxes.WT_BOSS:
            self.__fillBoss(bonuses, model)
        elif lootBoxType == WhiteTigerLootBoxes.WT_TANK:
            packBossMainVehicleBonus(model.rewardTank, bonuses, self.__tooltipItems)

    def __fillBoss(self, bonuses, model):
        bonuses = bonuses.get('byProbabilities', {})
        probability = 100
        p100 = bonuses.get(probability, [])
        model.setRewardsProbability(probability)
        self.__setProbBonuses(WhiteTigerLootBoxes.WT_BOSS, p100, model.rewards)
        probability = 5
        p5 = bonuses.get(probability, [])
        model.setCustomizationProbability(probability)
        self.__setProbBonuses(WhiteTigerLootBoxes.WT_BOSS, p5, model.collectionReward)
        p3 = bonuses.get(3, [])
        model.setTanksProbability(3)
        self.__setProbBonuses(WhiteTigerLootBoxes.WT_BOSS, p3, model.rewardTanks)

    def __fillHunter(self, bonuses, model):
        bonuses = bonuses.get('byProbabilities', {})
        probability = 100
        p100 = bonuses.get(probability, [])
        model.setRewardsProbability(probability)
        self.__setProbBonuses(WhiteTigerLootBoxes.WT_HUNTER, p100, model.rewards)
        probability = 15
        p15 = bonuses.get(probability, [])
        model.setCustomizationProbability(probability)
        self.__setProbBonuses(WhiteTigerLootBoxes.WT_HUNTER, p15, model.customizationReward)

    def __fillProbabilities(self, bonuses, model):

        def getProbability(bonusGroup):
            return bonuses[bonusGroup].probability[0] * 100

        if BonusGroup.GUARANTEED_ITEMS in bonuses:
            model.setRewardsProbability(getProbability(BonusGroup.GUARANTEED_ITEMS))
        if BonusGroup.CUSTOMIZATION in bonuses:
            model.setCustomizationProbability(getProbability(BonusGroup.CUSTOMIZATION))
        if BonusGroup.VEHICLES in bonuses:
            model.setTanksProbability(getProbability(BonusGroup.VEHICLES))

    def __setProbBonuses(self, lootBoxType, bonuses, listModel):
        order = HUNTER_BONUSES_ORDER
        if lootBoxType == WhiteTigerLootBoxes.WT_BOSS:
            order = BOSS_BONUSES_ORDER
        elif lootBoxType == WhiteTigerLootBoxes.WT_TANK:
            order = TANK_BONUSES_ORDER
        bonusesListModel = listModel
        bonusesListModel.clearItems()
        box = self._itemsCache.items.tokens.getLootBoxByType(lootBoxType)
        bonusGroupes = box.getBonusGroupes()
        customBonusItems = box.getCustomBonusData()
        self.__packMissionsBonusModelAndTooltipData(bonuses=sorted(bonuses, key=lambda bonus: sortBonuses(bonus, order)), model=bonusesListModel, bonusGroupes=bonusGroupes, customBonusItems=customBonusItems)
        bonusesListModel.invalidate()

    def __packMissionsBonusModelAndTooltipData(self, bonuses, model, bonusGroupes, customBonusItems):
        grouped = []
        common = []
        withCustomData = []
        for bonus in (b for b in bonuses if b.isShowInGUI()):
            groupId, _ = self.__getGroupIdData(bonus, bonusGroupes)
            if groupId:
                grouped.append(bonus)
            data = self.__getCustomBonusData(bonus, customBonusItems)
            if data:
                withCustomData.append((bonus, data))
            common.append(bonus)

        if common:
            self.__packCommon(common, model)
        if grouped:
            self.__packGrouped(grouped, model, bonusGroupes)
        if withCustomData:
            self.__packCustomData(withCustomData, model)

    def __getCustomBonusData(self, bonus, customBonusItems):
        for key, item in customBonusItems.iteritems():
            if item.get('type') == 'vehicle' and bonus.getName() == 'vehicles':
                vehicle, _ = bonus.getVehicles()[0]
                if key == vehicle.typeDescr.name:
                    return item

        return None

    def __packCommon(self, bonuses, model):
        tooltipIndex = 0 if self.__tooltipData is None else len(self.__tooltipData)
        for bonus in (b for b in bonuses if b.isShowInGUI()):
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

    def __packGrouped(self, bonuses, model, bonusGroupes):
        for bonus in (b for b in bonuses if b.isShowInGUI()):
            groupId, bonusGroupData = self.__getGroupIdData(bonus, bonusGroupes)
            self.__groupedBonuses.setdefault(groupId, [])
            if not self.__groupedBonuses[groupId]:
                item = PortalReward()
                item.setName(bonusGroupData.get('icon', ''))
                item.setIndex(groupId)
                if hasattr(item, 'setTooltipId'):
                    item.setTooltipId(str(groupId))
                item.setTooltipContentId(str(groupId))
                model.addViewModel(item)
            self.__groupedBonuses[groupId].append(bonus)

    def __packCustomData(self, bonuses, model):
        tooltipIndex = 0 if self.__tooltipData is None else len(self.__tooltipData)
        for bonus, customData in bonuses:
            if not bonus.isShowInGUI():
                continue
            bonusList = self.__bonusesPacker.pack(bonus)
            withTooltips = bonusList and self.__tooltipData is not None
            bTooltipList = self.__bonusesPacker.getToolTip(bonus) if withTooltips else []
            bContentIdList = self.__bonusesPacker.getContentId(bonus) if withTooltips else []
            for bIndex, bModel in enumerate(bonusList):
                bModel.setIndex(bIndex + tooltipIndex)
                if withTooltips:
                    tooltipIndex = self.__packBonusTooltip(bModel, bIndex, bTooltipList, bContentIdList, tooltipIndex)
                bModel.setIcon(customData.get('icon', ''))
                bModel.setName(customData.get('icon', ''))
                bModel.setIsCustom(True)
                model.addViewModel(bModel)

        return

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


class WtEventPortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, portalType, defaultRunPortalTimes, parent=None):
        super(WtEventPortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTEventPortalView(portalType, defaultRunPortalTimes), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _initialize(self):
        super(WtEventPortalWindow, self)._initialize()
        if Waiting.isOpened('updating'):
            Waiting.hide('updating')
