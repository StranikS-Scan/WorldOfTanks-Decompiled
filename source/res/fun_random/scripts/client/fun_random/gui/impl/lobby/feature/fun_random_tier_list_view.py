# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_tier_list_view.py
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from fun_random.gui.feature.fun_sounds import FUN_TIER_LIST_SOUND_SPACE
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher, FunAssetPacksMixin
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_tier_list_view_model import FunRandomTierListViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import RARITY_ORDER, getFunRandomBonusPacker
from fun_random.gui.impl.lobby.common.lootboxes import FEP_CATEGORY, packLootboxes
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency, server_settings
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache

class FunRandomTierListView(ViewImpl, FunProgressionWatcher, FunAssetPacksMixin, LobbyHeaderVisibility):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltips',)
    _COMMON_SOUND_SPACE = FUN_TIER_LIST_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = FunRandomTierListViewModel()
        self.__tooltips = {}
        super(FunRandomTierListView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FunRandomTierListView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FunRandomTierListView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        tc = R.views.lobby.awards.tooltips.RewardCompensationTooltip()
        if event.contentID == tc:
            if tooltipId in self.__tooltips:
                tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
                 'labelBefore': event.getArgument('labelBefore', ''),
                 'iconAfter': event.getArgument('iconAfter', ''),
                 'labelAfter': event.getArgument('labelAfter', ''),
                 'bonusName': event.getArgument('bonusName', ''),
                 'countBefore': event.getArgument('countBefore', 1),
                 'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
                tooltipData.update(self.__tooltips[tooltipId].specialArgs)
                settings = ViewSettings(tc, model=LootBoxVehicleCompensationTooltipModel(), kwargs=tooltipData)
                return VehicleCompensationTooltipContent(settings)
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(FunRandomTierListView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _initialize(self, *args, **kwargs):
        super(FunRandomTierListView, self)._initialize(*args, **kwargs)
        self.suspendLobbyHeader(self.uniqueID)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def _finalize(self):
        self.__tooltips.clear()
        self.resumeLobbyHeader(self.uniqueID)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        super(FunRandomTierListView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.showActiveProgressionPage),)

    @server_settings.serverSettingsChangeListener(Configs.LOOTBOXES_TOOLTIP_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__update()

    def __update(self):
        boxes = [ lb for lb in self.__itemsCache.items.tokens.getLootBoxes().values() if lb.getCategory() == FEP_CATEGORY ]
        lbConfig = self.__lobbyContext.getServerSettings().getLootBoxesTooltipConfig()
        with self.viewModel.transaction() as model:
            sortedBoxes = []
            model.setAssetsPointer(self.getModeAssetsPointer())
            for rarity in reversed(RARITY_ORDER):
                sortedBoxes.extend([ b for b in boxes if b.getType().split('_')[-1] == rarity.value ])

            packLootboxes(sortedBoxes, lbConfig, model.getLootBoxes(), getFunRandomBonusPacker(), self.getActiveProgression().config.visibleLBAwardsNames, self.getModeLocalsResRoot(), self.__tooltips)


class FunRandomTierListViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(FunRandomTierListViewWindow, self).__init__(WindowFlags.WINDOW, content=FunRandomTierListView(R.views.fun_random.lobby.feature.FunRandomTierListView()), parent=parent)
