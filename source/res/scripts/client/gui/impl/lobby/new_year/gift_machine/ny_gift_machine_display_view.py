# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_machine/ny_gift_machine_display_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_display_view_model import NyGiftMachineDisplayViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_view_model import MachineState
from gui.impl.lobby.new_year.gift_machine import getRentDaysLeftByExpiryTime, getVehicleRewardSpecialArg
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.impl.pub import ViewImpl
from gui.shared.utils.functions import stripHTMLTags
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class NyGiftMachineDisplayView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.GiftMachineDisplayView())
        settings.model = NyGiftMachineDisplayViewModel()
        settings.flags = ViewFlags.TEXTURE_VIEW
        settings.textureName = 'content/Hangars/h30_newyear_2021/environment/h30_NY23_006_Machine_Screen_AM.dds'
        self.__state = None
        super(NyGiftMachineDisplayView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def updateState(self, state):
        if self.__state == state:
            return
        self.__state = state
        with self.viewModel.transaction() as model:
            model.setMachineState(state.value)

    def updateTokens(self, tokensCount):
        self.viewModel.setTokenCount(tokensCount)

    def fillReward(self, isVehicle, reward):
        if reward:
            if isVehicle:
                self.__fillVehicleReward(reward)
            else:
                self.__fillSimpleReward(reward)

    def _onLoading(self, *args, **kwargs):
        super(NyGiftMachineDisplayView, self)._onLoading(*args, **kwargs)
        self.updateState(MachineState.IDLE)

    def __fillVehicleReward(self, reward):
        vehIntCD = getVehicleRewardSpecialArg(reward, 0)
        vehicle = self.__itemsCache.items.getItemByCD(vehIntCD)
        with self.viewModel.transaction() as model:
            rewardModel = model.reward
            rewardModel.setRentBattles(getVehicleRewardSpecialArg(reward, 3, 0))
            rewardModel.setRentDays(getRentDaysLeftByExpiryTime(getVehicleRewardSpecialArg(reward, 2, 0)))
            rewardModel.setName(reward.get('bonusName', ''))
            rewardModel.setUserName(getNationLessName(vehicle.name))
            rewardModel.setValue('')
            vehicleInfo = rewardModel.vehicleInfo
            vehicleInfo.setVehicleName(vehicle.userName)
            vehicleInfo.setVehicleType(vehicle.type)
            vehicleInfo.setVehicleLvl(vehicle.level)
            vehicleInfo.setIsElite(vehicle.isElite)

    def __fillSimpleReward(self, reward):
        with self.viewModel.transaction() as model:
            rewardModel = model.reward
            rewardModel.setName(reward.get('bonusName', ''))
            rewardModel.setIcon(reward.get('imgSource', ''))
            rewardModel.setUserName(reward.get('userName', ''))
            rewardModel.setValue(stripHTMLTags(reward['label']) if reward.get('label') is not None else '')
        return
