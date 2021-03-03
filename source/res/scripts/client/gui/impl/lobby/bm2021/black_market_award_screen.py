# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/black_market_award_screen.py
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.lobby.bm2021.additional_rewards import ADDITIONAL_REWARDS
from gui.impl.lobby.bm2021.sound import BLACK_MARKET_AWARD_SOUND_SPACE
from gui.impl.lobby.loot_box.loot_box_helper import setVehicleDataToModel
from gui.impl.gen.view_models.views.lobby.bm2021.black_market_award_screen_model import BlackMarketAwardScreenModel
from gui.impl.gen.view_models.views.lobby.bm2021.reward_item_model import RewardItemModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES
from gui.shared.utils.functions import getImageResourceFromPath
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache

class BlackMarketAwardScreen(ViewImpl):
    __slots__ = ('__vehCD',)
    _COMMON_SOUND_SPACE = BLACK_MARKET_AWARD_SOUND_SPACE
    __service = dependency.descriptor(ICustomizationService)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, vehCD):
        settings = ViewSettings(layoutID)
        settings.model = BlackMarketAwardScreenModel()
        super(BlackMarketAwardScreen, self).__init__(settings)
        self.__vehCD = vehCD

    @property
    def viewModel(self):
        return super(BlackMarketAwardScreen, self).getViewModel()

    def _finalize(self):
        vehicleData = self.__itemsCache.items.inventory.getItemData(self.__vehCD)
        if vehicleData is not None:
            g_currentVehicle.selectVehicle(vehicleData.invID)
        super(BlackMarketAwardScreen, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            setVehicleDataToModel(self.__vehCD, vm.mainReward)
            additionalRewardsList = vm.getAdditionalRewards()
            for itemType, itemID in ADDITIONAL_REWARDS:
                item = self.__service.getItemByID(itemType, itemID)
                secondaryReward = RewardItemModel()
                secondaryReward.setValue(1)
                secondaryReward.setName(item.userName)
                secondaryReward.setIcon(getImageResourceFromPath(item.getBonusIcon())())
                secondaryReward.setBigIcon(getImageResourceFromPath(item.getBonusIcon('big'))())
                secondaryReward.setTooltipId(TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM)
                secondaryReward.setItemCD(item.intCD)
                secondaryReward.setItemType(GUI_ITEM_TYPE_NAMES[itemType])
                additionalRewardsList.addViewModel(secondaryReward)

            additionalRewardsList.invalidate()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipID = event.getArgument('tooltipId', '')
            tooltipParameters = createTooltipData(isSpecial=True, specialAlias=tooltipID, specialArgs=[int(event.getArgument('itemCD')),
             -1,
             True,
             -1])
            window = BackportTooltipWindow(tooltipParameters, self.getParentWindow())
            window.load()
            return window
        return super(BlackMarketAwardScreen, self).createToolTip(event)


class BlackMarketAwardScreenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, contentResId, vehCD):
        super(BlackMarketAwardScreenWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BlackMarketAwardScreen(contentResId, vehCD))
