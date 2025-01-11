# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/gift_machine/ny_gift_machine_loot_list_view.py
import logging
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import getNYRanndomsBonusPacker
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.ny_gift_machine_loot_list_view_model import NyGiftMachineLootListViewModel, RewardGroupModel
from gui.impl.lobby.new_year.tooltips.ny_sack_random_reward_tooltip import NySackRandomRewardTooltip
from gui.impl.new_year.loot_box_helper import LootBoxHelper
from gui.impl.new_year.new_year_helper import backportTooltipDecorator, ADDITIONAL_BONUS_NAME_GETTERS
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.new_year import IGiftMachineController
from shared_utils import first
from gui.shared.money import Currency
_logger = logging.getLogger(__name__)

def __getAdditionalNameItems(bonus):
    item, _ = first(bonus.getItems().iteritems())
    return item.descriptor.name if item is not None else bonus.getName()


_BONUS_NAME_GETTERS = {'items': __getAdditionalNameItems}
_BONUS_NAME_GETTERS.update(ADDITIONAL_BONUS_NAME_GETTERS)
_BONUSES_ORDER = ('modernizedExtraHealthReserveAntifragmentationLining1',
 'modernizedTurbochargerRotationMechanism1',
 'modernizedAimDrivesAimingStabilizer1',
 Currency.EQUIP_COIN,
 Currency.FREE_XP,
 Currency.CREDITS,
 'booster_credits',
 'booster_xp',
 'randomNyBooklet',
 'randomNyInstruction',
 'randomNyCrewInstruction',
 'goodies',
 'largeRepairkit',
 'largeMedkit',
 'autoExtinguishers')

def _getBonusName(bonus):
    bonusName = bonus.getName()
    getAdditionalName = _BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return bonusName


def _bonusesSortOrder(bonusName):
    return _BONUSES_ORDER.index(bonusName) if bonusName in _BONUSES_ORDER else len(_BONUSES_ORDER)


def _bonusesOrderCmp(bonus1, bonus2):
    bonusName1 = _getBonusName(bonus1)
    bonusName2 = _getBonusName(bonus2)
    return cmp(bonus2.getValue(), bonus1.getValue()) if bonusName1 == bonusName2 else cmp(_bonusesSortOrder(bonusName1), _bonusesSortOrder(bonusName2))


class NyGiftMachineLootListView(ViewImpl):
    __nyGiftMachineCtrl = dependency.descriptor(IGiftMachineController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = NyGiftMachineLootListViewModel()
        super(NyGiftMachineLootListView, self).__init__(settings)
        self._tooltips = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyGiftMachineLootListView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return NySackRandomRewardTooltip(event.getArgument('resourceType')) if contentID == R.views.lobby.new_year.tooltips.NySackRandomRewardTooltip() else super(NyGiftMachineLootListView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        events = super(NyGiftMachineLootListView, self)._getEvents()
        return events + ((self.__nyGiftMachineCtrl.onLootListInfoUpdated, self.__update),)

    def _onLoading(self, *args, **kwargs):
        super(NyGiftMachineLootListView, self)._onLoading(*args, **kwargs)
        self.__update()
        self.__nyGiftMachineCtrl.onLootListInfoWindowStateChanged(True)

    def _finalize(self):
        super(NyGiftMachineLootListView, self)._finalize()
        self.__nyGiftMachineCtrl.onLootListInfoWindowStateChanged(False)

    def __update(self):
        lootListInfo = self.__nyGiftMachineCtrl.getLootListInfo().copy()
        if not lootListInfo:
            _logger.warning('lootListInfo empty')
            self.destroyWindow()
        groupsWithBonuses = LootBoxHelper.getLootBoxBonuses(lootListInfo, convertToNyRandom=True)
        groupsWithBonuses.sort(key=lambda group: -group.probability)
        with self.viewModel.transaction() as tx:
            self._tooltips.clear()
            rewardGrpoups = tx.getRewardGroups()
            rewardGrpoups.clear()
            for group in groupsWithBonuses:
                bonuses = group.bonuses[:]
                bonuses.sort(cmp=_bonusesOrderCmp)
                groupModel = RewardGroupModel()
                groupModel.setProbabilities(int(round(group.probability * 100)))
                packBonusModelAndTooltipData(bonuses, groupModel.getRewards(), getNYRanndomsBonusPacker(), self._tooltips)
                rewardGrpoups.addViewModel(groupModel)

            rewardGrpoups.invalidate()


class NyGiftMachineLootListWindow(LobbyWindow):

    def __init__(self):
        super(NyGiftMachineLootListWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NyGiftMachineLootListView(R.views.lobby.new_year.NyGiftMachineLootListView()), layer=WindowLayer.OVERLAY)
