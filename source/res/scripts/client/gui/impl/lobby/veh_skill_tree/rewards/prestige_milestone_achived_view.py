# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/rewards/prestige_milestone_achived_view.py
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from typing import Optional
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.vehicle_hub.sub_presenters.veh_skill_tree.utils import getPrestigeBonus, getVehSkillTreeRewardViewBonusPacker, PrestigeBonusContext
from gui.prestige.prestige_helpers import getMilestones
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.shared.gui_items import GUI_ITEM_TYPE, getItemTypeID
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.reward_screen_view_model import RewardScreenViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.rewards_slot_model import RewardStatus

class PrestigeMilestoneAchivedView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __customizationService = dependency.instance(ICustomizationService)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = RewardScreenViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__vehicle = None
        self.__level = None
        super(PrestigeMilestoneAchivedView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(PrestigeMilestoneAchivedView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PrestigeMilestoneAchivedView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onOpen, self.__onRewardPreview), (self.viewModel.onClose, self.destroyWindow))

    def _onLoading(self, vehCD, level):
        super(PrestigeMilestoneAchivedView, self)._onLoading()
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_reward_screen_general()))
        self.__vehicle = self.__itemsCache.items.getItemByCD(vehCD)
        self.__level = level
        self.__bonus = self.__getBonus()
        with self.viewModel.transaction() as vm:
            self.__fillReward(vm)
            self.__fillVehicleInfo(vm)

    def _finalize(self):
        self.__vehicle = None
        self.__tooltipItems.clear()
        self.__tooltipItems = None
        super(PrestigeMilestoneAchivedView, self)._finalize()
        return

    def __getBonus(self):
        return getPrestigeBonus(getMilestones(self.__vehicle.compactDescr), PrestigeBonusContext(self.__vehicle.compactDescr, self.__level, RewardStatus.AVAILABLE))

    def __fillReward(self, viewModel):
        rewardArray = viewModel.getRewards()
        rewardArray.clear()
        packBonusModelAndTooltipData([self.__bonus], rewardArray, self.__tooltipItems, packer=getVehSkillTreeRewardViewBonusPacker())

    def __fillVehicleInfo(self, viewModel):
        model = viewModel.vehicleInfo
        model.setType(self.__vehicle.type)
        model.setName(self.__vehicle.userName)
        model.setIsPremium(self.__vehicle.isElite)
        model.setPrestigeLevel(self.__level)
        model.setLevel(self.__vehicle.level)
        model.setIsBroken(self.__vehicle.isBroken)

    def __onRewardPreview(self):
        if self.__vehicle is None or self.__level is None:
            return
        elif not self.__bonus:
            return
        else:
            customizations = self.__bonus.getCustomizations()
            if not customizations:
                return
            itemTypeID = getItemTypeID(customizations[0].get('custType'))
            if itemTypeID is None:
                return
            if itemTypeID == GUI_ITEM_TYPE.STYLE:
                tabId = CustomizationTabs.STYLES_2D
            elif itemTypeID == GUI_ITEM_TYPE.ATTACHMENT:
                tabId = CustomizationTabs.ATTACHMENTS
            else:
                tabId = None
            self.__customizationService.showCustomization(vehInvID=self.__vehicle.invID, tabId=tabId)
            self.destroyWindow()
            return


class PrestigeMilestoneAchivedWindow(LobbyNotificationWindow):

    def __init__(self, vehCD, level, parent=None):
        super(PrestigeMilestoneAchivedWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PrestigeMilestoneAchivedView(R.views.mono.lobby.veh_skill_tree.reward_screen(), vehCD, level), parent=parent, layer=WindowLayer.TOP_WINDOW)
