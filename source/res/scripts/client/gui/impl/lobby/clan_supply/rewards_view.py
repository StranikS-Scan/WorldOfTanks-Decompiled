# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/clan_supply/rewards_view.py
import typing
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.clan_supply.rewards_view_model import RewardsViewModel, RewardingType
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.clan_supply.bonus_packers import composeBonuses, findVehicle, getClanSupplyBonusPacker, BONUSES_ORDER
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import selectVehicleInHangar
if typing.TYPE_CHECKING:
    from gui.impl.backport import TooltipData
    from gui.server_events.bonuses import SimpleBonus

class RewardsView(ViewImpl):
    __slots__ = ('__tooltips', '__vehicleCD')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.clan_supply.RewardsView(), flags=ViewFlags.VIEW, model=RewardsViewModel(), args=args, kwargs=kwargs)
        self.__tooltips = {}
        self.__vehicleCD = None
        super(RewardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(RewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        if event.contentID == R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent():
            if tooltipId in self.__tooltips:
                tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
                 'labelBefore': event.getArgument('labelBefore', ''),
                 'iconAfter': event.getArgument('iconAfter', ''),
                 'labelAfter': event.getArgument('labelAfter', ''),
                 'bonusName': event.getArgument('bonusName', ''),
                 'countBefore': event.getArgument('countBefore', 1),
                 'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
                tooltipData.update(self.__tooltips[tooltipId].specialArgs)
                settings = ViewSettings(R.views.common.tooltip_window.loot_box_compensation_tooltip.LootBoxVehicleCompensationTooltipContent())
                settings.flags = ViewFlags.VIEW
                settings.model = LootBoxVehicleCompensationTooltipModel()
                settings.kwargs = tooltipData
                return VehicleCompensationTooltipContent(settings)
        return super(RewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _getEvents(self):
        return super(RewardsView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose), (self.viewModel.onGoToHangar, self.__onGoToHangar))

    def _onLoading(self, isElite, rewards, *args, **kwargs):
        super(RewardsView, self)._onLoading(*args, **kwargs)
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_reward_screen_general()))
        self.__vehicleCD = findVehicle(rewards)
        with self.viewModel.transaction() as tx:
            bonusAllocator = None
            if isElite and self.__vehicleCD is not None:
                bonusAllocator = self.__mainVehicleBonusAllocator
                tx.setType(RewardingType.ELITE_WITH_VEHICLE)
            elif isElite:
                tx.setType(RewardingType.ELITE)
            else:
                tx.setType(RewardingType.COMMON)
            self.__tooltips.clear()
            bonuses = composeBonuses(rewards, bonusesOrder=BONUSES_ORDER)
            if bonusAllocator is not None:
                mainBonuses, additionalBonuses = bonusAllocator(bonuses)
            else:
                mainBonuses, additionalBonuses = bonuses, []
            rewardsModel = tx.getRewards()
            packBonusModelAndTooltipData(mainBonuses, rewardsModel, self.__tooltips, packer=getClanSupplyBonusPacker())
            rewardsModel.invalidate()
            if additionalBonuses:
                additionalRewardsModel = tx.getAdditionalRewards()
                packBonusModelAndTooltipData(additionalBonuses, additionalRewardsModel, self.__tooltips, packer=getClanSupplyBonusPacker())
                additionalRewardsModel.invalidate()
        return

    def __onClose(self):
        self.destroyWindow()

    def __onGoToHangar(self):
        if self.__vehicleCD is None:
            return
        else:
            selectVehicleInHangar(self.__vehicleCD)
            self.destroyWindow()
            return

    @staticmethod
    def __mainVehicleBonusAllocator(bonuses):
        mainBonuses = []
        additionalBonuses = []
        for b in bonuses:
            bonusName = b.getName()
            if bonusName in ('vehicles',):
                mainBonuses.append(b)
            if bonusName in ('customizations',):
                additionalBonuses.append(b)

        return (mainBonuses, additionalBonuses)


class RewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, isElite, rewards, parent=None):
        super(RewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RewardsView(isElite, rewards), parent=parent)
