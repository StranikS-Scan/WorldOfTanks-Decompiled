# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_portal.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LAUNCH_ANIMATED
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import WtEventPortalModel, PortalType, EventTankType
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.lobby.wt_event.wt_event_constants import BonusGroup
from gui.impl.lobby.wt_event.wt_event_base_portals_view import WtEventBasePortalsView
from gui.impl.lobby.wt_event.tooltips.wt_event_info_tooltip_view import WtEventInfoTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from gui.impl.lobby.wt_event.wt_event_sound import changePortalState, playLootBoxPortalExit
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared import event_dispatcher, g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData
from gui.wt_event.wt_event_helpers import getPortalCost
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, setBonusVehicles, setGuaranteedAward, hasUnclaimedLoot, fillFirstLaunchReward
from gui.wt_event.wt_event_simple_bonus_packers import getWtEventSimpleBonusPacker, fillPortalRewardModel, sortBonuses, packSpecialVehicleBonus, HUNTER_BONUSES_ORDER, BOSS_BONUSES_ORDER, packRentVehicleBonus
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)
_DEFAULT_RUN_PORTAL_TIMES = 1
_UNCLAIMED_RUN_DELAY = 1
_BoxTypesForPortals = {PortalType.HUNTER: EventLootBoxes.WT_HUNTER,
 PortalType.BOSS: EventLootBoxes.WT_BOSS}

class WTEventPortalView(WtEventBasePortalsView, CallbackDelayer):
    __slots__ = ('__portalType', '__tooltipItems', '__defaultRunPortalTimes')
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, portalType, defaultRunPortalTimes=1):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventInsidePortal(), model=WtEventPortalModel())
        super(WTEventPortalView, self).__init__(settings)
        self.__portalType = portalType
        self.__tooltipItems = {}
        self.__defaultRunPortalTimes = defaultRunPortalTimes

    @property
    def viewModel(self):
        return super(WTEventPortalView, self).getViewModel()

    @property
    def portalType(self):
        return self.__portalType

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventInfoTooltipView():
            return WtEventInfoTooltipView(tooltipType=event.getArgument('tooltipType'))
        return WtGuaranteedRewardTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtGuaranteedRewardTooltipView() else super(WTEventPortalView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventPortalView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipItems.get(int(tooltipId)) if tooltipId is not None else None

    def _onLoaded(self, *args, **kwargs):
        super(WTEventPortalView, self)._onLoaded(*args, **kwargs)
        changePortalState(self.__portalType)
        portalType = EventLootBoxes.WT_HUNTER if self.__portalType == PortalType.HUNTER else EventLootBoxes.WT_BOSS
        if hasUnclaimedLoot(portalType):
            self.delayCallback(_UNCLAIMED_RUN_DELAY, self.__openPortal)

    def _finalize(self):
        self.__tooltipItems = None
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
            model.setBackButtonText(backport.text(R.strings.event.WtEventPortals.inside.backButton()))
            model.setIsLaunchAnimated(AccountSettings.getSettings(IS_LAUNCH_ANIMATED))
            if portalType == PortalType.HUNTER:
                self.__updatePortalInfo(model, lootBoxType=EventLootBoxes.WT_HUNTER)
            elif portalType == PortalType.BOSS:
                self.__updatePortalInfo(model, lootBoxType=EventLootBoxes.WT_BOSS)
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
            model.setIsBoxesEnabled(self._lobbyContext.getServerSettings().isLootBoxesEnabled())
            if self.__portalType == PortalType.HUNTER:
                self.__updatePortalInfo(model, lootBoxType=EventLootBoxes.WT_HUNTER)
            elif self.__portalType == PortalType.BOSS:
                self.__updatePortalInfo(model, lootBoxType=EventLootBoxes.WT_BOSS)

    def __onBackClick(self, isEsc=False):
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
            isBoxesEnabled = self._lobbyContext.getServerSettings().isLootBoxesEnabled()
            model.setIsBoxesEnabled(isBoxesEnabled)
            setGuaranteedAward(model.guaranteedAward)
            if isBoxesEnabled and self.__portalType in (PortalType.HUNTER, PortalType.BOSS):
                self.__setBonuses(self.__getLootBoxType(), model)

    def __getLootBoxType(self):
        return _BoxTypesForPortals.get(self.__portalType)

    def __setBonuses(self, lootBoxType, model):
        bonuses = self._lootBoxesCtrl.getLootBoxesRewards(lootBoxType)
        lastIndex = self.__setProbBonuses(lootBoxType, bonuses, BonusGroup.HIGH, model.rewards, 0)
        if lootBoxType == EventLootBoxes.WT_HUNTER:
            self.__setProbBonuses(lootBoxType, bonuses, BonusGroup.AVERAGE, model.customizationReward, lastIndex)
        else:
            setBonusVehicles(model.tanks, withoutSpecialTank=True)
            packSpecialVehicleBonus(model.rewardTanks, bonuses, self.__tooltipItems)
            packRentVehicleBonus(model.rentalTank, bonuses, self.__tooltipItems)
            styleBonuses = bonuses.get(BonusGroup.AVERAGE)
            if styleBonuses is not None:
                fillPortalRewardModel(model.collectionReward, styleBonuses.bonuses)
        return

    def __setProbBonuses(self, lootBoxType, bonuses, bonusGroup, listModel, iterator=0):
        bonusGroup = bonuses.get(bonusGroup)
        if bonusGroup is None:
            return
        else:
            order = BOSS_BONUSES_ORDER if lootBoxType == EventLootBoxes.WT_BOSS else HUNTER_BONUSES_ORDER
            bonusesListModel = listModel
            bonusesListModel.clearItems()
            lastIndex = packBonusModelAndTooltipData(bonuses=sorted(bonusGroup.bonuses, key=lambda bonus: sortBonuses(bonus, order)), packer=getWtEventSimpleBonusPacker(), model=bonusesListModel, tooltipData=self.__tooltipItems, iterator=iterator)
            bonusesListModel.invalidate()
            return lastIndex


class WtEventPortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, portalType, defaultRunPortalTimes, parent=None):
        super(WtEventPortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTEventPortalView(portalType, defaultRunPortalTimes), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _initialize(self):
        super(WtEventPortalWindow, self)._initialize()
        if Waiting.isOpened('updating'):
            Waiting.hide('updating')
