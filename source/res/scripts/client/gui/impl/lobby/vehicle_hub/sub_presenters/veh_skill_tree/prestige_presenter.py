# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/sub_presenters/veh_skill_tree/prestige_presenter.py
from __future__ import absolute_import
from collections import OrderedDict
from functools import partial
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VEH_SKILL_TREE_PRESTIGE_GLARE_SHOWN
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.vehicle_hub import VehicleHubCtx
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.presenter_location_controller import IPresenterLocationController
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.utils import getVehSkillTreeRewardViewBonusPacker, getPrestigeBonus, PrestigeBonusContext
from gui.impl.lobby.veh_skill_tree.tooltips.prestige_reward_tooltip import PrestigeRewardTooltipView
from gui.impl.gui_decorators import args2params
from gui.prestige.prestige_helpers import getVehiclePrestige, getVehicleAchievedMilestones, fillPrestigeEmblemModel, getMilestones, DEFAULT_PRESTIGE
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showStylePreview, showVehicleHubVehSkillTreePrestige
from gui.shared.gui_items import GUI_ITEM_TYPE, getItemTypeID
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.prestige_view_model import PrestigeViewModel, PrestigeState
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.rewards_slot_model import RewardStatus
_logger = logging.getLogger(__name__)

class PrestigePresenter(SubModelPresenter, IPresenterLocationController):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, viewModel, parentView):
        super(PrestigePresenter, self).__init__(viewModel, parentView)
        self.__vehCD = None
        self.__vehiclePrestige = DEFAULT_PRESTIGE
        self.__vehicleAchievedMilestones = None
        self.__rewardStates = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, vhCtx):
        super(PrestigePresenter, self).initialize()
        self.__vehCD = vhCtx.intCD
        self.__vehiclePrestige = DEFAULT_PRESTIGE
        self.__vehicleAchievedMilestones = set()
        self.__rewardStates = OrderedDict()
        settings = AccountSettings.getUIFlag(VEH_SKILL_TREE_PRESTIGE_GLARE_SHOWN)
        settings.add(self.__vehCD)
        AccountSettings.setUIFlag(VEH_SKILL_TREE_PRESTIGE_GLARE_SHOWN, settings)
        self._initializeLocation()
        self.__update()

    def finalize(self):
        self._finalizeLocation()
        super(PrestigePresenter, self).finalize()

    def clear(self):
        self.__vehCD = None
        self.__vehiclePrestige = None
        self.__vehicleAchievedMilestones = None
        self.__rewardStates = None
        super(PrestigePresenter, self).clear()
        return

    def _initializeLocation(self):
        pass

    def _finalizeLocation(self):
        pass

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.mono.vehicle_hub.tooltips.prestige_reward_tooltip():
            level = event.getArgument('level')
            if level is not None:
                milestones = getMilestones(self.__vehCD)
                state = self.__rewardStates.get(level)
                if milestones and state:
                    bonus = getPrestigeBonus(milestones, PrestigeBonusContext(self.__vehCD, level, state))
                    if bonus:
                        return PrestigeRewardTooltipView(bonus)
                    _logger.error('Bonus cannot be parsed')
                else:
                    _logger.error('Bonus with passed level is not found: %d', level)
            else:
                _logger.error('Missing level to show tooltip')
        return super(PrestigePresenter, self).createToolTipContent(event, contentID)

    def _getCallbacks(self):
        return (('stats.dossier', self.__dossierUpdate), ('stats.prestigeMilestonesAchieved', self.__prestigeMilestonesAchievedUpdate))

    def _getEvents(self):
        return ((self.viewModel.onPreview, self.__onRewardPreview),)

    @args2params(int)
    def __onRewardPreview(self, level):
        milestones = getMilestones(self.__vehCD)
        state = self.__rewardStates.get(level)
        if not state or not milestones:
            return
        else:
            bonus = getPrestigeBonus(milestones, PrestigeBonusContext(self.__vehCD, level, state))
            if not bonus:
                return
            customizations = bonus.getCustomizations()
            if not customizations:
                return
            itemTypeID = getItemTypeID(customizations[0].get('custType'))
            if itemTypeID is None or itemTypeID != GUI_ITEM_TYPE.STYLE:
                return
            c11nItem = bonus.getC11nItem(customizations[0])

            def __onRewardPreviewCallback(vehCD):
                showVehicleHubVehSkillTreePrestige(intCD=vehCD)

            g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
            showStylePreview(self.__vehCD, c11nItem, descr=c11nItem.getDescription(), backCallback=partial(__onRewardPreviewCallback, self.__vehCD), backBtnDescrLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.skillTreePrestige()))
            return

    def __dossierUpdate(self, *_):
        self.__update()

    def __prestigeMilestonesAchievedUpdate(self, args):
        self.__update()

    def __update(self):
        self.__vehiclePrestige = getVehiclePrestige(self.__vehCD)
        self.__vehicleAchievedMilestones = getVehicleAchievedMilestones(self.__vehCD)
        milestones = getMilestones(self.__vehCD)
        if milestones:
            self.__rewardStates = self.__getRewardStates(milestones)
            self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as vm:
            self.__fillRewards(vm)
            fillPrestigeEmblemModel(vm.prestigeEmblem, self.__vehiclePrestige.currentLevel, self.__vehCD)
            vm.setPrestigeState(self.__getPrestigeState())

    def __fillRewards(self, viewModel):
        bonuses = list(filter(None, (getPrestigeBonus(getMilestones(self.__vehCD), PrestigeBonusContext(self.__vehCD, level, state)) for level, state in self.__rewardStates.items())))
        rewardArray = viewModel.getRewards()
        rewardArray.clear()
        packBonusModelAndTooltipData(bonuses, rewardArray, packer=getVehSkillTreeRewardViewBonusPacker())
        return

    def __getRewardStates(self, milestones):
        vehicleLevel = self.__vehiclePrestige.currentLevel
        wasAchived = True
        states = OrderedDict()
        for rewardLevel in sorted(milestones):
            if self.__vehiclePrestige == DEFAULT_PRESTIGE:
                state = RewardStatus.BLOCKED
            elif vehicleLevel >= rewardLevel and rewardLevel in self.__vehicleAchievedMilestones:
                state = RewardStatus.ACHIEVED
                wasAchived = True
            elif wasAchived:
                state = RewardStatus.PROGRESS
                wasAchived = False
            else:
                state = RewardStatus.AVAILABLE
            states[rewardLevel] = state

        return states

    def __getPrestigeState(self):
        prestigeConfig = self.__lobbyContext.getServerSettings().prestigeConfig
        if self.__vehiclePrestige.currentLevel == prestigeConfig.defaultMaxLevel:
            return PrestigeState.COMPLETED
        return PrestigeState.DISABLED if self.__vehiclePrestige == DEFAULT_PRESTIGE else PrestigeState.AVAILABLE
