# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dragon_boat/dragon_boat_award_view.py
import WWISE
from account_helpers.settings_core.settings_constants import DragonBoatStorageKeys
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.game_control.dragon_boat_controller import DBOAT_FINAL_REWARD
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dragon_boat.rewards_screen_model import RewardsScreenModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import VehiclesBonus
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.server_events import IEventsCache
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class DragonBoatFinalRewardView(ViewImpl):
    __slots__ = ('__closeCallback', '__vehicle', '__tooltipItems')
    __eventsCache = dependency.descriptor(IEventsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self, closeCallback=None):
        settings = ViewSettings(R.views.lobby.dragon_boats.FinalRewardScreen())
        settings.flags = ViewFlags.VIEW
        settings.model = RewardsScreenModel()
        self.__closeCallback = closeCallback
        self.__vehicle = None
        self.__tooltipItems = {}
        super(DragonBoatFinalRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(DragonBoatFinalRewardView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.viewModel.onClose += self.__onClose

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.__vehicle = None
        self.__tooltipItems.clear()
        return

    def _onLoading(self, *args, **kwargs):
        super(DragonBoatFinalRewardView, self)._onLoading(*args, **kwargs)
        WWISE.WW_eventGlobal(backport.sound(R.sounds.ev_cn_dragonboat_reward()))
        self.__setAwards()
        if self.__settingsCore.isReady and self.__settingsCache.isSynced():
            self.__settingsCore.serverSettings.saveInDragonBoatStorage({DragonBoatStorageKeys.DBOAT_FINAL_REWARD_OBTAINED: True})

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(DragonBoatFinalRewardView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def __onClose(self):
        self.destroyWindow()
        if self.__closeCallback is not None:
            self.__closeCallback()
        return

    def __setAwards(self):
        quests = self.__eventsCache.getHiddenQuests()
        finalTokenQuest = quests.get(DBOAT_FINAL_REWARD)
        bonuses = finalTokenQuest.getBonuses() if finalTokenQuest else []
        mainReward = next((reward for reward in bonuses if isinstance(reward, VehiclesBonus)), None)
        addReward = [ reward for reward in bonuses if not isinstance(reward, VehiclesBonus) and reward.getValue() ]
        self.__vehicle = mainReward.getVehicles()
        if self.__vehicle:
            vehicle, _ = self.__vehicle[0]
            self.__setVehicleData(vehicle)
        with self.viewModel.transaction() as tx:
            mainBonusesModel = tx.getMainRewards()
            addBonusesModel = tx.getAdditionalRewards()
            packBonusModelAndTooltipData([mainReward], mainBonusesModel, tooltipData=self.__tooltipItems)
            packBonusModelAndTooltipData(addReward, addBonusesModel, tooltipData=self.__tooltipItems)
        return

    def __setVehicleData(self, vehicle):
        with self.viewModel.transaction() as model:
            model.vehicleInfo.setVehicleName(vehicle.shortUserName)
            model.vehicleInfo.setVehicleType(vehicle.type)
            model.vehicleInfo.setVehicleLvl(vehicle.level)
            model.vehicleInfo.setIsElite(vehicle.isElite)


class DragonBoatFinalRewardWindow(LobbyWindow):

    def __init__(self, parent=None, closeCallback=None):
        super(DragonBoatFinalRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=DragonBoatFinalRewardView(closeCallback), parent=parent)
