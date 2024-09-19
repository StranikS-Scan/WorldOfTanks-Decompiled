# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_portal.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_LAUNCH_ANIMATED
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.game_control.wt_lootboxes_controller import convertToBonuses
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_model import WtEventPortalModel, PortalType, LootBoxType
from gui.impl.gui_decorators import args2params
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.lobby.wt_event.wt_event_constants import BonusGroup
from gui.impl.lobby.wt_event.wt_event_base_portals_view import WtEventBasePortalsView
from gui.impl.lobby.wt_event.tooltips.wt_event_info_tooltip_view import WtEventInfoTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_guaranteed_reward_tooltip_view import WtGuaranteedRewardTooltipView
from gui.impl.lobby.wt_event.wt_event_sound import changePortalState
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData
from gui.wt_event.wt_event_helpers import getPortalCost
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, setBonusVehicles, setGuaranteedAward, hasUnclaimedLoot
from gui.wt_event.wt_event_simple_bonus_packers import getWtEventSimpleBonusPacker, fillPortalRewardModel, sortBonuses, packSpecialVehicleBonus, HUNTER_BONUSES_ORDER, BOSS_BONUSES_ORDER, packRentVehicleBonus
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWTLootBoxesController
_logger = logging.getLogger(__name__)
_DEFAULT_RUN_PORTAL_TIMES = 1
_UNCLAIMED_RUN_DELAY = 1
_BoxTypesForPortals = {PortalType.HUNTER: EventLootBoxes.WT_HUNTER,
 PortalType.BOSS: EventLootBoxes.WT_BOSS}

class WTEventPortalView(WtEventBasePortalsView, CallbackDelayer):
    __slots__ = ('__portalType', '__tooltipItems', '__defaultRunPortalTimes')
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lootBoxCtrl = dependency.descriptor(IWTLootBoxesController)

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
        tooltipId = int(event.getArgument('tooltipId'))
        return self.__tooltipItems.get(str(tooltipId)) if tooltipId is not None else None

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
        self.__fillPortalData()

    def __fillPortalData(self):
        activeBox = EventLootBoxes.WT_HUNTER if self.__portalType == PortalType.HUNTER else EventLootBoxes.WT_BOSS
        inactiveBox = EventLootBoxes.WT_BOSS if self.__portalType == PortalType.HUNTER else EventLootBoxes.WT_HUNTER
        probabilities = self.__lootBoxCtrl.getSlotsProbabilities(activeBox)
        with self.viewModel.transaction() as model:
            model.setPortalType(self.__portalType)
            model.setBackButtonText(backport.text(R.strings.event.WtEventPortals.inside.backButton()))
            model.setIsLaunchAnimated(AccountSettings.getSettings(IS_LAUNCH_ANIMATED))
            if self.__portalType == PortalType.HUNTER:
                model.setHighRewardProbability(probabilities[0])
                model.setMediumRewardProbability(probabilities[1])
                model.setTankRewardProbability(0)
                model.setRentalRewardProbability(0)
                model.guaranteedAward.setGuaranteedTankAttemptCount(0)
                model.guaranteedAward.setLeftAttemptsCount(0)
                model.guaranteedAward.setAttemptsCount(0)
                model.guaranteedAward.setIsIgnored(0)
            else:
                model.setGuaranteedRewadProbability(probabilities[0])
                model.setHighRewardProbability(probabilities[1])
                model.setMediumRewardProbability(probabilities[2])
                model.setTankRewardProbability(probabilities[3])
                model.setRentalRewardProbability(probabilities[4])
                setGuaranteedAward(model.guaranteedAward)
            self.__updatePortalInfo(model, lootBoxType=activeBox, inactiveBoxType=inactiveBox)

    def _getEvents(self):
        return ((self._lootBoxesCtrl.onUpdatedConfig, self.__updateBoxesConfig),
         (self.viewModel.onRunPortalClick, self.__onRunPortal),
         (self.viewModel.onAnimationSettingChange, self.__switchAnimationSetting),
         (self.viewModel.onUpdateLootbox, self.__onUpdateLootbox))

    def _addListeners(self):
        super(WTEventPortalView, self)._addListeners()
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)
        super(WTEventPortalView, self)._removeListeners()

    def _onPortalAwardsViewClose(self, _):
        self.destroyWindow()

    def _onCacheResync(self, *_):
        if not self._eventCtrl.isEnabled():
            return
        self._updateLootBoxesPurchaseCount()
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self._lobbyContext.getServerSettings().isLootBoxesEnabled())
            if self.__portalType == PortalType.HUNTER:
                self.__updatePortalInfo(model, lootBoxType=EventLootBoxes.WT_HUNTER, inactiveBoxType=EventLootBoxes.WT_BOSS)
            elif self.__portalType == PortalType.BOSS:
                self.__updatePortalInfo(model, lootBoxType=EventLootBoxes.WT_BOSS, inactiveBoxType=EventLootBoxes.WT_HUNTER)

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

    @args2params(LootBoxType)
    def __onUpdateLootbox(self, lootBoxType):
        self.__portalType = PortalType.HUNTER if lootBoxType == LootBoxType.HUNTER else PortalType.BOSS
        self._updateModel()

    def __getDefaultRunPortalTimes(self, lootBoxType):
        lootBoxesCount = self._lootBoxesCtrl.getLootBoxesCountByTypeForUI(lootBoxType)
        return self.__defaultRunPortalTimes if lootBoxesCount >= self.__defaultRunPortalTimes else _DEFAULT_RUN_PORTAL_TIMES

    def __updatePortalInfo(self, model, lootBoxType, inactiveBoxType):
        model.portalAvailability.setAttemptPrice(getPortalCost(lootBoxType))
        model.setDefaultRunPortalTimes(self.__getDefaultRunPortalTimes(lootBoxType))
        setLootBoxesCount(model.portalAvailability, lootBoxType)
        setLootBoxesCount(model.inactivePortalAvailability, inactiveBoxType)
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
        if lootBoxType == EventLootBoxes.WT_HUNTER:
            lastIndex = self.__setProbBonuses(lootBoxType, bonuses, BonusGroup.GUARANTEED, model.rewards, 0)
            self.__setProbBonuses(lootBoxType, bonuses, BonusGroup.HIGH, model.customizationReward, lastIndex)
        else:
            model.bossSpecificRewards.clearItems()
            model.collectionReward.clearItems()
            self.__setProbBonuses(lootBoxType, bonuses, BonusGroup.GUARANTEED, model.guaranteedRewards, 0)
            self.__setProbBonuses(lootBoxType, bonuses, BonusGroup.HIGH, model.rewards, 0)
            extra = self.__lootBoxCtrl.getExtraRewards(lootBoxType, count=0)
            extraRewardBonusGroup = convertToBonuses(extra)[0]
            packMissionsBonusModelAndTooltipData(bonuses=extraRewardBonusGroup.bonuses, packer=getWtEventSimpleBonusPacker(), model=model.bossSpecificRewards, tooltipData=self.__tooltipItems, iterator=0)
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
            lastIndex = packMissionsBonusModelAndTooltipData(bonuses=sorted(bonusGroup.bonuses, key=lambda bonus: sortBonuses(bonus, order)), packer=getWtEventSimpleBonusPacker(), model=bonusesListModel, tooltipData=self.__tooltipItems, iterator=iterator)
            return lastIndex


class WtEventPortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, portalType, defaultRunPortalTimes, parent=None):
        super(WtEventPortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTEventPortalView(portalType, defaultRunPortalTimes), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _initialize(self):
        super(WtEventPortalWindow, self)._initialize()
        if Waiting.isOpened('updating'):
            Waiting.hide('updating')
