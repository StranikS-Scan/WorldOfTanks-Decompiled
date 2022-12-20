# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_rewards_view.py
import logging
from collections import OrderedDict
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_rewards_view_model import BattleMattersRewardsViewModel, State, RewardType
from gui.impl.lobby.battle_matters.tooltips.battle_matters_token_tooltip_view import BattleMattersTokenTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses, getMergedBonusesFromDicts
from gui.server_events.events_dispatcher import showBattleMatters
from gui.shared.event_dispatcher import showDelayedReward, selectVehicleInHangar, showHangar
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData
from gui.impl.lobby.battle_matters.battle_matters_bonus_packer import getBattleMattersBonusPacker, indexesCmp, bonusesSort, blueprintsCmp
from helpers import dependency
from sound_gui_manager import CommonSoundSpaceSettings
from shared_utils import first
from skeletons.gui.battle_matters import IBattleMattersController
from gui.server_events.bonuses import VehiclesBonus, TankmenBonus
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
    from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_vehicle_model import BattleMattersVehicleModel
    from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
    from frameworks.wulf import ViewEvent, View
    from typing import Sequence, Tuple, Callable, Optional
    from Event import Event
_logger = logging.getLogger(__name__)
_CUSTOMIZATIONS_ORDER = ('style', 'emblem', 'camouflage', 'modification', 'decal', 'inscription', 'paint')
_DEVICES_TYPES_ORDER = (SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS, SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY, SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT)
_ITEMS_NAMES_ORDER = ('optionalDevice', 'battleBooster', 'equipment')

def _vehiclesCmp(firstModel, secondModel):
    return cmp(firstModel.getLevel(), secondModel.getLevel())


def _customizationsCmp(firstModel, secondModel):
    return indexesCmp(_CUSTOMIZATIONS_ORDER, firstModel.getIcon(), secondModel.getIcon())


def _itemsCmp(firstModel, secondModel):
    result = indexesCmp(_ITEMS_NAMES_ORDER, firstModel.getName(), secondModel.getName())
    if not result:
        result = indexesCmp(_DEVICES_TYPES_ORDER, firstModel.getOverlayType(), secondModel.getOverlayType())
    return result


def _customSort(rewardType):
    return _CUSTOM_SORT.get(rewardType, lambda _, __: 0)


_CUSTOM_SORT = {VehiclesBonus.VEHICLES_BONUS: _vehiclesCmp,
 'customizations': _customizationsCmp,
 'items': _itemsCmp}
_CLIENT_REWARD_IDX = -1

class BattleMattersRewardsView(ViewImpl):
    __slots__ = ('__cds', '__questOrder', '__isPairQuest', '__isWithDelayed', '__delayedReward', '__intermediateQuestID', '__intermediateRewards', '__regularQuestID', '__regularRewards', '__tooltipData')
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='battle_matters', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='bm_reward', exitEvent='', parentSpace='')
    __battleMattersController = dependency.descriptor(IBattleMattersController)

    def __init__(self, ctx):
        settings = ViewSettings(layoutID=R.views.lobby.battle_matters.BattleMattersRewardsView(), model=BattleMattersRewardsViewModel())
        self.__cds = []
        self.__intermediateQuestID = ''
        self.__intermediateRewards = OrderedDict()
        self.__regularQuestID = ''
        self.__regularRewards = OrderedDict()
        self.__tooltipData = {RewardType.REGULAR: {},
         RewardType.VEHICLE: {},
         RewardType.INTERMEDIATE: {}}
        self.__questOrder = ctx.keys()[0]
        questData = ctx[self.__questOrder]
        self.__isPairQuest = questData.get('isInPair', False)
        self.__isWithDelayed = questData.get('isWithDelayedBonus', False)
        self.__delayedReward = ctx.get(_CLIENT_REWARD_IDX, {})
        questData = questData.get('quests', {})
        questIDs = questData.keys()
        for qID in questIDs:
            if self.__battleMattersController.isIntermediateBattleMattersQuestID(qID):
                self.__intermediateQuestID = qID
                self.__intermediateRewards = questData[qID]
            if self.__battleMattersController.isRegularBattleMattersQuestID(qID):
                self.__regularQuestID = qID
                self.__regularRewards = questData[qID]

        super(BattleMattersRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersRewardsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BattleMattersTokenTooltipView() if contentID == R.views.lobby.battle_matters.tooltips.BattleMattersTokenTooltipView() else super(BattleMattersRewardsView, self).createToolTipContent(event, contentID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(BattleMattersRewardsView, self).createToolTip(event)

    def onChooseVehicle(self):
        showDelayedReward()
        self.destroyWindow()

    def onShowVehicle(self):
        selectVehicleInHangar(first(self.__cds))
        self.destroyWindow()

    def onClose(self):
        if self.__getState() == State.TOKENVEHICLE:
            showHangar()
        self.destroyWindow()

    def onNextTask(self):
        showBattleMatters()
        self.destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(BattleMattersRewardsView, self)._onLoading(args, kwargs)
        vehicles = self.__processVehicles()
        regularBonuses = sorted(self.__getBonuses(self.__regularRewards), cmp=bonusesSort) if self.__regularQuestID else []
        intermediateBonuses = sorted(self.__getBonuses(self.__intermediateRewards), cmp=bonusesSort) if self.__intermediateQuestID else []
        self.__processBlueprints(regularBonuses)
        self.__processBlueprints(intermediateBonuses)
        self.__processDelayedBonuses(regularBonuses)
        packer = getBattleMattersBonusPacker()
        with self.viewModel.transaction() as tx:
            tx.setState(self.__getState())
            tx.setQuestNumber(self.__questOrder)
            self.__fillVehicles(tx, vehicles, packer)
            self.__fillIntermediate(tx, intermediateBonuses, packer)
            self.__fillRegular(tx, regularBonuses, packer)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),
         (self.viewModel.onChooseVehicle, self.onChooseVehicle),
         (self.viewModel.onNextTask, self.onNextTask),
         (self.viewModel.onShowVehicle, self.onShowVehicle))

    @staticmethod
    def __getBonuses(rewards):
        bonuses = []
        for key, value in rewards.items():
            bonus = getNonQuestBonuses(key, value)
            if bonus:
                bonuses.extend(bonus)

        return bonuses

    def __fillVehicles(self, model, vehicles, packer):
        vehiclesModel = model.getVehicles()
        vehiclesModel.clear()
        packBonusModelAndTooltipData(vehicles, packer, vehiclesModel, self.__tooltipData[RewardType.VEHICLE], sort=_customSort)
        vehiclesModel.invalidate()

    def __fillIntermediate(self, model, bonuses, packer):
        intermediateModel = model.getIntermediateRewards()
        intermediateModel.clear()
        packBonusModelAndTooltipData(bonuses, packer, intermediateModel, self.__tooltipData[RewardType.INTERMEDIATE], sort=_customSort)
        intermediateModel.invalidate()

    def __fillRegular(self, model, bonuses, packer):
        regularModel = model.getRegularRewards()
        regularModel.clear()
        packBonusModelAndTooltipData(bonuses, packer, regularModel, self.__tooltipData[RewardType.REGULAR], sort=_customSort)
        regularModel.invalidate()

    def __processVehicles(self):
        vehicles = [{VehiclesBonus.VEHICLES_BONUS: self.__regularRewards.pop(VehiclesBonus.VEHICLES_BONUS, {})}, {VehiclesBonus.VEHICLES_BONUS: self.__intermediateRewards.pop(VehiclesBonus.VEHICLES_BONUS, {})}]
        if self.__delayedReward:
            vehicles.append({VehiclesBonus.VEHICLES_BONUS: self.__delayedReward[VehiclesBonus.VEHICLES_BONUS]})
        vehicles = getMergedBonusesFromDicts(vehicles)
        for v in vehicles.get(VehiclesBonus.VEHICLES_BONUS, []):
            exclude = [ vehCD for vehCD in v if v[vehCD].get('compensatedNumber', 0) > 0 ]
            for vehCD in exclude:
                v.pop(vehCD)

        for v in vehicles.get(VehiclesBonus.VEHICLES_BONUS, []):
            self.__cds.extend(v.keys())

        return self.__getBonuses(vehicles) if vehicles else []

    def __processDelayedBonuses(self, bonuses):
        if self.__delayedReward:
            vehInfo = first(self.__delayedReward.get(VehiclesBonus.VEHICLES_BONUS))
            for vehCD, vehicle in vehInfo.iteritems():
                if vehicle:
                    bonuses.append(TankmenBonus('tankmen', [TankmenBonus.getTankmenDataForCrew(vehCD, vehicle.get('crewLvl', 0))]))

            if 'slots' in self.__delayedReward:
                bonuses.extend(getNonQuestBonuses('slots', self.__delayedReward['slots']))

    def __getState(self):
        if self.__questOrder == self.__battleMattersController.getFinalQuest().getOrder():
            return State.FINAL
        if self.__isWithDelayed:
            return State.TOKEN
        if self.__delayedReward:
            return State.TOKENVEHICLE
        return State.INTERMEDIATE if self.__intermediateQuestID else State.REGULAR

    def __getBackportTooltipData(self, event):
        rewardType = RewardType(event.getArgument(BattleMattersRewardsViewModel.ARG_REWARD_TYPE))
        index = int(event.getArgument(BattleMattersRewardsViewModel.ARG_REWARD_INDEX))
        if rewardType is None:
            _logger.warning('No reward type for backport tooltip')
            return
        else:
            return self.__tooltipData[rewardType].get(index)

    def __processBlueprints(self, bonuses):
        blueprints = [ b for b in bonuses if b.getName() == 'blueprints' ]
        firstIdx = bonuses.index(blueprints[0]) if blueprints else 0
        secondIdx = firstIdx + len(blueprints)
        if secondIdx:
            bonuses[firstIdx:secondIdx] = sorted(blueprints, cmp=blueprintsCmp)


class BattleMattersRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(BattleMattersRewardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattleMattersRewardsView(ctx=ctx), parent=parent)
